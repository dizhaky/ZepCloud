#!/usr/bin/env python3
"""
RAG-Anything M365 Integration Orchestrator
Coordinates the enhanced preprocessing pipeline for M365 documents
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import shared utilities
from logger import setup_logging
from config_manager import get_config_manager

# Import enhanced indexers
from m365_sharepoint_indexer_enhanced import EnhancedSharePointIndexer

class RAGAnythingOrchestrator:
    """
    Orchestrates the enhanced M365 document processing pipeline
    - Routes documents to appropriate processors
    - Manages graph relationships
    - Coordinates Azure indexing
    - Tracks progress and errors
    """

    def __init__(self):
        self.config = get_config_manager()
        self.logger = setup_logging('rag-anything-orchestrator', level='INFO')
        self.stats = {
            'start_time': datetime.now(),
            'sharepoint_docs': 0,
            'onedrive_docs': 0,
            'exchange_docs': 0,
            'total_relationships': 0,
            'errors': []
        }

        # Initialize enhanced indexers
        self.sharepoint_indexer = None
        self.onedrive_indexer = None
        self.exchange_indexer = None

    def sync_sharepoint(
        self,
        site_limit: int = None,
        site_id: str = None
    ) -> Dict[str, Any]:
        """
        Sync SharePoint documents with enhanced processing

        Args:
            site_limit: Limit number of sites to process
            site_id: Specific site ID to process

        Returns:
            Result dictionary with statistics
        """
        print("="*60)
        print("📊 SharePoint Enhanced Sync")
        print("="*60)

        # Initialize SharePoint indexer
        if not self.sharepoint_indexer:
            self.sharepoint_indexer = EnhancedSharePointIndexer()

        try:
            if site_id:
                # Process specific site
                result = self.sharepoint_indexer.index_site(site_id, f"Site-{site_id}")
            else:
                # Process all sites (or limited)
                result = self.sharepoint_indexer.index_all_sites(limit=site_limit)

            # Update stats
            self.stats['sharepoint_docs'] = result.get('documents_uploaded', 0)
            self.stats['total_relationships'] += result.get('relationships_created', 0)

            return result

        except Exception as e:
            error_msg = f"SharePoint sync failed: {e}"
            print(f"❌ {error_msg}")
            self.stats['errors'].append(error_msg)
            return {'error': error_msg}

    def sync_onedrive(
        self,
        user_limit: int = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Sync OneDrive documents with enhanced processing

        Args:
            user_limit: Limit number of users to process
            user_id: Specific user ID to process

        Returns:
            Result dictionary with statistics
        """
        print("="*60)
        print("📊 OneDrive Enhanced Sync")
        print("="*60)
        print("⚠️  OneDrive enhanced indexer not yet implemented")
        print("   Use: python3 m365_onedrive_indexer.py")

        return {'status': 'not_implemented', 'message': 'Use standard OneDrive indexer for now'}

    def sync_exchange(
        self,
        user_limit: int = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Sync Exchange email attachments with enhanced processing

        Args:
            user_limit: Limit number of users to process
            user_id: Specific user ID to process

        Returns:
            Result dictionary with statistics
        """
        print("="*60)
        print("📊 Exchange Enhanced Sync")
        print("="*60)
        print("⚠️  Exchange enhanced indexer not yet implemented")
        print("   Use: python3 m365_exchange_indexer.py")

        return {'status': 'not_implemented', 'message': 'Use standard Exchange indexer for now'}

    def sync_all(
        self,
        sharepoint_limit: int = None,
        onedrive_limit: int = None,
        exchange_limit: int = None
    ) -> Dict[str, Any]:
        """
        Sync all M365 data sources

        Args:
            sharepoint_limit: Limit SharePoint sites
            onedrive_limit: Limit OneDrive users
            exchange_limit: Limit Exchange users

        Returns:
            Combined result dictionary
        """
        print("="*60)
        print("🚀 M365 Complete Enhanced Sync")
        print("="*60)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        results = {
            'sharepoint': None,
            'onedrive': None,
            'exchange': None,
            'summary': {}
        }

        # SharePoint
        print("\n1️⃣  Syncing SharePoint...")
        results['sharepoint'] = self.sync_sharepoint(site_limit=sharepoint_limit)

        # OneDrive
        print("\n2️⃣  Syncing OneDrive...")
        results['onedrive'] = self.sync_onedrive(user_limit=onedrive_limit)

        # Exchange
        print("\n3️⃣  Syncing Exchange...")
        results['exchange'] = self.sync_exchange(user_limit=exchange_limit)

        # Generate summary
        duration = datetime.now() - self.stats['start_time']
        results['summary'] = {
            'total_documents': (
                self.stats['sharepoint_docs'] +
                self.stats['onedrive_docs'] +
                self.stats['exchange_docs']
            ),
            'sharepoint_docs': self.stats['sharepoint_docs'],
            'onedrive_docs': self.stats['onedrive_docs'],
            'exchange_docs': self.stats['exchange_docs'],
            'total_relationships': self.stats['total_relationships'],
            'errors': len(self.stats['errors']),
            'duration': str(duration)
        }

        # Print summary
        print("\n" + "="*60)
        print("✅ M365 Enhanced Sync Complete")
        print("="*60)
        print(f"Duration: {duration}")
        print(f"Total Documents: {results['summary']['total_documents']}")
        print(f"  SharePoint: {results['summary']['sharepoint_docs']}")
        print(f"  OneDrive: {results['summary']['onedrive_docs']}")
        print(f"  Exchange: {results['summary']['exchange_docs']}")
        print(f"Total Relationships: {results['summary']['total_relationships']}")
        print(f"Errors: {results['summary']['errors']}")

        if self.stats['errors']:
            print("\n⚠️  Errors encountered:")
            for error in self.stats['errors']:
                print(f"   - {error}")

        return results

    def get_status(self) -> Dict[str, Any]:
        """Get status of all indexers"""
        print("="*60)
        print("📊 RAG-Anything Integration Status")
        print("="*60)

        status = {
            'sharepoint': None,
            'onedrive': None,
            'exchange': None,
            'azure_index': None
        }

        # SharePoint status
        if not self.sharepoint_indexer:
            self.sharepoint_indexer = EnhancedSharePointIndexer()
        status['sharepoint'] = self.sharepoint_indexer.get_status()

        print("\n📁 SharePoint:")
        print(f"   Last Sync: {status['sharepoint'].get('last_sync', 'Never')}")
        print(f"   Sites: {status['sharepoint'].get('sites_processed', 0)}")
        print(f"   Documents: {status['sharepoint'].get('total_documents', 0)}")
        print(f"   Relationships: {status['sharepoint'].get('total_relationships', 0)}")

        # Graph statistics
        if 'graph_stats' in status['sharepoint']:
            graph_stats = status['sharepoint']['graph_stats']
            print(f"\n📊 Graph Statistics:")
            print(f"   Documents in graph: {graph_stats['total_documents']}")
            print(f"   Total entities: {graph_stats['total_entities']}")
            print(f"   Total topics: {graph_stats['total_topics']}")
            print(f"   Avg connections/doc: {graph_stats['avg_relationships_per_doc']:.2f}")

        print("\n💡 Enhanced Features:")
        print("   ✅ Multimodal content detection")
        print("   ✅ Document relationship graphs")
        print("   ✅ Entity co-occurrence tracking")
        print("   ✅ Topic clustering")
        print("   ✅ Citation and reference extraction")

        return status

    def rebuild_graph(self) -> Dict[str, Any]:
        """Rebuild the document relationship graph"""
        print("="*60)
        print("🔄 Rebuilding Document Relationship Graph")
        print("="*60)
        print("⚠️  This will reprocess all documents to rebuild relationships")
        print("   This may take several minutes...")
        print()

        # TODO: Implement graph rebuild logic
        # This would reprocess existing Azure blobs to build graph

        return {'status': 'not_implemented', 'message': 'Graph rebuild coming soon'}


def main():
    """CLI interface for RAG-Anything orchestrator"""
    parser = argparse.ArgumentParser(
        description='RAG-Anything M365 Integration Orchestrator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sync SharePoint (limited to 5 sites)
  python3 orchestrate_rag_anything.py --source sharepoint --limit 5

  # Sync all M365 sources
  python3 orchestrate_rag_anything.py --source all

  # Get status
  python3 orchestrate_rag_anything.py --status

  # Sync specific SharePoint site
  python3 orchestrate_rag_anything.py --source sharepoint --site-id SITE_ID
        """
    )

    parser.add_argument(
        '--source',
        choices=['sharepoint', 'onedrive', 'exchange', 'all'],
        help='Data source to sync'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of items to process (sites/users)'
    )
    parser.add_argument(
        '--site-id',
        help='Specific SharePoint site ID to process'
    )
    parser.add_argument(
        '--user-id',
        help='Specific user ID to process'
    )
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show current status'
    )
    parser.add_argument(
        '--rebuild-graph',
        action='store_true',
        help='Rebuild document relationship graph'
    )

    args = parser.parse_args()

    # Initialize orchestrator
    orchestrator = RAGAnythingOrchestrator()

    # Handle status request
    if args.status:
        orchestrator.get_status()
        return 0

    # Handle graph rebuild
    if args.rebuild_graph:
        result = orchestrator.rebuild_graph()
        return 0 if result.get('status') != 'error' else 1

    # Handle sync operations
    if not args.source:
        parser.print_help()
        print("\n⚠️  Please specify --source or use --status")
        return 1

    # Execute sync based on source
    if args.source == 'sharepoint':
        result = orchestrator.sync_sharepoint(
            site_limit=args.limit,
            site_id=args.site_id
        )
    elif args.source == 'onedrive':
        result = orchestrator.sync_onedrive(
            user_limit=args.limit,
            user_id=args.user_id
        )
    elif args.source == 'exchange':
        result = orchestrator.sync_exchange(
            user_limit=args.limit,
            user_id=args.user_id
        )
    elif args.source == 'all':
        result = orchestrator.sync_all(
            sharepoint_limit=args.limit,
            onedrive_limit=args.limit,
            exchange_limit=args.limit
        )

    # Check for errors
    if result.get('error'):
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

