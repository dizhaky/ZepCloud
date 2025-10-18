#!/usr/bin/env python3
"""
Microsoft 365 Exchange Indexer
Downloads and indexes Exchange emails and attachments for all users to Azure Blob Storage
"""

# Standard library imports
import os
import json
import time
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional

# Third-party imports
import requests
from azure.storage.blob import BlobServiceClient
from tenacity import retry, stop_after_attempt, wait_exponential
from tqdm import tqdm

# Local application imports
from config_manager import get_config_manager
from logger import setup_logging
from m365_auth import M365Auth

class ExchangeIndexer:
    """Index Exchange emails and attachments for all users to Azure Blob Storage"""

    def __init__(self, progress_file: str = None):
        self.config = get_config_manager()
        self.logger = setup_logging('exchange-indexer', level='INFO')
        self.auth = M365Auth()

        # Use config manager for progress file
        self.progress_file = Path(progress_file or self.config.get_progress_file('exchange'))
        self.progress = self._load_progress()

        # Azure Blob Storage setup
        self.connection_string = self.config.get_connection_string()
        self.blob_service = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = self.blob_service.get_container_client(
            self.config.get_azure_storage_config().get('container_name', 'training-data')
        )

        # Supported attachment file types from config
        self.supported_attachment_extensions = set(self.config.get_supported_file_extensions('exchange'))

        # Statistics
        self.stats = {
            'users_processed': 0,
            'emails_found': 0,
            'attachments_found': 0,
            'attachments_uploaded': 0,
            'emails_skipped': 0,
            'errors': 0,
            'start_time': datetime.now()
        }

    def _load_progress(self) -> Dict[str, Any]:
        """Load progress tracking data"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Error loading progress: {e}")

        return {
            'last_sync': None,
            'users': {},
            'total_emails': 0,
            'total_attachments': 0
        }

    def _save_progress(self):
        """Save progress tracking data"""
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(self.progress, f, indent=2)
        except Exception as e:
            print(f"⚠️  Error saving progress: {e}")


    def _get_file_extension(self, filename: str) -> str:
        """Get file extension in lowercase"""
        return Path(filename).suffix.lower()

    def _is_supported_attachment(self, filename: str) -> bool:
        """Check if attachment file type is supported for indexing"""
        return self._get_file_extension(filename) in self.supported_attachment_extensions

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True
    )
    def _download_file(self, download_url: str, timeout: int = 300) -> bytes:
        """Download file content with retry logic"""
        headers = self.auth.get_graph_headers()
        if not headers:
            raise Exception("Authentication failed")

        response = requests.get(download_url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.content

    def _upload_to_blob(self, content: bytes, blob_name: str, metadata: Dict[str, str] = None) -> bool:
        """Upload content to Azure Blob Storage"""
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            blob_client.upload_blob(
                content,
                overwrite=True,
                metadata=metadata or {},
                timeout=300
            )
            return True
        except Exception as e:
            print(f"❌ Upload failed for {blob_name}: {e}")
            return False

    def _get_user_emails(self, user_id: str, user_name: str, date_range_days: int = None) -> List[Dict[str, Any]]:
        """Get emails from a user's mailbox"""
        headers = self.auth.get_graph_headers()
        if not headers:
            return []

        emails = []

        try:
            # Build date filter if specified
            date_filter = ""
            if date_range_days:
                start_date = datetime.now() - timedelta(days=date_range_days)
                date_filter = f"&$filter=receivedDateTime ge {start_date.isoformat()}Z"

            # Get messages from inbox and other folders
            messages_url = f'https://graph.microsoft.com/v1.0/users/{user_id}/messages?$top=1000{date_filter}'

            print(f"   📧 Processing emails for: {user_name}")

            while messages_url:
                response = requests.get(messages_url, headers=headers, timeout=30)

                if response.status_code != 200:
                    print(f"⚠️  Failed to get emails for {user_name}: {response.status_code}")
                    break

                data = response.json()
                messages = data.get('value', [])

                for message in messages:
                    email_info = {
                        'id': message.get('id'),
                        'subject': message.get('subject', 'No Subject'),
                        'sender': message.get('sender', {}).get('emailAddress', {}).get('address', 'Unknown'),
                        'received': message.get('receivedDateTime'),
                        'body_preview': message.get('bodyPreview', ''),
                        'has_attachments': message.get('hasAttachments', False),
                        'web_url': message.get('webLink', ''),
                        'user_name': user_name
                    }
                    emails.append(email_info)

                # Get next page URL
                messages_url = data.get('@odata.nextLink')
                if messages_url:
                    time.sleep(0.5)  # Rate limiting

        except Exception as e:
            print(f"❌ Error processing emails for {user_name}: {e}")
            self.stats['errors'] += 1

        return emails

    def _get_email_attachments(self, user_id: str, message_id: str, user_name: str, subject: str) -> List[Dict[str, Any]]:
        """Get attachments from a specific email"""
        headers = self.auth.get_graph_headers()
        if not headers:
            return []

        attachments = []

        try:
            # Get attachments for this message
            attachments_url = f'https://graph.microsoft.com/v1.0/users/{user_id}/messages/{message_id}/attachments'
            response = requests.get(attachments_url, headers=headers, timeout=30)

            if response.status_code != 200:
                return []

            data = response.json()
            attachment_items = data.get('value', [])

            for attachment in attachment_items:
                attachment_name = attachment.get('name', '')

                if self._is_supported_attachment(attachment_name):
                    attachment_info = {
                        'id': attachment.get('id'),
                        'name': attachment_name,
                        'size': attachment.get('size', 0),
                        'content_type': attachment.get('contentType', ''),
                        'content_bytes': attachment.get('contentBytes'),
                        'user_name': user_name,
                        'email_subject': subject,
                        'message_id': message_id
                    }
                    attachments.append(attachment_info)

        except Exception as e:
            print(f"⚠️  Error getting attachments for {subject}: {e}")

        return attachments

    def _process_attachment(self, attachment: Dict[str, Any]) -> bool:
        """Process a single attachment (upload to blob storage)"""
        try:
            # Generate blob name
            user_name = attachment['user_name']
            email_subject = attachment['email_subject']
            filename = attachment['name']

            # Clean up path for blob storage
            clean_user = user_name.replace(' ', '_').replace('/', '_')
            clean_subject = email_subject.replace(' ', '_').replace('/', '_')[:50]  # Limit length
            blob_name = f"exchange/{clean_user}/attachments/{clean_subject}/{filename}"

            # Check if already processed
            if self._is_attachment_processed(attachment['id']):
                self.stats['emails_skipped'] += 1
                return True

            # Get attachment content
            content_bytes = attachment.get('content_bytes')
            if not content_bytes:
                print(f"⚠️  No content for attachment {filename}")
                return False

            # Decode base64 content
            import base64
            content = base64.b64decode(content_bytes)

            print(f"   📎 Processing attachment: {filename}")

            # Prepare metadata
            metadata = {
                'source': 'exchange',
                'user_name': user_name,
                'email_subject': email_subject,
                'attachment_name': filename,
                'file_size': str(attachment['size']),
                'content_type': attachment.get('content_type', ''),
                'message_id': attachment['message_id'],
                'indexed_at': datetime.now().isoformat()
            }

            # Upload to blob storage
            if self._upload_to_blob(content, blob_name, metadata):
                self._mark_attachment_processed(attachment['id'])
                self.stats['attachments_uploaded'] += 1
                return True
            else:
                self.stats['errors'] += 1
                return False

        except Exception as e:
            print(f"❌ Error processing attachment {attachment.get('name', 'unknown')}: {e}")
            self.stats['errors'] += 1
            return False

    def _is_attachment_processed(self, attachment_id: str) -> bool:
        """Check if attachment has already been processed"""
        return attachment_id in self.progress.get('processed_attachments', set())

    def _mark_attachment_processed(self, attachment_id: str):
        """Mark attachment as processed"""
        if 'processed_attachments' not in self.progress:
            self.progress['processed_attachments'] = set()
        self.progress['processed_attachments'].add(attachment_id)

    def index_user(self, user_id: str, user_name: str, date_range_days: int = None) -> Dict[str, Any]:
        """Index emails and attachments from a specific user's mailbox"""
        print(f"📧 Indexing Exchange for: {user_name}")

        start_time = datetime.now()
        emails = self._get_user_emails(user_id, user_name, date_range_days)

        if not emails:
            print(f"   ℹ️  No emails found for {user_name}")
            return {'success': True, 'emails': 0, 'attachments': 0}

        print(f"   📊 Found {len(emails)} emails")

        # Process emails and their attachments
        processed_attachments = 0
        total_attachments = 0

        for email in tqdm(emails, desc=f"Processing {user_name}"):
            if email.get('has_attachments'):
                attachments = self._get_email_attachments(
                    user_id,
                    email['id'],
                    user_name,
                    email['subject']
                )
                total_attachments += len(attachments)

                for attachment in attachments:
                    if self._process_attachment(attachment):
                        processed_attachments += 1

        # Update progress
        self.progress['users'][user_id] = {
            'name': user_name,
            'last_sync': datetime.now().isoformat(),
            'emails_found': len(emails),
            'attachments_found': total_attachments,
            'attachments_processed': processed_attachments
        }

        self._save_progress()

        duration = datetime.now() - start_time
        print(f"   ✅ Completed {user_name}: {processed_attachments}/{total_attachments} attachments in {duration}")

        return {
            'success': True,
            'emails': len(emails),
            'attachments': total_attachments,
            'processed_attachments': processed_attachments,
            'duration': str(duration)
        }

    def index_all_users(self, limit: int = None, date_range_days: int = None) -> Dict[str, Any]:
        """Index emails and attachments from all users' mailboxes"""
        print("🚀 Starting Exchange indexing for all users...")

        headers = self.auth.get_graph_headers()
        if not headers:
            return {'error': 'Authentication failed'}

        try:
            # Get all users in the organization
            users_response = requests.get(
                'https://graph.microsoft.com/v1.0/users?$select=id,displayName,userPrincipalName',
                headers=headers,
                timeout=30
            )

            if users_response.status_code != 200:
                return {'error': f'Failed to get users: {users_response.status_code}'}

            users_data = users_response.json()
            users = users_data.get('value', [])

            if limit:
                users = users[:limit]

            print(f"📊 Found {len(users)} users")

            results = []
            for user in users:
                user_id = user.get('id')
                user_name = user.get('displayName', user.get('userPrincipalName', 'Unknown'))

                result = self.index_user(user_id, user_name, date_range_days)
                results.append({
                    'user_name': user_name,
                    'user_id': user_id,
                    **result
                })

                self.stats['users_processed'] += 1
                self.stats['emails_found'] += result.get('emails', 0)
                self.stats['attachments_found'] += result.get('attachments', 0)

            # Update overall progress
            self.progress['last_sync'] = datetime.now().isoformat()
            self.progress['total_emails'] = self.stats['emails_found']
            self.progress['total_attachments'] = self.stats['attachments_found']
            self._save_progress()

            return {
                'success': True,
                'users_processed': self.stats['users_processed'],
                'total_emails': self.stats['emails_found'],
                'total_attachments': self.stats['attachments_found'],
                'attachments_uploaded': self.stats['attachments_uploaded'],
                'emails_skipped': self.stats['emails_skipped'],
                'errors': self.stats['errors'],
                'duration': str(datetime.now() - self.stats['start_time']),
                'user_results': results
            }

        except Exception as e:
            return {'error': f'Indexing failed: {e}'}

    def get_status(self) -> Dict[str, Any]:
        """Get current indexing status"""
        return {
            'last_sync': self.progress.get('last_sync'),
            'users_processed': len(self.progress.get('users', {})),
            'total_emails': self.progress.get('total_emails', 0),
            'total_attachments': self.progress.get('total_attachments', 0),
            'processed_attachments': len(self.progress.get('processed_attachments', set())),
            'current_stats': self.stats
        }

def main():
    """CLI interface for Exchange indexer"""
    import argparse

    parser = argparse.ArgumentParser(description='Exchange Email and Attachment Indexer')
    parser.add_argument('--user', help='Index specific user by ID')
    parser.add_argument('--limit', type=int, help='Limit number of users to process')
    parser.add_argument('--days', type=int, help='Only index emails from last N days')
    parser.add_argument('--status', action='store_true', help='Show indexing status')

    args = parser.parse_args()

    indexer = ExchangeIndexer()

    if args.status:
        status = indexer.get_status()
        print("📊 Exchange Indexing Status:")
        print(f"   Last Sync: {status.get('last_sync', 'Never')}")
        print(f"   Users Processed: {status.get('users_processed', 0)}")
        print(f"   Total Emails: {status.get('total_emails', 0)}")
        print(f"   Total Attachments: {status.get('total_attachments', 0)}")
        print(f"   Processed Attachments: {status.get('processed_attachments', 0)}")
        return 0

    if args.user:
        # Index specific user
        result = indexer.index_user(args.user, f"User-{args.user}", args.days)
        print(f"Result: {result}")
    else:
        # Index all users
        result = indexer.index_all_users(args.limit, args.days)

        if result.get('success'):
            print(f"\n✅ Exchange indexing completed!")
            print(f"   Users: {result['users_processed']}")
            print(f"   Emails: {result['total_emails']}")
            print(f"   Attachments: {result['total_attachments']}")
            print(f"   Uploaded: {result['attachments_uploaded']}")
            print(f"   Skipped: {result['emails_skipped']}")
            print(f"   Errors: {result['errors']}")
            print(f"   Duration: {result['duration']}")
        else:
            print(f"❌ Exchange indexing failed: {result.get('error')}")
            return 1

    return 0

if __name__ == "__main__":
    exit(main())
