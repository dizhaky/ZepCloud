#!/usr/bin/env python3
"""
Microsoft Contacts Indexer
Index Outlook contacts for all users
"""

# Standard library imports
import os
import json
import time
from pathlib import Path
from datetime import datetime, timezone
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

class ContactsIndexer:
    """Index Microsoft Outlook Contacts to Azure Blob Storage"""

    def __init__(self, progress_file: str = "contacts_progress.json"):
        self.logger = setup_logging('contacts-indexer', level='INFO')
        self.auth = M365Auth()
        self.progress_file = Path(progress_file)
        self.progress = self._load_progress()

        # Azure Blob Storage setup
        self.connection_string = self._get_connection_string()
        self.blob_service = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = self.blob_service.get_container_client("training-data")

        # Statistics
        self.stats = {
            'users_processed': 0,
            'contacts_processed': 0,
            'contacts_uploaded': 0,
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
            'total_contacts': 0
        }

    def _save_progress(self):
        """Save progress tracking data"""
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(self.progress, f, indent=2)
        except Exception as e:
            print(f"⚠️  Error saving progress: {e}")

    def _get_connection_string(self) -> str:
        """Get Azure Storage connection string"""
        account_name = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
        account_key = os.getenv('AZURE_STORAGE_ACCOUNT_KEY')

        if not account_name or not account_key:
            raise ValueError("Missing Azure Storage credentials in environment")

        return f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"

    def get_user_contacts(self, user_id: str) -> List[Dict[str, Any]]:
        """Get contacts for a user"""
        headers = self.auth.get_graph_headers()
        if not headers:
            return []

        try:
            response = requests.get(
                f'https://graph.microsoft.com/v1.0/users/{user_id}/contacts?$top=100',
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                return response.json().get('value', [])
            else:
                return []

        except Exception as e:
            print(f"⚠️  Error getting contacts: {e}")
            return []

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True
    )
    def _upload_contact_to_blob(self, contact_data: Dict[str, Any], user_name: str):
        """Upload contact to blob storage"""
        contact_id = contact_data.get('id', 'unknown')

        # Create a searchable document from the contact
        content = {
            'user': user_name,
            'displayName': contact_data.get('displayName', ''),
            'givenName': contact_data.get('givenName', ''),
            'surname': contact_data.get('surname', ''),
            'emailAddresses': [email.get('address', '') for email in contact_data.get('emailAddresses', [])],
            'businessPhones': contact_data.get('businessPhones', []),
            'mobilePhone': contact_data.get('mobilePhone', ''),
            'jobTitle': contact_data.get('jobTitle', ''),
            'companyName': contact_data.get('companyName', ''),
            'department': contact_data.get('department', ''),
            'officeLocation': contact_data.get('officeLocation', ''),
            'businessAddress': contact_data.get('businessAddress', {}),
            'categories': contact_data.get('categories', [])
        }

        # Create blob name
        safe_user = user_name.replace('/', '_').replace(' ', '_')
        safe_name = contact_data.get('displayName', 'unknown').replace('/', '_').replace(' ', '_')
        blob_name = f"contacts/{safe_user}/{safe_name}_{contact_id}.json"

        # Upload to blob storage
        blob_client = self.container_client.get_blob_client(blob_name)
        blob_client.upload_blob(
            json.dumps(content, indent=2),
            overwrite=True,
            content_type='application/json'
        )

        self.stats['contacts_uploaded'] += 1

    def index_user(self, user_id: str, user_name: str) -> Dict[str, Any]:
        """Index contacts for a user"""
        result = {
            'user_id': user_id,
            'user_name': user_name,
            'contacts': 0,
            'errors': 0
        }

        try:
            # Get contacts
            contacts = self.get_user_contacts(user_id)

            for contact in contacts:
                try:
                    self._upload_contact_to_blob(contact, user_name)
                    result['contacts'] += 1
                    self.stats['contacts_processed'] += 1
                except Exception as e:
                    result['errors'] += 1
                    self.stats['errors'] += 1

            self.stats['users_processed'] += 1

            # Update progress
            self.progress['users'][user_id] = {
                'name': user_name,
                'last_sync': datetime.now().isoformat(),
                'contacts': result['contacts']
            }
            self._save_progress()

        except Exception as e:
            print(f"❌ Error processing user {user_name}: {e}")
            result['errors'] += 1

        return result

    def index_all_users(self, limit: int = None) -> Dict[str, Any]:
        """Index contacts for all users"""
        print("🚀 Starting Contacts indexing for all users...")

        headers = self.auth.get_graph_headers()
        if not headers:
            return {'error': 'Authentication failed'}

        try:
            # Get all users
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
            for user in tqdm(users, desc="Processing users"):
                user_id = user.get('id')
                user_name = user.get('displayName', user.get('userPrincipalName', 'Unknown'))

                result = self.index_user(user_id, user_name)
                results.append(result)

            # Update overall progress
            self.progress['last_sync'] = datetime.now().isoformat()
            self.progress['total_contacts'] = self.stats['contacts_processed']
            self._save_progress()

            return {
                'success': True,
                'users_processed': self.stats['users_processed'],
                'contacts_processed': self.stats['contacts_processed'],
                'contacts_uploaded': self.stats['contacts_uploaded'],
                'errors': self.stats['errors'],
                'results': results
            }

        except Exception as e:
            print(f"❌ Error: {e}")
            return {'error': str(e)}

    def get_status(self) -> Dict[str, Any]:
        """Get current sync status"""
        return {
            'last_sync': self.progress.get('last_sync'),
            'users_processed': len(self.progress.get('users', {})),
            'total_contacts': self.progress.get('total_contacts', 0)
        }

if __name__ == "__main__":
    indexer = ContactsIndexer()
    result = indexer.index_all_users()
    print(f"\n✅ Contacts indexing complete!")
    print(f"   Users: {result.get('users_processed', 0)}")
    print(f"   Contacts: {result.get('contacts_processed', 0)}")
