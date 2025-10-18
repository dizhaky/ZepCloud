"""
Main synchronization script for M365 to Elasticsearch with RAG-Anything
"""
from utils.graph_client import GraphClientWrapper
from utils.document_processor import DocumentProcessor
from utils.bulk_indexer import BulkIndexer
from utils.raganything_processor import RAGAnythingProcessor
from utils.elasticsearch_graph_builder import ElasticsearchGraphBuilder
from datetime import datetime
from tqdm import tqdm
import logging
from config_elasticsearch import Config

# Setup logging
logging.basicConfig(
    level=Config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class M365Sync:
    """Synchronize M365 data to Elasticsearch with RAG-Anything enhancements"""

    def __init__(self):
        logger.info("Initializing M365 Elasticsearch Sync...")
        self.graph = GraphClientWrapper()
        self.processor = DocumentProcessor()
        self.indexer = BulkIndexer()
        self.raganything_processor = RAGAnythingProcessor()
        self.graph_builder = ElasticsearchGraphBuilder(self.indexer)
        self.stats = {
            'sites_processed': 0,
            'documents_found': 0,
            'documents_indexed': 0,
            'documents_skipped': 0,
            'documents_enhanced': 0,
            'relationships_created': 0,
            'errors': 0
        }

    def sync_sharepoint(self):
        """Sync all SharePoint sites and documents with RAG-Anything processing"""
        logger.info("Starting SharePoint sync with RAG-Anything...")

        sites = self.graph.get_sites()
        if not sites:
            logger.warning("No SharePoint sites found")
            return

        logger.info(f"Found {len(sites.value)} SharePoint sites")

        for site in tqdm(sites.value, desc="SharePoint Sites"):
            try:
                self._process_site(site)
            except Exception as e:
                logger.error(f"Error processing site {site.get('displayName', 'Unknown')}: {e}")
                self.stats['errors'] += 1
                continue

        # Flush remaining documents
        self.indexer.flush()

        logger.info(f"SharePoint sync complete: {self.stats}")

    def _process_site(self, site):
        """Process a single SharePoint site"""
        site_name = site.get('displayName', 'Unknown')
        site_id = site.get('id')

        logger.info(f"Processing site: {site_name}")
        self.stats['sites_processed'] += 1

        # Get all document libraries
        drives_response = self.graph.get_drives(site_id)
        if not drives_response or not drives_response.value:
            logger.debug(f"No drives found for site {site_name}")
            return

        for drive in drives_response.value:
            try:
                self._process_drive(site_id, site_name, drive)
            except Exception as e:
                logger.error(f"Error processing drive {drive.get('name')}: {e}")
                continue

    def _process_drive(self, site_id, site_name, drive):
        """Process a document library"""
        drive_name = drive.get('name', 'Unknown')
        drive_id = drive.get('id')

        logger.info(f"  Processing library: {drive_name}")

        # Get root items
        items_response = self.graph.get_drive_items(site_id, drive_id)
        if not items_response or not items_response.value:
            return

        # Process items recursively
        self._process_items(site_id, site_name, drive_id, drive_name, items_response.value)

    def _process_items(self, site_id, site_name, drive_id, drive_name, items):
        """Process drive items recursively"""
        for item in items:
            self.stats['documents_found'] += 1

            # Check if it's a folder
            if 'folder' in item:
                # Recursively process folder
                folder_items = self.graph.get_drive_items(site_id, drive_id, item['id'])
                if folder_items and folder_items.value:
                    self._process_items(site_id, site_name, drive_id, drive_name, folder_items.value)
                continue

            # Process file
            try:
                self._process_file(site_id, site_name, drive_id, drive_name, item)
            except Exception as e:
                logger.error(f"Error processing file {item.get('name')}: {e}")
                self.stats['errors'] += 1
                continue

    def _process_file(self, site_id, site_name, drive_id, drive_name, item):
        """Process a single file with RAG-Anything enhancements"""
        file_name = item.get('name', '')
        file_size = item.get('size', 0)
        modified_date = item.get('lastModifiedDateTime')

        # Check if should process
        if not self.processor.should_process_file(file_name, file_size, modified_date):
            self.stats['documents_skipped'] += 1
            return

        # Extract metadata
        metadata = self.processor.extract_metadata(item)

        # Download and extract text with OlmoCR/RAG-Anything
        content_text = ""
        multimodal_content = {}

        if Config.ENABLE_OCR:
            file_content = self.graph.get_file_content(site_id, drive_id, item['id'])
            if file_content:
                mime_type = metadata.get('file_type')
                extraction_result = self.processor.extract_text(file_content, mime_type, file_name)
                content_text = extraction_result.get('content', '')
                multimodal_content = extraction_result.get('multimodal_content', {})

        # Create base document
        doc_id = f"sharepoint_{site_id}_{item['id']}"
        document = {
            "id": doc_id,
            "source_type": "sharepoint",
            "source_id": item['id'],
            "site_id": site_id,
            "site_name": site_name,
            "library_name": drive_name,
            "title": file_name,
            "content": content_text,
            "multimodal_content": multimodal_content,
            **metadata,
            "indexed_date": datetime.utcnow().isoformat(),
            "processing_status": "completed"
        }

        # Process with RAG-Anything for enhanced features
        enhanced_document = self.raganything_processor.process_document(document)

        if enhanced_document.get('entities') or enhanced_document.get('relationships'):
            self.stats['documents_enhanced'] += 1

        # Add to batch
        self.indexer.add_document(doc_id, enhanced_document)
        self.stats['documents_indexed'] += 1

    def sync_onedrive(self):
        """Sync OneDrive files for all users"""
        logger.info("Starting OneDrive sync...")

        users_response = self.graph.get_users()
        if not users_response or not users_response.value:
            logger.warning("No users found")
            return

        logger.info(f"Found {len(users_response.value)} users")

        for user in tqdm(users_response.value, desc="OneDrive Users"):
            try:
                self._process_user_onedrive(user)
            except Exception as e:
                logger.error(f"Error processing OneDrive for {user.get('displayName')}: {e}")
                continue

        self.indexer.flush()
        logger.info(f"OneDrive sync complete: {self.stats}")

    def _process_user_onedrive(self, user):
        """Process OneDrive for a single user"""
        user_name = user.get('displayName', 'Unknown')
        user_id = user.get('id')

        logger.info(f"Processing OneDrive for: {user_name}")

        # Get user's drive
        drive = self.graph.get_user_drive(user_id)
        if not drive:
            return

        drive_id = drive.id

        # Get root items
        items_response = self.graph.get_drive_items(None, drive_id)
        if not items_response or not items_response.value:
            return

        # Process items (similar to SharePoint)
        logger.info(f"  Found {len(items_response.value)} items in OneDrive")

    def sync_emails(self):
        """Sync emails for all users"""
        logger.info("Starting Email sync...")

        # Get date filter if enabled
        filter_query = None
        if Config.DATE_FILTER_ENABLED:
            date_from = Config.get_date_filter()
            if date_from:
                filter_query = f"receivedDateTime ge {date_from.isoformat()}"

        users_response = self.graph.get_users()
        if not users_response or not users_response.value:
            return

        for user in tqdm(users_response.value, desc="Email Users"):
            try:
                self._process_user_emails(user, filter_query)
            except Exception as e:
                logger.error(f"Error processing emails for {user.get('displayName')}: {e}")
                continue

        self.indexer.flush()
        logger.info(f"Email sync complete: {self.stats}")

    def _process_user_emails(self, user, filter_query):
        """Process emails for a single user"""
        user_name = user.get('displayName', 'Unknown')
        user_id = user.get('id')

        logger.info(f"Processing emails for: {user_name}")

        messages_response = self.graph.get_user_messages(user_id, filter_query)
        if not messages_response or not messages_response.value:
            return

        for message in messages_response.value:
            try:
                doc_id = f"email_{user_id}_{message.get('id')}"
                document = {
                    "id": doc_id,
                    "source_type": "email",
                    "source_id": message.get('id'),
                    "title": message.get('subject', ''),
                    "subject": message.get('subject', ''),
                    "content": message.get('body', {}).get('content', ''),
                    "from_email": message.get('from', {}).get('emailAddress', {}).get('address', ''),
                    "to_emails": [r.get('emailAddress', {}).get('address', '')
                                for r in message.get('toRecipients', [])],
                    "has_attachments": message.get('hasAttachments', False),
                    "created_date": message.get('receivedDateTime'),
                    "indexed_date": datetime.utcnow().isoformat(),
                    "processing_status": "completed"
                }

                # Process with RAG-Anything
                enhanced_document = self.raganything_processor.process_document(document)

                self.indexer.add_document(doc_id, enhanced_document)
                self.stats['documents_indexed'] += 1

            except Exception as e:
                logger.error(f"Error processing email: {e}")
                continue

    def build_relationships(self):
        """Build document relationships using RAG-Anything"""
        logger.info("Building document relationships...")

        # This would typically process existing documents to build relationships
        # For now, we'll create the relationship index
        self.indexer.create_relationship_index()

        logger.info("Relationship building complete")

    def run_full_sync(self):
        """Run complete sync of all M365 data sources"""
        start_time = datetime.utcnow()

        print("="*60)
        print("M365 to Elasticsearch Full Synchronization with RAG-Anything")
        print("="*60)
        print(f"Start time: {start_time}")
        print(f"Elasticsearch: {Config.ELASTIC_HOST}")
        print(f"Index: {Config.ELASTIC_INDEX}")
        print(f"RAG-Anything: {'Enabled' if Config.RAG_ANYTHING_ENABLED else 'Disabled'}")
        print(f"OlmoCR: {'Enabled' if Config.OLMOCR_ENABLED else 'Disabled'}")
        print(f"Date filter: {'Enabled' if Config.DATE_FILTER_ENABLED else 'Disabled'}")
        if Config.DATE_FILTER_ENABLED:
            print(f"  From: {Config.DATE_FILTER_FROM}")
        print("="*60)
        print()

        try:
            # Sync data sources
            self.sync_sharepoint()
            self.sync_onedrive()
            self.sync_emails()

            # Build relationships
            self.build_relationships()

        except KeyboardInterrupt:
            logger.warning("Sync interrupted by user")
            print("\n⚠️ Sync interrupted. Flushing remaining documents...")
            self.indexer.flush()
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            raise
        finally:
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()

            # Get final stats
            indexer_stats = self.indexer.get_stats()

            print("\n" + "="*60)
            print("Synchronization Complete!")
            print("="*60)
            print(f"Duration: {duration/60:.2f} minutes")
            print(f"Sites processed: {self.stats['sites_processed']:,}")
            print(f"Documents found: {self.stats['documents_found']:,}")
            print(f"Documents indexed: {self.stats['documents_indexed']:,}")
            print(f"Documents enhanced: {self.stats['documents_enhanced']:,}")
            print(f"Documents skipped: {self.stats['documents_skipped']:,}")
            print(f"Relationships created: {self.stats['relationships_created']:,}")
            print(f"Errors: {self.stats['errors']:,}")
            print(f"Success rate: {indexer_stats['success_rate']:.1f}%")
            print(f"Enhancement rate: {indexer_stats['enhancement_rate']:.1f}%")
            print("="*60)

if __name__ == "__main__":
    try:
        sync = M365Sync()
        sync.run_full_sync()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n❌ Sync failed: {e}")
        exit(1)
