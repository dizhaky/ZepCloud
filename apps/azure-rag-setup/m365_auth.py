#!/usr/bin/env python3
"""
M365 Authentication - Supports both Application and Delegated permissions
"""

import os
from typing import Optional, Dict
from dotenv import load_dotenv

class M365Auth:
    """Handle M365 authentication with automatic method selection"""

    def __init__(self):
        load_dotenv()

        # Check if we should use delegated auth
        use_delegated = os.getenv('M365_USE_DELEGATED_AUTH', 'false').lower() == 'true'

        if use_delegated:
            # Try interactive browser auth first (works better with org policies)
            try:
                from m365_auth_interactive import M365AuthInteractive
                self._auth = M365AuthInteractive()
                print("🔐 Using interactive browser authentication (user context)")
            except Exception as e:
                print(f"⚠️  Interactive auth not available, falling back to device code: {e}")
                from m365_auth_delegated import M365AuthDelegated
                self._auth = M365AuthDelegated()
                print("🔐 Using device code authentication (user context)")
        else:
            from m365_auth_app import M365Auth as M365AuthApp
            self._auth = M365AuthApp()
            print("🔐 Using application authentication (app context)")

    def get_access_token(self) -> Optional[str]:
        """Get access token"""
        return self._auth.get_access_token()

    def get_graph_headers(self) -> Optional[Dict[str, str]]:
        """Get headers for Microsoft Graph API requests"""
        return self._auth.get_graph_headers()

    def validate_credentials(self) -> bool:
        """Validate that credentials are configured"""
        return self._auth.validate_credentials()

    def test_connection(self) -> bool:
        """Test connection to Microsoft Graph API"""
        return self._auth.test_connection()

if __name__ == "__main__":
    # Test authentication
    auth = M365Auth()
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
