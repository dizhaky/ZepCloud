#!/usr/bin/env python3
"""
Microsoft 365 Unified Indexer CLI
Main command-line interface for M365 data indexing
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
import json

# Import our modules
from m365_auth import M365Auth
from logger import setup_logging
from config_manager import get_config_manager
from estimate_m365_volume import M365VolumeEstimator
from m365_sharepoint_indexer import SharePointIndexer
from m365_onedrive_indexer import OneDriveIndexer
from m365_exchange_indexer import ExchangeIndexer
from m365_teams_indexer import TeamsIndexer
from m365_calendar_indexer import CalendarIndexer
from m365_contacts_indexer import ContactsIndexer

class M365IndexerCLI:
    """Unified CLI for M365 indexing operations"""

    def __init__(self):
        self.config = get_config_manager()
        self.logger = setup_logging('m365-indexer', level='INFO')
        self.auth = M365Auth()

    def cmd_estimate(self, args):
        """Run volume estimation"""
        print("🔍 Running M365 Volume Estimation...")

        estimator = M365VolumeEstimator()
        results = estimator.run_estimation()

        if 'error' in results:
            print(f"❌ Estimation failed: {results['error']}")
            return 1

        # Print summary
        estimator.print_summary()

        # Save report if requested
        if args.output:
            report_file = estimator.save_report(args.output)
            print(f"📄 Report saved to: {report_file}")

        return 0

    def cmd_sync_sharepoint(self, args):
        """Sync SharePoint documents"""
        print("🏢 Starting SharePoint sync...")

        if not self.auth.test_connection():
            print("❌ Authentication failed")
            return 1

        indexer = SharePointIndexer()

        if hasattr(args, 'site') and args.site:
            # Sync specific site
            result = indexer.index_site(args.site, f"Site-{args.site}")
        else:
            # Sync all sites
            limit = args.limit if hasattr(args, 'limit') else None
            result = indexer.index_all_sites(limit)

        if result.get('success'):
            print(f"\n✅ SharePoint sync completed!")
            print(f"   Sites: {result.get('sites_processed', 0)}")
            print(f"   Documents: {result.get('total_documents', 0)}")
            print(f"   Uploaded: {result.get('documents_uploaded', 0)}")
            print(f"   Skipped: {result.get('documents_skipped', 0)}")
            print(f"   Errors: {result.get('errors', 0)}")
            print(f"   Duration: {result.get('duration', 'Unknown')}")
            return 0
        else:
            print(f"❌ SharePoint sync failed: {result.get('error')}")
            return 1

    def cmd_sync_onedrive(self, args):
        """Sync OneDrive documents"""
        print("👥 Starting OneDrive sync...")

        if not self.auth.test_connection():
            print("❌ Authentication failed")
            return 1

        indexer = OneDriveIndexer()

        if args.user:
            # Sync specific user
            result = indexer.index_user(args.user, f"User-{args.user}")
        else:
            # Sync all users
            result = indexer.index_all_users(args.limit)

        if result.get('success'):
            print(f"\n✅ OneDrive sync completed!")
            print(f"   Users: {result.get('users_processed', 0)}")
            print(f"   Documents: {result.get('total_documents', 0)}")
            print(f"   Uploaded: {result.get('documents_uploaded', 0)}")
            print(f"   Skipped: {result.get('documents_skipped', 0)}")
            print(f"   Errors: {result.get('errors', 0)}")
            print(f"   Duration: {result.get('duration', 'Unknown')}")
            return 0
        else:
            print(f"❌ OneDrive sync failed: {result.get('error')}")
            return 1

    def cmd_sync_exchange(self, args):
        """Sync Exchange emails and attachments"""
        print("📧 Starting Exchange sync...")

        if not self.auth.test_connection():
            print("❌ Authentication failed")
            return 1

        indexer = ExchangeIndexer()

        if args.user:
            # Sync specific user
            result = indexer.index_user(args.user, f"User-{args.user}", args.days)
        else:
            # Sync all users
            result = indexer.index_all_users(args.limit, args.days)

        if result.get('success'):
            print(f"\n✅ Exchange sync completed!")
            print(f"   Users: {result.get('users_processed', 0)}")
            print(f"   Emails: {result.get('total_emails', 0)}")
            print(f"   Attachments: {result.get('total_attachments', 0)}")
            print(f"   Uploaded: {result.get('attachments_uploaded', 0)}")
            print(f"   Skipped: {result.get('emails_skipped', 0)}")
            print(f"   Errors: {result.get('errors', 0)}")
            print(f"   Duration: {result.get('duration', 'Unknown')}")
            return 0
        else:
            print(f"❌ Exchange sync failed: {result.get('error')}")
            return 1

    def cmd_sync(self, args):
        """Sync all M365 data sources"""
        print("🚀 Starting full M365 sync...")

        # Start with SharePoint (MVP)
        print("\n1️⃣  Syncing SharePoint...")
        sharepoint_result = self.cmd_sync_sharepoint(args)

        if sharepoint_result != 0:
            print("❌ SharePoint sync failed, stopping")
            return sharepoint_result

        # Sync OneDrive
        print("\n2️⃣  Syncing OneDrive...")
        onedrive_result = self.cmd_sync_onedrive(args)

        if onedrive_result != 0:
            print("⚠️  OneDrive sync failed, continuing with Exchange...")

        # Sync Exchange
        print("\n3️⃣  Syncing Exchange...")
        exchange_result = self.cmd_sync_exchange(args)

        if exchange_result != 0:
            print("⚠️  Exchange sync failed, but SharePoint and OneDrive completed")

        print("\n✅ M365 sync completed!")
        return 0

    def cmd_status(self, args):
        """Show sync status for all services"""
        print("📊 M365 Sync Status")
        print("=" * 40)

        # SharePoint status
        try:
            indexer = SharePointIndexer()
            status = indexer.get_status()

            print(f"\n🏢 SharePoint:")
            print(f"   Last Sync: {status.get('last_sync', 'Never')}")
            print(f"   Sites Processed: {status.get('sites_processed', 0)}")
            print(f"   Total Documents: {status.get('total_documents', 0)}")
            print(f"   Processed Documents: {status.get('processed_documents', 0)}")
        except Exception as e:
            print(f"   ❌ Error getting status: {e}")

        # OneDrive status
        try:
            onedrive_indexer = OneDriveIndexer()
            onedrive_status = onedrive_indexer.get_status()

            print(f"\n👥 OneDrive:")
            print(f"   Last Sync: {onedrive_status.get('last_sync', 'Never')}")
            print(f"   Users Processed: {onedrive_status.get('users_processed', 0)}")
            print(f"   Total Documents: {onedrive_status.get('total_documents', 0)}")
            print(f"   Processed Documents: {onedrive_status.get('processed_documents', 0)}")
        except Exception as e:
            print(f"   ❌ Error getting OneDrive status: {e}")

        # Exchange status
        try:
            exchange_indexer = ExchangeIndexer()
            exchange_status = exchange_indexer.get_status()

            print(f"\n📧 Exchange:")
            print(f"   Last Sync: {exchange_status.get('last_sync', 'Never')}")
            print(f"   Users Processed: {exchange_status.get('users_processed', 0)}")
            print(f"   Total Emails: {exchange_status.get('total_emails', 0)}")
            print(f"   Total Attachments: {exchange_status.get('total_attachments', 0)}")
            print(f"   Processed Attachments: {exchange_status.get('processed_attachments', 0)}")
        except Exception as e:
            print(f"   ❌ Error getting Exchange status: {e}")

        return 0

    def cmd_test_auth(self, args):
        """Test authentication"""
        print("🔐 Testing M365 Authentication...")

        if self.auth.test_connection():
            print("✅ Authentication successful")
            return 0
        else:
            print("❌ Authentication failed")
            return 1

def create_parser():
    """Create command-line argument parser"""
    parser = argparse.ArgumentParser(
        description='Microsoft 365 Data Indexer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test authentication
  python3 m365_indexer.py test-auth

  # Estimate data volume
  python3 m365_indexer.py estimate

  # Sync SharePoint only
  python3 m365_indexer.py sync-sharepoint

  # Sync all services
  python3 m365_indexer.py sync

  # Show status
  python3 m365_indexer.py status
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Test authentication
    test_parser = subparsers.add_parser('test-auth', help='Test M365 authentication')

    # Volume estimation
    estimate_parser = subparsers.add_parser('estimate', help='Estimate M365 data volume')
    estimate_parser.add_argument('--output', help='Save report to file')

    # SharePoint sync
    sharepoint_parser = subparsers.add_parser('sync-sharepoint', help='Sync SharePoint documents')
    sharepoint_parser.add_argument('--site', help='Sync specific site by ID')
    sharepoint_parser.add_argument('--limit', type=int, help='Limit number of sites')

    # OneDrive sync
    onedrive_parser = subparsers.add_parser('sync-onedrive', help='Sync OneDrive documents')
    onedrive_parser.add_argument('--user', help='Sync specific user by ID')
    onedrive_parser.add_argument('--limit', type=int, help='Limit number of users to process')

    # Exchange sync
    exchange_parser = subparsers.add_parser('sync-exchange', help='Sync Exchange emails and attachments')
    exchange_parser.add_argument('--user', help='Sync specific user by ID')
    exchange_parser.add_argument('--limit', type=int, help='Limit number of users to process')
    exchange_parser.add_argument('--days', type=int, help='Only index emails from last N days')

    # Full sync
    sync_parser = subparsers.add_parser('sync', help='Sync all M365 data sources')
    sync_parser.add_argument('--limit', type=int, help='Limit number of sites (SharePoint)')

    # Status
    status_parser = subparsers.add_parser('status', help='Show sync status')

    return parser

def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    cli = M365IndexerCLI()

    # Route commands
    if args.command == 'test-auth':
        return cli.cmd_test_auth(args)
    elif args.command == 'estimate':
        return cli.cmd_estimate(args)
    elif args.command == 'sync-sharepoint':
        return cli.cmd_sync_sharepoint(args)
    elif args.command == 'sync-onedrive':
        return cli.cmd_sync_onedrive(args)
    elif args.command == 'sync-exchange':
        return cli.cmd_sync_exchange(args)
    elif args.command == 'sync':
        return cli.cmd_sync(args)
    elif args.command == 'status':
        return cli.cmd_status(args)
    else:
        print(f"❌ Unknown command: {args.command}")
        return 1


    def cmd_sync_teams(self, args):
        """Sync Teams messages and channels"""
        indexer = TeamsIndexer()

        print("🔄 Syncing Microsoft Teams...")
        result = indexer.index_all_teams(message_limit=args.message_limit if hasattr(args, 'message_limit') else 50)

        if result.get('success'):
            print(f"✅ Teams sync complete!")
            print(f"   Teams: {result['teams_processed']}")
            print(f"   Channels: {result['channels_processed']}")
            print(f"   Messages: {result['messages_processed']}")
        else:
            print(f"❌ Teams sync failed: {result.get('error', 'Unknown error')}")


    def cmd_sync_calendar(self, args):
        """Sync Calendar events"""
        indexer = CalendarIndexer()

        print("🔄 Syncing Calendar events...")
        result = indexer.index_all_users(
            days_back=args.days_back if hasattr(args, 'days_back') else 90,
            limit=args.limit if hasattr(args, 'limit') else None
        )

        if result.get('success'):
            print(f"✅ Calendar sync complete!")
            print(f"   Users: {result['users_processed']}")
            print(f"   Events: {result['events_processed']}")
        else:
            print(f"❌ Calendar sync failed: {result.get('error', 'Unknown error')}")


    def cmd_sync_contacts(self, args):
        """Sync Outlook contacts"""
        indexer = ContactsIndexer()

        print("🔄 Syncing Outlook contacts...")
        result = indexer.index_all_users(limit=args.limit if hasattr(args, 'limit') else None)

        if result.get('success'):
            print(f"✅ Contacts sync complete!")
            print(f"   Users: {result['users_processed']}")
            print(f"   Contacts: {result['contacts_processed']}")
        else:
            print(f"❌ Contacts sync failed: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    exit(main())
