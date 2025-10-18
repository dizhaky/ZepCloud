#!/usr/bin/env python3
"""
Debug script for M365 authentication issues
"""

import os
import json
import requests
from dotenv import load_dotenv
from m365_auth import M365Auth

def debug_authentication():
    """Debug M365 authentication step by step"""
    print("🔍 M365 Authentication Debug")
    print("=" * 50)

    # Load environment
    load_dotenv()

    # Check environment variables
    print("\n1. Environment Variables:")
    client_id = os.getenv('M365_CLIENT_ID')
    client_secret = os.getenv('M365_CLIENT_SECRET')
    tenant_id = os.getenv('M365_TENANT_ID')

    print(f"   M365_CLIENT_ID: {'✅ Set' if client_id else '❌ Missing'}")
    print(f"   M365_CLIENT_SECRET: {'✅ Set' if client_secret else '❌ Missing'}")
    print(f"   M365_TENANT_ID: {'✅ Set' if tenant_id else '❌ Missing'}")

    if not all([client_id, client_secret, tenant_id]):
        print("❌ Missing required environment variables")
        return False

    # Test authentication
    print("\n2. Authentication Test:")
    try:
        auth = M365Auth()
        token = auth.get_access_token()

        if token:
            print("   ✅ Token acquired successfully")
            print(f"   Token preview: {token[:20]}...")

            # Decode token to check details
            try:
                import base64
                parts = token.split('.')
                if len(parts) >= 2:
                    payload = parts[1]
                    payload += '=' * (4 - len(payload) % 4)
                    decoded = base64.urlsafe_b64decode(payload)
                    token_data = json.loads(decoded)

                    print(f"   Token audience: {token_data.get('aud', 'unknown')}")
                    print(f"   Token app ID: {token_data.get('appid', 'unknown')}")
                    print(f"   Token scopes: {token_data.get('scp', 'unknown')}")
                    print(f"   Token roles: {token_data.get('roles', 'unknown')}")
                else:
                    print("   ⚠️  Token format issue")
            except Exception as e:
                print(f"   ⚠️  Token decode error: {e}")
        else:
            print("   ❌ Failed to acquire token")
            return False

    except Exception as e:
        print(f"   ❌ Authentication error: {e}")
        return False

    # Test Graph API endpoints
    print("\n3. Graph API Endpoint Tests:")

    headers = auth.get_graph_headers()
    if not headers:
        print("   ❌ Failed to generate headers")
        return False

    # Test different endpoints
    endpoints = [
        ("Organization", "https://graph.microsoft.com/v1.0/organization"),
        ("Users", "https://graph.microsoft.com/v1.0/users?$top=1"),
        ("Sites", "https://graph.microsoft.com/v1.0/sites?search=*"),
        ("Applications", "https://graph.microsoft.com/v1.0/applications?$top=1"),
    ]

    for name, url in endpoints:
        try:
            response = requests.get(url, headers=headers, timeout=30)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"   {status} {name}: {response.status_code}")

            if response.status_code != 200:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error_code = error_data.get('error', {}).get('code', 'unknown')
                error_message = error_data.get('error', {}).get('message', 'unknown')
                print(f"      Error: {error_code} - {error_message[:100]}")
        except Exception as e:
            print(f"   ❌ {name}: Exception - {e}")

    # Test with different scopes
    print("\n4. Scope Testing:")
    try:
        # Try with explicit scope
        from msal import ConfidentialClientApplication

        app = ConfidentialClientApplication(
            client_id=client_id,
            client_credential=client_secret,
            authority=f"https://login.microsoftonline.com/{tenant_id}"
        )

        # Try different scopes
        scopes = [
            ["https://graph.microsoft.com/.default"],
            ["https://graph.microsoft.com/Sites.Read.All"],
            ["https://graph.microsoft.com/User.Read.All"],
            ["https://graph.microsoft.com/Files.Read.All"],
        ]

        for scope in scopes:
            try:
                result = app.acquire_token_silent(scope, account=None)
                if not result:
                    result = app.acquire_token_for_client(scopes=scope)

                if result and 'access_token' in result:
                    print(f"   ✅ Scope {scope[0]}: Token acquired")
                else:
                    error = result.get('error', 'unknown') if result else 'no result'
                    print(f"   ❌ Scope {scope[0]}: {error}")
            except Exception as e:
                print(f"   ❌ Scope {scope[0]}: {e}")

    except Exception as e:
        print(f"   ❌ Scope testing error: {e}")

    print("\n5. Recommendations:")
    print("   - If all endpoints fail with 403, wait 5-15 minutes for permission propagation")
    print("   - If specific endpoints fail, check if those permissions are granted")
    print("   - If token acquisition fails, check client secret and tenant ID")
    print("   - If scopes fail, check if the app has the required permissions")

    return True

if __name__ == "__main__":
    debug_authentication()
