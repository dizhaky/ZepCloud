#!/usr/bin/env python3
from dotenv import load_dotenv
import os
from azure.storage.blob import BlobServiceClient

load_dotenv()

connection_string = f"DefaultEndpointsProtocol=https;AccountName={os.getenv('AZURE_STORAGE_ACCOUNT_NAME')};AccountKey={os.getenv('AZURE_STORAGE_ACCOUNT_KEY')};EndpointSuffix=core.windows.net"

try:
    blob_service = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service.get_container_client("training-data")
    
    blobs = list(container_client.list_blobs())
    
    print(f"📊 Azure Blob Storage Status:")
    print(f"   Total blobs: {len(blobs)}")
    
    # Count by type
    m365_blobs = [b for b in blobs if 'm365' in b.name.lower() or 'sharepoint' in b.name.lower()]
    print(f"   M365/SharePoint blobs: {len(m365_blobs)}")
    
    if m365_blobs:
        print(f"\n📄 Recent M365 uploads:")
        for blob in sorted(m365_blobs, key=lambda x: x.last_modified, reverse=True)[:10]:
            print(f"   - {blob.name} ({blob.size} bytes, {blob.last_modified})")
    
    # Check recent uploads (last 24 hours)
    from datetime import datetime, timedelta
    recent = datetime.now() - timedelta(hours=1)
    recent_blobs = [b for b in blobs if b.last_modified.replace(tzinfo=None) > recent]
    
    if recent_blobs:
        print(f"\n🆕 Uploads in last hour: {len(recent_blobs)}")
        for blob in sorted(recent_blobs, key=lambda x: x.last_modified, reverse=True)[:5]:
            print(f"   - {blob.name}")
    
except Exception as e:
    print(f"❌ Error checking blob storage: {e}")
