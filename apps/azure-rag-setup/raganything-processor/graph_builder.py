#!/usr/bin/env python3
"""
Document Relationship Graph Builder
Extracts and builds relationships between documents based on:
- Entity co-occurrence (people, orgs, locations)
- Citations and references
- Topic similarity
- Shared metadata
"""

import os
import re
import json
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict
from datetime import datetime
import hashlib

class GraphBuilder:
    """Build document relationship graphs for enhanced RAG"""

    def __init__(self):
        self.documents = {}
        self.entity_index = defaultdict(set)  # entity -> set of doc_ids
        self.topic_index = defaultdict(set)  # topic -> set of doc_ids
        self.citation_graph = defaultdict(set)  # doc_id -> set of cited doc_ids
        self.similarity_threshold = 0.3

    def add_document(
        self,
        doc_id: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add a document and extract its relationships

        Args:
            doc_id: Unique document identifier
            content: Full document text
            metadata: Document metadata (entities, topics, etc.)

        Returns:
            Document relationship data
        """
        # Store document
        self.documents[doc_id] = {
            'id': doc_id,
            'content': content,
            'metadata': metadata,
            'added_at': datetime.now().isoformat()
        }

        # Extract and index entities
        entities = self._extract_entities(content, metadata)
        for entity_type, entity_values in entities.items():
            for entity in entity_values:
                self.entity_index[f"{entity_type}:{entity}"].add(doc_id)

        # Extract and index topics/key phrases
        topics = self._extract_topics(content, metadata)
        for topic in topics:
            self.topic_index[topic].add(doc_id)

        # Extract citations/references
        citations = self._extract_citations(content, metadata)
        if citations:
            self.citation_graph[doc_id].update(citations)

        # Build relationships
        relationships = self._build_relationships(doc_id, entities, topics, citations)

        return relationships

    def _extract_entities(
        self,
        content: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Set[str]]:
        """Extract entities from content and metadata"""
        entities = {
            'people': set(),
            'organizations': set(),
            'locations': set(),
            'emails': set(),
            'urls': set()
        }

        # Get from metadata (Azure AI enrichment)
        if 'people' in metadata and metadata['people']:
            entities['people'].update(metadata['people'])
        if 'organizations' in metadata and metadata['organizations']:
            entities['organizations'].update(metadata['organizations'])
        if 'locations' in metadata and metadata['locations']:
            entities['locations'].update(metadata['locations'])
        if 'emails' in metadata and metadata['emails']:
            entities['emails'].update(metadata['emails'])
        if 'urls' in metadata and metadata['urls']:
            entities['urls'].update(metadata['urls'])

        # Extract from content using regex (backup/supplement)
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        entities['emails'].update(re.findall(email_pattern, content))

        # URL pattern
        url_pattern = r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)'
        entities['urls'].update(re.findall(url_pattern, content))

        return entities

    def _extract_topics(
        self,
        content: str,
        metadata: Dict[str, Any]
    ) -> Set[str]:
        """Extract topics/key phrases"""
        topics = set()

        # Get from metadata (Azure AI enrichment)
        if 'keyPhrases' in metadata and metadata['keyPhrases']:
            topics.update(metadata['keyPhrases'])

        # Could add custom topic extraction here if needed

        return topics

    def _extract_citations(
        self,
        content: str,
        metadata: Dict[str, Any]
    ) -> Set[str]:
        """Extract document citations and references"""
        citations = set()

        # Common citation patterns
        patterns = [
            r'see\s+(?:document|file|report|memo)[\s:]+([A-Za-z0-9_\-\.]+)',
            r'(?:ref|reference)[\s:]+([A-Za-z0-9_\-\.]+)',
            r'as\s+(?:mentioned|described|noted)\s+in\s+([A-Za-z0-9_\-\.]+)',
            r'\[([A-Za-z0-9_\-\.]+)\]',  # Bracketed references
            r'(?:attachment|annex|appendix)[\s:]+([A-Za-z0-9_\-\.]+)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            citations.update(matches)

        # Get from metadata if available
        if 'references' in metadata and metadata['references']:
            citations.update(metadata['references'])

        return citations

    def _build_relationships(
        self,
        doc_id: str,
        entities: Dict[str, Set[str]],
        topics: Set[str],
        citations: Set[str]
    ) -> Dict[str, Any]:
        """Build comprehensive relationship data for a document"""
        relationships = {
            'doc_id': doc_id,
            'relationships': {
                'cites': list(citations),
                'cited_by': [],  # Will be computed later
                'shares_entities': {},
                'similar_topics': [],
                'related_by_email': [],
                'related_by_url': []
            },
            'entity_connections': {},
            'topic_connections': {},
            'relationship_score': 0.0
        }

        # Find documents sharing entities
        for entity_type, entity_values in entities.items():
            for entity in entity_values:
                entity_key = f"{entity_type}:{entity}"
                related_docs = self.entity_index[entity_key] - {doc_id}

                if related_docs:
                    if entity_type not in relationships['entity_connections']:
                        relationships['entity_connections'][entity_type] = {}
                    relationships['entity_connections'][entity_type][entity] = list(related_docs)

                    # Group by specific entity types for easy access
                    if entity_type == 'emails':
                        relationships['relationships']['related_by_email'].extend(related_docs)
                    elif entity_type == 'urls':
                        relationships['relationships']['related_by_url'].extend(related_docs)
                    else:
                        if entity not in relationships['relationships']['shares_entities']:
                            relationships['relationships']['shares_entities'][entity] = []
                        relationships['relationships']['shares_entities'][entity].extend(related_docs)

        # Find documents with similar topics
        for topic in topics:
            related_docs = self.topic_index[topic] - {doc_id}
            if related_docs:
                relationships['topic_connections'][topic] = list(related_docs)
                relationships['relationships']['similar_topics'].extend(related_docs)

        # Remove duplicates
        relationships['relationships']['similar_topics'] = list(set(relationships['relationships']['similar_topics']))
        relationships['relationships']['related_by_email'] = list(set(relationships['relationships']['related_by_email']))
        relationships['relationships']['related_by_url'] = list(set(relationships['relationships']['related_by_url']))

        # Calculate relationship score (how connected this document is)
        relationships['relationship_score'] = self._calculate_relationship_score(relationships)

        # Update reverse citations
        self._update_reverse_citations(doc_id, citations)

        return relationships

    def _calculate_relationship_score(self, relationships: Dict[str, Any]) -> float:
        """Calculate a score indicating how well-connected a document is"""
        score = 0.0

        # Citations (both directions)
        score += len(relationships['relationships']['cites']) * 2.0
        score += len(relationships['relationships']['cited_by']) * 2.0

        # Entity connections
        score += len(relationships['relationships']['shares_entities']) * 1.5

        # Topic similarity
        score += len(relationships['relationships']['similar_topics']) * 1.0

        # Email/URL connections
        score += len(relationships['relationships']['related_by_email']) * 1.0
        score += len(relationships['relationships']['related_by_url']) * 0.5

        return score

    def _update_reverse_citations(self, citing_doc: str, cited_docs: Set[str]):
        """Update the cited_by relationships for cited documents"""
        # This would need to be done in a second pass or maintained separately
        pass

    def get_document_relationships(self, doc_id: str) -> Dict[str, Any]:
        """Get relationship data for a specific document"""
        if doc_id not in self.documents:
            return None

        doc = self.documents[doc_id]
        return doc.get('relationships', {})

    def find_related_documents(
        self,
        doc_id: str,
        relationship_types: List[str] = None,
        min_score: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Find documents related to the given document

        Args:
            doc_id: Source document ID
            relationship_types: Types of relationships to consider
                              (e.g., ['cites', 'shares_entities', 'similar_topics'])
            min_score: Minimum relationship score threshold

        Returns:
            List of related documents with their relationship data
        """
        if doc_id not in self.documents:
            return []

        related_docs = defaultdict(list)
        doc = self.documents[doc_id]
        relationships = doc.get('relationships', {}).get('relationships', {})

        if not relationship_types:
            relationship_types = relationships.keys()

        # Collect related documents by type
        for rel_type in relationship_types:
            if rel_type in relationships:
                if isinstance(relationships[rel_type], list):
                    for related_id in relationships[rel_type]:
                        related_docs[related_id].append(rel_type)
                elif isinstance(relationships[rel_type], dict):
                    for entity, doc_list in relationships[rel_type].items():
                        for related_id in doc_list:
                            related_docs[related_id].append(f"{rel_type}:{entity}")

        # Format results
        results = []
        for related_id, rel_types in related_docs.items():
            if related_id in self.documents:
                rel_doc = self.documents[related_id]
                score = rel_doc.get('relationships', {}).get('relationship_score', 0.0)

                if score >= min_score:
                    results.append({
                        'doc_id': related_id,
                        'relationship_types': rel_types,
                        'relationship_score': score,
                        'metadata': rel_doc.get('metadata', {})
                    })

        # Sort by relationship score
        results.sort(key=lambda x: x['relationship_score'], reverse=True)

        return results

    def export_graph(self, output_file: str):
        """Export the relationship graph to JSON"""
        graph_data = {
            'documents': self.documents,
            'entity_index': {k: list(v) for k, v in self.entity_index.items()},
            'topic_index': {k: list(v) for k, v in self.topic_index.items()},
            'citation_graph': {k: list(v) for k, v in self.citation_graph.items()},
            'stats': {
                'total_documents': len(self.documents),
                'total_entities': len(self.entity_index),
                'total_topics': len(self.topic_index),
                'total_citations': sum(len(v) for v in self.citation_graph.values())
            }
        }

        with open(output_file, 'w') as f:
            json.dump(graph_data, f, indent=2)

        print(f"✅ Graph exported to {output_file}")
        print(f"   Documents: {graph_data['stats']['total_documents']}")
        print(f"   Entities: {graph_data['stats']['total_entities']}")
        print(f"   Topics: {graph_data['stats']['total_topics']}")
        print(f"   Citations: {graph_data['stats']['total_citations']}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics"""
        return {
            'total_documents': len(self.documents),
            'total_entities': len(self.entity_index),
            'total_topics': len(self.topic_index),
            'total_citations': sum(len(v) for v in self.citation_graph.values()),
            'avg_relationships_per_doc': sum(
                doc.get('relationships', {}).get('relationship_score', 0.0)
                for doc in self.documents.values()
            ) / len(self.documents) if self.documents else 0,
            'most_connected_entities': sorted(
                [(k, len(v)) for k, v in self.entity_index.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10],
            'most_common_topics': sorted(
                [(k, len(v)) for k, v in self.topic_index.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }


def main():
    """Test the graph builder"""
    print("="*60)
    print("Document Relationship Graph Builder - Test")
    print("="*60)

    # Create graph builder
    graph = GraphBuilder()

    # Add sample documents
    doc1_metadata = {
        'people': ['Dan Izhaky', 'John Smith'],
        'organizations': ['United Safety Technology'],
        'locations': ['Boston'],
        'keyPhrases': ['safety equipment', 'annual report', 'financial results'],
        'emails': ['dan@ust.com'],
        'urls': ['https://ust.com/reports']
    }

    relationships1 = graph.add_document(
        'doc1.pdf',
        'Annual report for United Safety Technology. Contact Dan Izhaky at dan@ust.com. See attachment financial_2024.pdf',
        doc1_metadata
    )

    print("\nDocument 1 relationships:")
    print(json.dumps(relationships1, indent=2))

    doc2_metadata = {
        'people': ['Dan Izhaky', 'Jane Doe'],
        'organizations': ['United Safety Technology'],
        'keyPhrases': ['safety equipment', 'Q4 results'],
        'emails': ['dan@ust.com', 'jane@ust.com']
    }

    relationships2 = graph.add_document(
        'doc2.pdf',
        'Q4 results summary. Contact Dan Izhaky or Jane Doe.',
        doc2_metadata
    )

    print("\nDocument 2 relationships:")
    print(json.dumps(relationships2, indent=2))

    # Get statistics
    print("\nGraph Statistics:")
    stats = graph.get_statistics()
    print(json.dumps(stats, indent=2))

    # Find related documents
    print("\nRelated documents to doc1.pdf:")
    related = graph.find_related_documents('doc1.pdf')
    print(json.dumps(related, indent=2))

    print("\n✅ Graph builder test complete!")

if __name__ == "__main__":
    main()

