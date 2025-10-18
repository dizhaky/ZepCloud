#!/usr/bin/env python3
"""
M365 Authentication using Application Permissions (Client Credentials Flow)
"""

import os
from typing import Optional, Dict
from msal import ConfidentialClientApplication
from dotenv import load_dotenv

class M365Auth:
    """Handle M365 authentication with application permissions"""

    def __init__(self):
        load_dotenv()

        self.client_id = os.getenv('M365_CLIENT_ID')
        self.client_secret = os.getenv('M365_CLIENT_SECRET')
        self.tenant_id = os.getenv('M365_TENANT_ID')

        if not all([self.client_id, self.client_secret, self.tenant_id]):
            raise ValueError("M365_CLIENT_ID, M365_CLIENT_SECRET, and M365_TENANT_ID must be set")

        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scope = ["https://graph.microsoft.com/.default"]

        self.app = ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=self.authority
        )

        self._access_token = None

    def get_access_token(self) -> Optional[str]:
        """Get access token using client credentials flow"""
        result = self.app.acquire_token_silent(self.scope, account=None)

        if not result:
            result = self.app.acquire_token_for_client(scopes=self.scope)

        if 'access_token' in result:
            self._access_token = result['access_token']
            return self._access_token
        else:
            error = result.get('error_description', result.get('error', 'Unknown error'))
            raise ValueError(f"Failed to acquire token: {error}")

    def get_graph_headers(self) -> Optional[Dict[str, str]]:
        """Get headers for Microsoft Graph API requests"""
        token = self.get_access_token()
        if token:
            return {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
        return None

    def validate_credentials(self) -> bool:
        """Validate that all required credentials are present"""
        missing = []

        if not self.client_id:
            missing.append("M365_CLIENT_ID")
        if not self.client_secret:
            missing.append("M365_CLIENT_SECRET")
        if not self.tenant_id:
            missing.append("M365_TENANT_ID")

        if missing:
            print("❌ Missing required environment variables:")
            for var in missing:
                print(f"   - {var}")
            return False

        return True

    def test_connection(self) -> bool:
        """Test connection to Microsoft Graph API"""
        import requests

        try:
            headers = self.get_graph_headers()
            if not headers:
                return False

            # Test with a simple endpoint
            response = requests.get(
                'https://graph.microsoft.com/v1.0/organization',
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                print("✅ Successfully connected to Microsoft Graph API")
                return True
            else:
                print(f"❌ Graph API test failed: {response.status_code} - {response.text[:200]}")
                return False

        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
