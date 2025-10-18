"""
Bulk indexing utilities for Elasticsearch with RAG-Anything enhancements
"""
from elasticsearch import Elasticsearch, helpers
from config_elasticsearch import Config
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class BulkIndexer:
    """Handle bulk indexing to Elasticsearch with enhanced features"""

    def __init__(self):
        self.es = Elasticsearch(
            Config.ELASTIC_HOST,
            basic_auth=(Config.ELASTIC_USERNAME, Config.ELASTIC_PASSWORD)
        )
        self.batch = []
        self.batch_size = Config.BATCH_SIZE
        self.total_indexed = 0
        self.total_failed = 0
        self.enhanced_docs = 0  # Documents with RAG-Anything processing

    def add_document(self, doc_id, document):
        """Add document to batch with RAG-Anything enhancements"""

        # Add processing metadata
        document.update({
            "indexed_date": datetime.utcnow().isoformat(),
            "processing_pipeline": "elasticsearch-m365",
            "olmocr_processed": document.get("multimodal_content", {}).get("images") is not None,
            "raganything_processed": document.get("entities") is not None or document.get("relationships") is not None
        })

        # Count enhanced documents
        if document.get("entities") or document.get("relationships") or document.get("multimodal_content"):
            self.enhanced_docs += 1

        self.batch.append({
            "_index": Config.ELASTIC_INDEX,
            "_id": doc_id,
            "_source": document
        })

        # Index if batch is full
        if len(self.batch) >= self.batch_size:
            self.flush()

    def flush(self):
        """Index current batch"""
        if not self.batch:
            return

        try:
            success, failed = helpers.bulk(
                self.es,
                self.batch,
                raise_on_error=False,
                raise_on_exception=False
            )

            self.total_indexed += success
            self.total_failed += len(failed) if failed else 0

            if failed:
                logger.warning(f"Failed to index {len(failed)} documents")
                for item in failed[:5]:  # Log first 5 failures
                    logger.debug(f"Failed item: {item}")

            logger.info(f"Indexed batch: {success} succeeded, {len(failed) if failed else 0} failed")

            # Clear batch
            self.batch = []

            return success

        except Exception as e:
            logger.error(f"Bulk indexing error: {e}")
            self.batch = []
            return 0

    def get_stats(self):
        """Get indexing statistics including RAG-Anything metrics"""
        return {
            'total_indexed': self.total_indexed,
            'total_failed': self.total_failed,
            'enhanced_docs': self.enhanced_docs,
            'success_rate': (self.total_indexed / (self.total_indexed + self.total_failed) * 100)
                           if (self.total_indexed + self.total_failed) > 0 else 0,
            'enhancement_rate': (self.enhanced_docs / self.total_indexed * 100)
                              if self.total_indexed > 0 else 0
        }

    def create_relationship_index(self):
        """Create a separate index for document relationships"""
        relationship_mapping = {
            "mappings": {
                "properties": {
                    "source_doc_id": {"type": "keyword"},
                    "target_doc_id": {"type": "keyword"},
                    "relationship_type": {"type": "keyword"},
                    "strength": {"type": "float"},
                    "shared_entities": {"type": "keyword"},
                    "shared_topics": {"type": "keyword"},
                    "created_date": {"type": "date"}
                }
            }
        }

        relationship_index = f"{Config.ELASTIC_INDEX}-relationships"

        if not self.es.indices.exists(index=relationship_index):
            self.es.indices.create(index=relationship_index, body=relationship_mapping)
            logger.info(f"Created relationship index: {relationship_index}")

    def index_relationship(self, source_doc_id, target_doc_id, relationship_type, strength, shared_entities=None, shared_topics=None):
        """Index a document relationship"""
        relationship_doc = {
            "source_doc_id": source_doc_id,
            "target_doc_id": target_doc_id,
            "relationship_type": relationship_type,
            "strength": strength,
            "shared_entities": shared_entities or [],
            "shared_topics": shared_topics or [],
            "created_date": datetime.utcnow().isoformat()
        }

        relationship_index = f"{Config.ELASTIC_INDEX}-relationships"
        self.es.index(
            index=relationship_index,
            body=relationship_doc
        )
