#!/usr/bin/env python3
"""
Microsoft Calendar Indexer
Index calendar events and meetings for all users
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

class CalendarIndexer:
    """Index Microsoft Calendar data to Azure Blob Storage"""

    def __init__(self, progress_file: str = "calendar_progress.json"):
        self.logger = setup_logging('calendar-indexer', level='INFO')
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
            'events_processed': 0,
            'events_uploaded': 0,
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
            'total_events': 0
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

    def get_user_calendar_events(self, user_id: str, days_back: int = 90) -> List[Dict[str, Any]]:
        """Get calendar events for a user"""
        headers = self.auth.get_graph_headers()
        if not headers:
            return []

        try:
            # Get events from last N days
            start_date = (datetime.now() - timedelta(days=days_back)).isoformat()

            response = requests.get(
                f'https://graph.microsoft.com/v1.0/users/{user_id}/calendar/events?$top=100&$filter=start/dateTime ge \'{start_date}\'',
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                return response.json().get('value', [])
            else:
                return []

        except Exception as e:
            print(f"⚠️  Error getting calendar events: {e}")
            return []

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True
    )
    def _upload_event_to_blob(self, event_data: Dict[str, Any], user_name: str):
        """Upload calendar event to blob storage"""
        event_id = event_data.get('id', 'unknown')

        # Create a searchable document from the event
        content = {
            'user': user_name,
            'subject': event_data.get('subject', 'No Subject'),
            'organizer': event_data.get('organizer', {}).get('emailAddress', {}).get('name', 'Unknown'),
            'start': event_data.get('start', {}).get('dateTime', ''),
            'end': event_data.get('end', {}).get('dateTime', ''),
            'location': event_data.get('location', {}).get('displayName', ''),
            'attendees': [att.get('emailAddress', {}).get('name', '') for att in event_data.get('attendees', [])],
            'body': event_data.get('body', {}).get('content', ''),
            'isOnlineMeeting': event_data.get('isOnlineMeeting', False),
            'onlineMeetingUrl': event_data.get('onlineMeetingUrl', ''),
            'importance': event_data.get('importance', 'normal'),
            'categories': event_data.get('categories', [])
        }

        # Create blob name
        safe_user = user_name.replace('/', '_').replace(' ', '_')
        blob_name = f"calendar/{safe_user}/{event_id}.json"

        # Upload to blob storage
        blob_client = self.container_client.get_blob_client(blob_name)
        blob_client.upload_blob(
            json.dumps(content, indent=2),
            overwrite=True,
            content_type='application/json'
        )

        self.stats['events_uploaded'] += 1

    def index_user(self, user_id: str, user_name: str, days_back: int = 90) -> Dict[str, Any]:
        """Index calendar events for a user"""
        result = {
            'user_id': user_id,
            'user_name': user_name,
            'events': 0,
            'errors': 0
        }

        try:
            # Get calendar events
            events = self.get_user_calendar_events(user_id, days_back)

            for event in events:
                try:
                    self._upload_event_to_blob(event, user_name)
                    result['events'] += 1
                    self.stats['events_processed'] += 1
                except Exception as e:
                    result['errors'] += 1
                    self.stats['errors'] += 1

            self.stats['users_processed'] += 1

            # Update progress
            self.progress['users'][user_id] = {
                'name': user_name,
                'last_sync': datetime.now().isoformat(),
                'events': result['events']
            }
            self._save_progress()

        except Exception as e:
            print(f"❌ Error processing user {user_name}: {e}")
            result['errors'] += 1

        return result

    def index_all_users(self, days_back: int = 90, limit: int = None) -> Dict[str, Any]:
        """Index calendar events for all users"""
        print("🚀 Starting Calendar indexing for all users...")

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

                result = self.index_user(user_id, user_name, days_back)
                results.append(result)

            # Update overall progress
            self.progress['last_sync'] = datetime.now().isoformat()
            self.progress['total_events'] = self.stats['events_processed']
            self._save_progress()

            return {
                'success': True,
                'users_processed': self.stats['users_processed'],
                'events_processed': self.stats['events_processed'],
                'events_uploaded': self.stats['events_uploaded'],
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
            'total_events': self.progress.get('total_events', 0)
        }

if __name__ == "__main__":
    indexer = CalendarIndexer()
    result = indexer.index_all_users(days_back=90)
    print(f"\n✅ Calendar indexing complete!")
    print(f"   Users: {result.get('users_processed', 0)}")
    print(f"   Events: {result.get('events_processed', 0)}")
