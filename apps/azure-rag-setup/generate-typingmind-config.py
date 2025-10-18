#!/usr/bin/env python3
"""
TypingMind Configuration Generator
Generates configuration for TypingMind Azure AI Search plugin
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, Any, Optional

from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TypingMindConfigGenerator:
    """Generates TypingMind configuration for Azure AI Search plugin"""

    def __init__(self):
        self.search_service_name = os.getenv('AZURE_SEARCH_SERVICE_NAME')
        self.admin_key = os.getenv('AZURE_SEARCH_ADMIN_KEY')
        self.endpoint = os.getenv('AZURE_SEARCH_ENDPOINT')
        self.index_name = os.getenv('AZURE_SEARCH_INDEX_NAME', 'training-data-index')

        if not all([self.search_service_name, self.admin_key, self.endpoint]):
            raise ValueError("Azure Search credentials not found in .env file")

        # Initialize search client
        self.search_client = SearchClient(
            endpoint=self.endpoint,
            index_name=self.index_name,
            credential=AzureKeyCredential(self.admin_key)
        )

    def create_query_key(self) -> str:
        """Create a new query key for TypingMind"""
        print("🔑 Creating query key for TypingMind...")

        # For now, we'll use the admin key
        # In production, you should create a dedicated query key
        query_key = self.admin_key

        print("✅ Query key ready")
        return query_key

    def test_search_connectivity(self) -> bool:
        """Test Azure AI Search connectivity"""
        print("🔍 Testing search connectivity...")

        try:
            # Test search with a simple query
            results = self.search_client.search(
                search_text="*",
                top=1,
                include_total_count=True
            )

            # Get the results
            result_list = list(results)
            total_count = results.get_count()

            print(f"✅ Search connectivity test passed")
            print(f"📊 Total documents in index: {total_count}")

            if total_count > 0:
                print("✅ Index contains documents - ready for TypingMind!")
                return True
            else:
                print("⚠️  Index is empty - run the indexer first")
                return False

        except Exception as e:
            print(f"❌ Search connectivity test failed: {e}")
            return False

    def generate_typingmind_config(self) -> Dict[str, Any]:
        """Generate TypingMind plugin configuration"""
        print("⚙️  Generating TypingMind configuration...")

        # Get query key
        query_key = self.create_query_key()

        # Configuration for TypingMind Azure AI Search plugin
        config = {
            "plugin_name": "Azure AI Search (RAG)",
            "search_service_name": self.search_service_name,
            "index_name": self.index_name,
            "query_key": query_key,
            "api_version": "2023-11-01",
            "endpoint": self.endpoint,
            "configuration_notes": {
                "created_at": datetime.now().isoformat(),
                "description": "Azure AI Search RAG plugin for TypingMind",
                "usage": "Enable this plugin in TypingMind to search your training data"
            }
        }

        return config

    def generate_manual_setup_instructions(self) -> str:
        """Generate manual setup instructions for TypingMind"""
        config = self.generate_typingmind_config()

        instructions = f"""
# TypingMind Azure AI Search Plugin Setup

## Step 1: Open TypingMind Settings
1. Open TypingMind application
2. Go to **Settings** → **Plugins**
3. Find **"Query Training Data - Azure AI Search"** plugin
4. Click **"Enable"** or **"Configure"**

## Step 2: Enter Configuration
Use these exact values:

**Search Service Name:**
```
{config['search_service_name']}
```

**Index Name:**
```
{config['index_name']}
```

**Query Key:**
```
{config['query_key']}
```

**API Version:**
```
{config['api_version']}
```

## Step 3: Test the Plugin
1. Save the configuration
2. Try these test queries in TypingMind:
   - "Search from training data for [your topic]"
   - "What information do I have about [subject]"
   - "Find documents related to [keyword]"

## Step 4: Verify Results
- The AI should now search your uploaded documents
- Results should include relevant information from your training data
- You can ask follow-up questions about the retrieved content

## Troubleshooting
- If no results: Check that the indexer has completed successfully
- If connection errors: Verify the search service name and query key
- If permission errors: Ensure CORS is enabled on the search service

## Configuration Details
- **Endpoint:** {config['endpoint']}
- **Created:** {config['configuration_notes']['created_at']}
- **Description:** {config['configuration_notes']['description']}
"""

        return instructions

    def save_configuration_files(self) -> None:
        """Save configuration to files"""
        print("💾 Saving configuration files...")

        # Generate configuration
        config = self.generate_typingmind_config()

        # Save JSON configuration
        config_file = "typingmind-azure-config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Configuration saved to: {config_file}")

        # Save manual instructions
        instructions = self.generate_manual_setup_instructions()
        instructions_file = "typingmind-setup-instructions.md"
        with open(instructions_file, 'w') as f:
            f.write(instructions)
        print(f"✅ Instructions saved to: {instructions_file}")

        # Save environment summary
        env_summary = {
            "azure_search_service": self.search_service_name,
            "azure_search_endpoint": self.endpoint,
            "azure_search_index": self.index_name,
            "configuration_generated": datetime.now().isoformat()
        }

        summary_file = "azure-rag-summary.json"
        with open(summary_file, 'w') as f:
            json.dump(env_summary, f, indent=2)
        print(f"✅ Summary saved to: {summary_file}")

    def display_configuration(self) -> None:
        """Display configuration for manual entry"""
        config = self.generate_typingmind_config()

        print("\n" + "=" * 60)
        print("🔧 TYPINGMIND CONFIGURATION")
        print("=" * 60)
        print()
        print("Copy these values into TypingMind plugin settings:")
        print()
        print(f"Search Service Name: {config['search_service_name']}")
        print(f"Index Name: {config['index_name']}")
        print(f"Query Key: {config['query_key']}")
        print(f"API Version: {config['api_version']}")
        print()
        print("=" * 60)
        print("📋 SETUP INSTRUCTIONS")
        print("=" * 60)
        print()
        print("1. Open TypingMind → Settings → Plugins")
        print("2. Find 'Query Training Data - Azure AI Search'")
        print("3. Enable the plugin")
        print("4. Enter the configuration values above")
        print("5. Save and test with: 'Search from training data for [topic]'")
        print()

def main():
    """Main configuration generation process"""
    print("🔧 TypingMind Configuration Generator")
    print("=" * 50)

    try:
        # Initialize generator
        generator = TypingMindConfigGenerator()

        # Test connectivity
        if not generator.test_search_connectivity():
            print("⚠️  Search connectivity test failed")
            print("💡 Make sure the indexer has run successfully")
            print("💡 Run: python3 configure-indexer.py")
            return 1

        # Generate and save configuration
        generator.save_configuration_files()

        # Display configuration
        generator.display_configuration()

        print("\n✅ Configuration generation completed!")
        print("📁 Check the generated files for detailed instructions")

    except Exception as e:
        print(f"❌ Error during configuration generation: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
