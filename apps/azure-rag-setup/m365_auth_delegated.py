#!/usr/bin/env python3
"""
M365 Authentication using Delegated Permissions (Device Code Flow)
This uses user authentication instead of application-only permissions
"""

import os
from typing import Optional, Dict
from msal import PublicClientApplication
from dotenv import load_dotenv

class M365AuthDelegated:
    """Handle M365 authentication with delegated permissions"""

    def __init__(self):
        load_dotenv()

        self.client_id = os.getenv('M365_CLIENT_ID')
        self.tenant_id = os.getenv('M365_TENANT_ID')

        if not self.client_id or not self.tenant_id:
            raise ValueError("M365_CLIENT_ID and M365_TENANT_ID must be set in .env")

        # Scopes for delegated permissions
        self.scopes = [
            "https://graph.microsoft.com/Sites.Read.All",
            "https://graph.microsoft.com/Files.Read.All",
            "https://graph.microsoft.com/Mail.Read",
            "https://graph.microsoft.com/User.Read.All"
        ]

        # Create public client application
        self.app = PublicClientApplication(
            client_id=self.client_id,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}"
        )

        self.token_cache_file = ".m365_token_cache.json"
        self._access_token = None

    def get_access_token(self) -> Optional[str]:
        """Get access token using device code flow"""

        # Try to get token from cache first
        accounts = self.app.get_accounts()
        if accounts:
            print("🔄 Using cached credentials...")
            result = self.app.acquire_token_silent(self.scopes, account=accounts[0])
            if result and 'access_token' in result:
                self._access_token = result['access_token']
                return self._access_token

        # If no cached token, use device code flow
        print("\n🔐 M365 Authentication Required")
        print("=" * 50)
        print("Please authenticate with your Microsoft account")
        print("")

        flow = self.app.initiate_device_flow(scopes=self.scopes)

        if "user_code" not in flow:
            raise ValueError(f"Failed to create device flow: {flow.get('error_description')}")

        print(flow["message"])
        print("")
        print("⏳ Waiting for authentication...")

        # Wait for user to authenticate
        result = self.app.acquire_token_by_device_flow(flow)

        if "access_token" in result:
            self._access_token = result['access_token']
            print("✅ Authentication successful!")
            return self._access_token
        else:
            error = result.get('error_description', result.get('error', 'Unknown error'))
            raise ValueError(f"Authentication failed: {error}")

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
        """Validate that credentials are configured"""
        if not self.client_id:
            print("❌ M365_CLIENT_ID not set")
            return False
        if not self.tenant_id:
            print("❌ M365_TENANT_ID not set")
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

if __name__ == "__main__":
    # Test authentication
    auth = M365AuthDelegated()
    if auth.validate_credentials():
        print("✅ Credentials configured")
        try:
            token = auth.get_access_token()
            if token:
                print(f"✅ Token acquired: {token[:20]}...")
            else:
                print("❌ Failed to acquire token")
        except Exception as e:
            print(f"❌ Error: {e}")
