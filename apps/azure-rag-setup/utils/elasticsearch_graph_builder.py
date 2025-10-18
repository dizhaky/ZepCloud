"""
Elasticsearch-adapted graph builder for document relationships
"""
import logging
from typing import Dict, List, Any, Optional
from .bulk_indexer import BulkIndexer
from .raganything_processor import RAGAnythingProcessor
from config_elasticsearch import Config

logger = logging.getLogger(__name__)

class ElasticsearchGraphBuilder:
    """Build and manage document relationship graphs in Elasticsearch"""

    def __init__(self, bulk_indexer: BulkIndexer):
        self.bulk_indexer = bulk_indexer
        self.raganything_processor = RAGAnythingProcessor()
        self.relationship_index = f"{Config.ELASTIC_INDEX}-relationships"
        self.stats = {
            "documents_processed": 0,
            "relationships_created": 0,
            "entities_extracted": 0,
            "graph_nodes": 0,
            "graph_edges": 0
        }

    def build_document_graph(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build relationship graph for a set of documents

        Args:
            documents: List of document dictionaries

        Returns:
            Graph statistics and relationships
        """
        logger.info(f"Building graph for {len(documents)} documents")

        # Process documents with RAG-Anything
        enhanced_documents = []
        for doc in documents:
            enhanced_doc = self.raganything_processor.process_document(doc)
            enhanced_documents.append(enhanced_doc)

        # Find document relationships
        document_relationships = self.raganything_processor.find_document_relationships(enhanced_documents)

        # Index relationships in Elasticsearch
        self._index_relationships(document_relationships)

        # Update statistics
        self.stats["documents_processed"] += len(documents)
        self.stats["relationships_created"] += len(document_relationships)
        self.stats["entities_extracted"] += sum(len(doc.get("entities", [])) for doc in enhanced_documents)
        self.stats["graph_nodes"] = len(enhanced_documents)
        self.stats["graph_edges"] = len(document_relationships)

        return {
            "documents_processed": len(documents),
            "relationships_created": len(document_relationships),
            "entities_extracted": self.stats["entities_extracted"],
            "graph_stats": self.stats
        }

    def _index_relationships(self, relationships: List[Dict[str, Any]]):
        """Index document relationships in Elasticsearch"""
        for relationship in relationships:
            try:
                self.bulk_indexer.index_relationship(
                    relationship["source_doc_id"],
                    relationship["target_doc_id"],
                    relationship["relationship_type"],
                    relationship["strength"],
                    relationship.get("shared_entities", []),
                    relationship.get("shared_topics", [])
                )
            except Exception as e:
                logger.error(f"Failed to index relationship: {e}")

    def get_document_relationships(self, doc_id: str) -> List[Dict[str, Any]]:
        """Get relationships for a specific document"""
        try:
            # Query the relationships index
            query = {
                "query": {
                    "bool": {
                        "should": [
                            {"term": {"source_doc_id": doc_id}},
                            {"term": {"target_doc_id": doc_id}}
                        ]
                    }
                }
            }

            response = self.bulk_indexer.es.search(
                index=self.relationship_index,
                body=query
            )

            relationships = []
            for hit in response["hits"]["hits"]:
                relationships.append(hit["_source"])

            return relationships

        except Exception as e:
            logger.error(f"Failed to get document relationships: {e}")
            return []

    def get_graph_statistics(self) -> Dict[str, Any]:
        """Get graph statistics"""
        try:
            # Get relationship count
            relationship_count = self.bulk_indexer.es.count(index=self.relationship_index)

            # Get entity statistics from main index
            entity_agg = {
                "size": 0,
                "aggs": {
                    "entity_types": {
                        "nested": {"path": "entities"},
                        "aggs": {
                            "entity_type_count": {
                                "terms": {"field": "entities.type"}
                            }
                        }
                    }
                }
            }

            entity_response = self.bulk_indexer.es.search(
                index=Config.ELASTIC_INDEX,
                body=entity_agg
            )

            return {
                "total_relationships": relationship_count["count"],
                "total_documents": self.stats["documents_processed"],
                "total_entities": self.stats["entities_extracted"],
                "entity_types": entity_response.get("aggregations", {}).get("entity_types", {}).get("entity_type_count", {}).get("buckets", []),
                "graph_density": self._calculate_graph_density()
            }

        except Exception as e:
            logger.error(f"Failed to get graph statistics: {e}")
            return {}

    def _calculate_graph_density(self) -> float:
        """Calculate graph density"""
        if self.stats["graph_nodes"] <= 1:
            return 0.0

        max_edges = self.stats["graph_nodes"] * (self.stats["graph_nodes"] - 1) / 2
        return self.stats["graph_edges"] / max_edges if max_edges > 0 else 0.0

    def find_similar_documents(self, doc_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Find documents similar to the given document"""
        try:
            # Get the source document
            source_doc = self.bulk_indexer.es.get(
                index=Config.ELASTIC_INDEX,
                id=doc_id
            )

            source_entities = set(entity["value"] for entity in source_doc["_source"].get("entities", []))
            source_topics = set(source_doc["_source"].get("topics", []))

            # Find documents with similar entities and topics
            query = {
                "query": {
                    "bool": {
                        "must_not": [{"term": {"_id": doc_id}}],
                        "should": [
                            {"terms": {"entities.value": list(source_entities)}},
                            {"terms": {"topics": list(source_topics)}}
                        ]
                    }
                },
                "size": limit,
                "_source": ["title", "content", "entities", "topics", "source_type"]
            }

            response = self.bulk_indexer.es.search(
                index=Config.ELASTIC_INDEX,
                body=query
            )

            similar_docs = []
            for hit in response["hits"]["hits"]:
                doc = hit["_source"]
                doc["similarity_score"] = hit.get("_score", 0)
                doc["doc_id"] = hit["_id"]
                similar_docs.append(doc)

            return similar_docs

        except Exception as e:
            logger.error(f"Failed to find similar documents: {e}")
            return []

    def get_entity_network(self, entity_value: str, depth: int = 2) -> Dict[str, Any]:
        """Get network of entities connected to the given entity"""
        try:
            # Find documents containing this entity
            query = {
                "query": {
                    "nested": {
                        "path": "entities",
                        "query": {
                            "term": {"entities.value": entity_value}
                        }
                    }
                },
                "size": 100
            }

            response = self.bulk_indexer.es.search(
                index=Config.ELASTIC_INDEX,
                body=query
            )

            # Extract all entities from these documents
            all_entities = set()
            for hit in response["hits"]["hits"]:
                entities = hit["_source"].get("entities", [])
                for entity in entities:
                    all_entities.add(entity["value"])

            # Find co-occurrence relationships
            co_occurrences = {}
            for entity in all_entities:
                if entity != entity_value:
                    co_occurrences[entity] = self._calculate_entity_co_occurrence(entity_value, entity)

            return {
                "entity": entity_value,
                "connected_entities": list(all_entities),
                "co_occurrences": co_occurrences,
                "network_size": len(all_entities)
            }

        except Exception as e:
            logger.error(f"Failed to get entity network: {e}")
            return {}

    def _calculate_entity_co_occurrence(self, entity1: str, entity2: str) -> float:
        """Calculate co-occurrence strength between two entities"""
        try:
            # Find documents containing both entities
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "nested": {
                                    "path": "entities",
                                    "query": {"term": {"entities.value": entity1}}
                                }
                            },
                            {
                                "nested": {
                                    "path": "entities",
                                    "query": {"term": {"entities.value": entity2}}
                                }
                            }
                        ]
                    }
                },
                "size": 0
            }

            response = self.bulk_indexer.es.search(
                index=Config.ELASTIC_INDEX,
                body=query
            )

            co_occurrence_count = response["hits"]["total"]["value"]

            # Calculate individual entity frequencies
            entity1_count = self._get_entity_frequency(entity1)
            entity2_count = self._get_entity_frequency(entity2)

            # Calculate co-occurrence strength
            if entity1_count > 0 and entity2_count > 0:
                strength = co_occurrence_count / min(entity1_count, entity2_count)
                return min(strength, 1.0)

            return 0.0

        except Exception as e:
            logger.error(f"Failed to calculate entity co-occurrence: {e}")
            return 0.0

    def _get_entity_frequency(self, entity_value: str) -> int:
        """Get frequency of an entity across all documents"""
        try:
            query = {
                "query": {
                    "nested": {
                        "path": "entities",
                        "query": {"term": {"entities.value": entity_value}}
                    }
                },
                "size": 0
            }

            response = self.bulk_indexer.es.search(
                index=Config.ELASTIC_INDEX,
                body=query
            )

            return response["hits"]["total"]["value"]

        except Exception as e:
            logger.error(f"Failed to get entity frequency: {e}")
            return 0
