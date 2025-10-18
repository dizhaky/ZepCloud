"""
Query interface for searching Elasticsearch with RAG-Anything enhancements
"""
from elasticsearch import Elasticsearch
from config_elasticsearch import Config
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logging.basicConfig(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)

class M365SearchInterface:
    """Search interface for M365 data in Elasticsearch with RAG-Anything features"""

    def __init__(self):
        self.es = Elasticsearch(
            Config.ELASTIC_HOST,
            basic_auth=(Config.ELASTIC_USERNAME, Config.ELASTIC_PASSWORD)
        )
        self.index_name = Config.ELASTIC_INDEX
        self.relationship_index = f"{Config.ELASTIC_INDEX}-relationships"

    def simple_search(self, query: str, size: int = 10) -> List[Dict[str, Any]]:
        """Basic full-text search with RAG-Anything enhancements"""
        search_query = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": [
                        "title^3",
                        "content^2",
                        "file_name",
                        "subject",
                        "entities.value^2",
                        "key_phrases^1.5"
                    ],
                    "type": "best_fields",
                    "fuzziness": "AUTO"
                }
            },
            "size": size,
            "highlight": {
                "fields": {
                    "content": {"fragment_size": 150, "number_of_fragments": 3},
                    "title": {},
                    "entities.value": {}
                }
            }
        }

        results = self.es.search(index=self.index_name, body=search_query)
        return self.format_results(results)

    def advanced_search(self, query: str, filters: Optional[Dict[str, Any]] = None, size: int = 10) -> List[Dict[str, Any]]:
        """Advanced search with filters and RAG-Anything features"""
        must_clauses = [{
            "multi_match": {
                "query": query,
                "fields": [
                    "title^3",
                    "content^2",
                    "file_name",
                    "subject",
                    "entities.value^2",
                    "key_phrases^1.5"
                ],
                "fuzziness": "AUTO"
            }
        }]

        filter_clauses = []

        if filters:
            if filters.get('source_type'):
                filter_clauses.append({"term": {"source_type": filters['source_type']}})

            if filters.get('file_type'):
                filter_clauses.append({"term": {"file_type": filters['file_type']}})

            if filters.get('site_name'):
                filter_clauses.append({"term": {"site_name": filters['site_name']}})

            if filters.get('date_from'):
                filter_clauses.append({
                    "range": {
                        "modified_date": {
                            "gte": filters['date_from']
                        }
                    }
                })

            if filters.get('date_to'):
                filter_clauses.append({
                    "range": {
                        "modified_date": {
                            "lte": filters['date_to']
                        }
                    }
                })

            if filters.get('created_by'):
                filter_clauses.append({"match": {"created_by": filters['created_by']}})

            if filters.get('entities'):
                filter_clauses.append({
                    "nested": {
                        "path": "entities",
                        "query": {
                            "terms": {"entities.value": filters['entities']}
                        }
                    }
                })

            if filters.get('topics'):
                filter_clauses.append({"terms": {"topics": filters['topics']}})

            if filters.get('complexity_min'):
                filter_clauses.append({
                    "range": {
                        "complexity_score": {
                            "gte": filters['complexity_min']
                        }
                    }
                })

        search_query = {
            "query": {
                "bool": {
                    "must": must_clauses,
                    "filter": filter_clauses
                }
            },
            "size": size,
            "highlight": {
                "fields": {
                    "content": {"fragment_size": 150, "number_of_fragments": 3},
                    "title": {},
                    "entities.value": {}
                }
            },
            "sort": [
                {"_score": {"order": "desc"}},
                {"modified_date": {"order": "desc"}}
            ]
        }

        results = self.es.search(index=self.index_name, body=search_query)
        return self.format_results(results)

    def multimodal_search(self, query: str, content_types: List[str] = None, size: int = 10) -> List[Dict[str, Any]]:
        """Search across multimodal content (tables, equations, images, charts)"""
        if not content_types:
            content_types = ["tables", "equations", "images", "charts"]

        should_clauses = []

        for content_type in content_types:
            should_clauses.append({
                "nested": {
                    "path": f"multimodal_content.{content_type}",
                    "query": {
                        "multi_match": {
                            "query": query,
                            "fields": [
                                f"multimodal_content.{content_type}.content",
                                f"multimodal_content.{content_type}.caption",
                                f"multimodal_content.{content_type}.description"
                            ]
                        }
                    }
                }
            })

        search_query = {
            "query": {
                "bool": {
                    "should": should_clauses,
                    "minimum_should_match": 1
                }
            },
            "size": size,
            "highlight": {
                "fields": {
                    "multimodal_content.*.content": {},
                    "multimodal_content.*.caption": {},
                    "multimodal_content.*.description": {}
                }
            }
        }

        results = self.es.search(index=self.index_name, body=search_query)
        return self.format_results(results)

    def entity_search(self, entity_value: str, entity_type: str = None, size: int = 10) -> List[Dict[str, Any]]:
        """Search for documents containing specific entities"""
        query = {
            "nested": {
                "path": "entities",
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"entities.value": entity_value}}
                        ]
                    }
                }
            }
        }

        if entity_type:
            query["nested"]["query"]["bool"]["must"].append(
                {"term": {"entities.type": entity_type}}
            )

        search_query = {
            "query": query,
            "size": size,
            "highlight": {
                "fields": {
                    "entities.value": {}
                }
            }
        }

        results = self.es.search(index=self.index_name, body=search_query)
        return self.format_results(results)

    def relationship_search(self, doc_id: str, relationship_types: List[str] = None, size: int = 10) -> List[Dict[str, Any]]:
        """Find documents related to a specific document"""
        if not relationship_types:
            relationship_types = ["similarity", "co_occurrence", "citation"]

        # Get relationships from relationship index
        relationship_query = {
            "query": {
                "bool": {
                    "should": [
                        {"term": {"source_doc_id": doc_id}},
                        {"term": {"target_doc_id": doc_id}}
                    ]
                }
            },
            "size": 100
        }

        relationship_results = self.es.search(index=self.relationship_index, body=relationship_query)

        # Get related document IDs
        related_doc_ids = []
        for hit in relationship_results["hits"]["hits"]:
            source_id = hit["_source"]["source_doc_id"]
            target_id = hit["_source"]["target_doc_id"]

            if source_id == doc_id:
                related_doc_ids.append(target_id)
            else:
                related_doc_ids.append(source_id)

        if not related_doc_ids:
            return []

        # Get the actual documents
        docs_query = {
            "query": {
                "terms": {"_id": related_doc_ids}
            },
            "size": size
        }

        results = self.es.search(index=self.index_name, body=docs_query)
        return self.format_results(results)

    def aggregate_by_source(self) -> List[Dict[str, Any]]:
        """Get document counts by source type"""
        search_query = {
            "size": 0,
            "aggs": {
                "by_source": {
                    "terms": {
                        "field": "source_type",
                        "size": 20
                    }
                }
            }
        }

        results = self.es.search(index=self.index_name, body=search_query)
        return results['aggregations']['by_source']['buckets']

    def aggregate_by_site(self) -> List[Dict[str, Any]]:
        """Get document counts by SharePoint site"""
        search_query = {
            "size": 0,
            "aggs": {
                "by_site": {
                    "terms": {
                        "field": "site_name",
                        "size": 50
                    }
                }
            }
        }

        results = self.es.search(index=self.index_name, body=search_query)
        return results['aggregations']['by_site']['buckets']

    def aggregate_by_entity_type(self) -> List[Dict[str, Any]]:
        """Get entity type distribution"""
        search_query = {
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

        results = self.es.search(index=self.index_name, body=search_query)
        return results['aggregations']['entity_types']['entity_type_count']['buckets']

    def get_recent_documents(self, days: int = 7, size: int = 20) -> List[Dict[str, Any]]:
        """Get recently modified documents"""
        search_query = {
            "query": {
                "range": {
                    "modified_date": {
                        "gte": f"now-{days}d/d"
                    }
                }
            },
            "size": size,
            "sort": [
                {"modified_date": {"order": "desc"}}
            ]
        }

        results = self.es.search(index=self.index_name, body=search_query)
        return self.format_results(results)

    def get_enhanced_documents(self, size: int = 20) -> List[Dict[str, Any]]:
        """Get documents with RAG-Anything enhancements"""
        search_query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"raganything_processed": True}}
                    ]
                }
            },
            "size": size,
            "sort": [
                {"complexity_score": {"order": "desc"}},
                {"modified_date": {"order": "desc"}}
            ]
        }

        results = self.es.search(index=self.index_name, body=search_query)
        return self.format_results(results)

    def format_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format search results for display"""
        formatted = []
        for hit in results['hits']['hits']:
            source = hit['_source']
            formatted.append({
                "score": hit.get('_score', 0),
                "title": source.get('title', 'Untitled'),
                "source_type": source.get('source_type', 'unknown'),
                "site_name": source.get('site_name', ''),
                "url": source.get('web_url', ''),
                "modified_date": source.get('modified_date', ''),
                "created_by": source.get('created_by', ''),
                "file_type": source.get('file_type', ''),
                "entities": source.get('entities', []),
                "topics": source.get('topics', []),
                "complexity_score": source.get('complexity_score', 0),
                "raganything_processed": source.get('raganything_processed', False),
                "snippet": hit.get('highlight', {}).get('content', [''])[0] if 'highlight' in hit else source.get('content', '')[:200]
            })

        return formatted

    def get_index_stats(self) -> Dict[str, Any]:
        """Get index statistics including RAG-Anything metrics"""
        stats = self.es.indices.stats(index=self.index_name)

        # Get enhanced document count
        enhanced_query = {
            "query": {"term": {"raganything_processed": True}},
            "size": 0
        }
        enhanced_results = self.es.search(index=self.index_name, body=enhanced_query)

        # Get relationship count
        relationship_count = self.es.count(index=self.relationship_index)

        return {
            "total_documents": stats['indices'][self.index_name]['total']['docs']['count'],
            "total_size": stats['indices'][self.index_name]['total']['store']['size_in_bytes'],
            "total_size_mb": stats['indices'][self.index_name]['total']['store']['size_in_bytes'] / (1024 * 1024),
            "enhanced_documents": enhanced_results['hits']['total']['value'],
            "total_relationships": relationship_count['count'],
            "enhancement_rate": (enhanced_results['hits']['total']['value'] / stats['indices'][self.index_name]['total']['docs']['count'] * 100) if stats['indices'][self.index_name]['total']['docs']['count'] > 0 else 0
        }

def interactive_search():
    """Interactive search CLI"""
    print("="*60)
    print("M365 Elasticsearch Search Interface with RAG-Anything")
    print("="*60)

    search = M365SearchInterface()

    # Show stats
    try:
        stats = search.get_index_stats()
        print(f"Total documents: {stats['total_documents']:,}")
        print(f"Enhanced documents: {stats['enhanced_documents']:,}")
        print(f"Enhancement rate: {stats['enhancement_rate']:.1f}%")
        print(f"Total relationships: {stats['total_relationships']:,}")
        print(f"Index size: {stats['total_size_mb']:.2f} MB")
        print()
    except:
        print("Could not retrieve index stats")
        print()

    while True:
        print("\nOptions:")
        print("1. Simple search")
        print("2. Advanced search (with filters)")
        print("3. Multimodal search")
        print("4. Entity search")
        print("5. Relationship search")
        print("6. Show statistics")
        print("7. Recent documents")
        print("8. Enhanced documents")
        print("9. Exit")

        choice = input("\nSelect option (1-9): ").strip()

        if choice == '1':
            query = input("Enter search query: ").strip()
            if query:
                results = search.simple_search(query)
                print(f"\nFound {len(results)} results:\n")
                for i, r in enumerate(results, 1):
                    print(f"{i}. {r['title']} ({r['source_type']})")
                    print(f"   Score: {r['score']:.2f} | Enhanced: {r['raganything_processed']}")
                    print(f"   Entities: {len(r['entities'])} | Topics: {r['topics']}")
                    print(f"   {r['snippet'][:150]}...")
                    if r['url']:
                        print(f"   URL: {r['url']}")
                    print()

        elif choice == '2':
            query = input("Enter search query: ").strip()
            source_type = input("Filter by source type (sharepoint/onedrive/email) [optional]: ").strip()
            site_name = input("Filter by site name [optional]: ").strip()

            filters = {}
            if source_type:
                filters['source_type'] = source_type
            if site_name:
                filters['site_name'] = site_name

            results = search.advanced_search(query, filters)
            print(f"\nFound {len(results)} results:\n")
            for i, r in enumerate(results, 1):
                print(f"{i}. {r['title']} ({r['source_type']})")
                print(f"   Score: {r['score']:.2f} | Site: {r['site_name']}")
                print(f"   {r['snippet'][:150]}...")
                print()

        elif choice == '3':
            query = input("Enter multimodal search query: ").strip()
            content_types = input("Content types (tables,equations,images,charts) [optional]: ").strip()
            content_types = content_types.split(',') if content_types else None

            results = search.multimodal_search(query, content_types)
            print(f"\nFound {len(results)} multimodal results:\n")
            for i, r in enumerate(results, 1):
                print(f"{i}. {r['title']} ({r['source_type']})")
                print(f"   Score: {r['score']:.2f}")
                print(f"   {r['snippet'][:150]}...")
                print()

        elif choice == '4':
            entity = input("Enter entity value: ").strip()
            entity_type = input("Enter entity type [optional]: ").strip()
            entity_type = entity_type if entity_type else None

            results = search.entity_search(entity, entity_type)
            print(f"\nFound {len(results)} documents with entity '{entity}':\n")
            for i, r in enumerate(results, 1):
                print(f"{i}. {r['title']} ({r['source_type']})")
                print(f"   Score: {r['score']:.2f}")
                print(f"   {r['snippet'][:150]}...")
                print()

        elif choice == '5':
            doc_id = input("Enter document ID: ").strip()
            results = search.relationship_search(doc_id)
            print(f"\nFound {len(results)} related documents:\n")
            for i, r in enumerate(results, 1):
                print(f"{i}. {r['title']} ({r['source_type']})")
                print(f"   Score: {r['score']:.2f}")
                print(f"   {r['snippet'][:150]}...")
                print()

        elif choice == '6':
            print("\nDocument counts by source:")
            for bucket in search.aggregate_by_source():
                print(f"  {bucket['key']}: {bucket['doc_count']:,}")

            print("\nTop 10 sites by document count:")
            for bucket in search.aggregate_by_site()[:10]:
                print(f"  {bucket['key']}: {bucket['doc_count']:,}")

            print("\nEntity type distribution:")
            for bucket in search.aggregate_by_entity_type():
                print(f"  {bucket['key']}: {bucket['doc_count']:,}")

        elif choice == '7':
            days = input("Show documents from last N days (default 7): ").strip()
            days = int(days) if days.isdigit() else 7

            results = search.get_recent_documents(days)
            print(f"\nRecent documents (last {days} days):\n")
            for i, r in enumerate(results, 1):
                print(f"{i}. {r['title']} ({r['source_type']})")
                print(f"   Modified: {r['modified_date']} by {r['created_by']}")
                print()

        elif choice == '8':
            results = search.get_enhanced_documents()
            print(f"\nEnhanced documents (RAG-Anything processed):\n")
            for i, r in enumerate(results, 1):
                print(f"{i}. {r['title']} ({r['source_type']})")
                print(f"   Complexity: {r['complexity_score']:.2f} | Entities: {len(r['entities'])}")
                print(f"   Topics: {r['topics']}")
                print()

        elif choice == '9':
            print("Goodbye!")
            break

        else:
            print("Invalid option")

if __name__ == "__main__":
    try:
        interactive_search()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"\n❌ Error: {e}")
