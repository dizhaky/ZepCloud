#!/usr/bin/env python3
"""
Microsoft Teams Indexer
Index Teams messages, channels, and conversations
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

class TeamsIndexer:
    """Index Microsoft Teams data to Azure Blob Storage"""

    def __init__(self, progress_file: str = None):
        self.config = get_config_manager()
        self.logger = setup_logging('teams-indexer', level='INFO')
        self.auth = M365Auth()

        # Use config manager for progress file
        self.progress_file = Path(progress_file or self.config.get_progress_file('teams'))
        self.progress = self._load_progress()

        # Azure Blob Storage setup
        self.connection_string = self._get_connection_string()
        self.blob_service = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = self.blob_service.get_container_client("training-data")

        # Statistics
        self.stats = {
            'teams_processed': 0,
            'channels_processed': 0,
            'messages_processed': 0,
            'messages_uploaded': 0,
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
            'teams': {},
            'total_messages': 0
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

    def get_all_teams(self) -> List[Dict[str, Any]]:
        """Get all teams the user has access to"""
        headers = self.auth.get_graph_headers()
        if not headers:
            return []

        try:
            response = requests.get(
                'https://graph.microsoft.com/v1.0/me/joinedTeams',
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                teams = response.json().get('value', [])
                print(f"📊 Found {len(teams)} teams")
                return teams
            else:
                print(f"❌ Failed to get teams: {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ Error getting teams: {e}")
            return []

    def get_team_channels(self, team_id: str) -> List[Dict[str, Any]]:
        """Get all channels for a team"""
        headers = self.auth.get_graph_headers()
        if not headers:
            return []

        try:
            response = requests.get(
                f'https://graph.microsoft.com/v1.0/teams/{team_id}/channels',
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                return response.json().get('value', [])
            else:
                return []

        except Exception as e:
            print(f"⚠️  Error getting channels: {e}")
            return []

    def get_channel_messages(self, team_id: str, channel_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get messages from a channel"""
        headers = self.auth.get_graph_headers()
        if not headers:
            return []

        try:
            response = requests.get(
                f'https://graph.microsoft.com/v1.0/teams/{team_id}/channels/{channel_id}/messages?$top={limit}',
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                return response.json().get('value', [])
            else:
                return []

        except Exception as e:
            print(f"⚠️  Error getting messages: {e}")
            return []

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True
    )
    def _upload_message_to_blob(self, message_data: Dict[str, Any], team_name: str, channel_name: str):
        """Upload Teams message to blob storage"""
        message_id = message_data.get('id', 'unknown')

        # Create a searchable text document from the message
        content = {
            'team': team_name,
            'channel': channel_name,
            'from': message_data.get('from', {}).get('user', {}).get('displayName', 'Unknown'),
            'created': message_data.get('createdDateTime', ''),
            'subject': message_data.get('subject', ''),
            'body': message_data.get('body', {}).get('content', ''),
            'importance': message_data.get('importance', 'normal'),
            'messageType': message_data.get('messageType', 'message')
        }

        # Create blob name
        safe_team = team_name.replace('/', '_').replace(' ', '_')
        safe_channel = channel_name.replace('/', '_').replace(' ', '_')
        blob_name = f"teams/{safe_team}/{safe_channel}/{message_id}.json"

        # Upload to blob storage
        blob_client = self.container_client.get_blob_client(blob_name)
        blob_client.upload_blob(
            json.dumps(content, indent=2),
            overwrite=True,
            content_type='application/json'
        )

        self.stats['messages_uploaded'] += 1

    def index_team(self, team_id: str, team_name: str, message_limit: int = 50) -> Dict[str, Any]:
        """Index all channels and messages for a team"""
        print(f"\n📁 Processing team: {team_name}")

        result = {
            'team_id': team_id,
            'team_name': team_name,
            'channels': 0,
            'messages': 0,
            'errors': 0
        }

        try:
            # Get channels
            channels = self.get_team_channels(team_id)
            result['channels'] = len(channels)

            for channel in tqdm(channels, desc=f"  Channels in {team_name}"):
                channel_id = channel.get('id')
                channel_name = channel.get('displayName', 'Unknown')

                try:
                    # Get messages
                    messages = self.get_channel_messages(team_id, channel_id, message_limit)

                    for message in messages:
                        try:
                            self._upload_message_to_blob(message, team_name, channel_name)
                            result['messages'] += 1
                            self.stats['messages_processed'] += 1
                        except Exception as e:
                            result['errors'] += 1
                            self.stats['errors'] += 1

                    self.stats['channels_processed'] += 1

                except Exception as e:
                    print(f"  ⚠️  Error processing channel {channel_name}: {e}")
                    result['errors'] += 1

            self.stats['teams_processed'] += 1

            # Update progress
            self.progress['teams'][team_id] = {
                'name': team_name,
                'last_sync': datetime.now().isoformat(),
                'messages': result['messages']
            }
            self._save_progress()

        except Exception as e:
            print(f"❌ Error processing team: {e}")
            result['errors'] += 1

        return result

    def index_all_teams(self, message_limit: int = 50) -> Dict[str, Any]:
        """Index all teams"""
        print("🚀 Starting Teams indexing...")

        teams = self.get_all_teams()
        if not teams:
            return {'error': 'No teams found or authentication failed'}

        results = []
        for team in teams:
            team_id = team.get('id')
            team_name = team.get('displayName', 'Unknown')

            result = self.index_team(team_id, team_name, message_limit)
            results.append(result)

        # Update overall progress
        self.progress['last_sync'] = datetime.now().isoformat()
        self.progress['total_messages'] = self.stats['messages_processed']
        self._save_progress()

        return {
            'success': True,
            'teams_processed': self.stats['teams_processed'],
            'channels_processed': self.stats['channels_processed'],
            'messages_processed': self.stats['messages_processed'],
            'messages_uploaded': self.stats['messages_uploaded'],
            'errors': self.stats['errors'],
            'results': results
        }

    def get_status(self) -> Dict[str, Any]:
        """Get current sync status"""
        return {
            'last_sync': self.progress.get('last_sync'),
            'teams_processed': len(self.progress.get('teams', {})),
            'total_messages': self.progress.get('total_messages', 0)
        }

if __name__ == "__main__":
    indexer = TeamsIndexer()
    result = indexer.index_all_teams(message_limit=50)
    print(f"\n✅ Teams indexing complete!")
    print(f"   Teams: {result.get('teams_processed', 0)}")
    print(f"   Channels: {result.get('channels_processed', 0)}")
    print(f"   Messages: {result.get('messages_processed', 0)}")
