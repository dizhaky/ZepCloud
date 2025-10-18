#!/usr/bin/env python3
"""
Azure RAG Data Upload Script
Automates uploading OneDrive and email data to Azure Blob Storage for RAG indexing
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import mimetypes

# Azure imports
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.core.exceptions import AzureError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DataUploader:
    """Handles uploading training data to Azure Blob Storage"""

    def __init__(self):
        self.storage_account_name = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
        self.storage_key = os.getenv('AZURE_STORAGE_ACCOUNT_KEY')
        self.container_name = os.getenv('AZURE_STORAGE_CONTAINER_NAME', 'training-data')

        if not all([self.storage_account_name, self.storage_key]):
            raise ValueError("Azure storage credentials not found in .env file")

        # Initialize blob service client
        connection_string = f"DefaultEndpointsProtocol=https;AccountName={self.storage_account_name};AccountKey={self.storage_key};EndpointSuffix=core.windows.net"
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        # Supported file types
        self.supported_extensions = {
            '.pdf', '.docx', '.doc', '.txt', '.md', '.rtf',
            '.xlsx', '.xls', '.csv', '.json', '.xml',
            '.msg', '.eml', '.html', '.htm'
        }

        # Upload statistics
        self.stats = {
            'total_files': 0,
            'uploaded_files': 0,
            'skipped_files': 0,
            'error_files': 0,
            'total_size': 0
        }

    def scan_onedrive_folder(self, onedrive_path: str) -> List[Path]:
        """Scan OneDrive folder for supported documents"""
        print(f"🔍 Scanning OneDrive folder: {onedrive_path}")

        if not os.path.exists(onedrive_path):
            print(f"⚠️  OneDrive path not found: {onedrive_path}")
            return []

        documents = []
        for root, dirs, files in os.walk(onedrive_path):
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in self.supported_extensions:
                    documents.append(file_path)

        print(f"📄 Found {len(documents)} supported documents")
        return documents

    def scan_email_archives(self, email_path: str) -> List[Path]:
        """Scan for email archive files"""
        print(f"📧 Scanning email archives: {email_path}")

        if not os.path.exists(email_path):
            print(f"⚠️  Email path not found: {email_path}")
            return []

        email_files = []
        for root, dirs, files in os.walk(email_path):
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in ['.msg', '.eml', '.mbox']:
                    email_files.append(file_path)

        print(f"📧 Found {len(email_files)} email files")
        return email_files

    def get_file_metadata(self, file_path: Path) -> Dict[str, str]:
        """Extract metadata from file"""
        stat = file_path.stat()

        metadata = {
            'source': 'onedrive' if 'OneDrive' in str(file_path) else 'email',
            'filename': file_path.name,
            'filepath': str(file_path),
            'size': str(stat.st_size),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'content_type': mimetypes.guess_type(str(file_path))[0] or 'application/octet-stream'
        }

        return metadata

    def upload_file(self, file_path: Path, blob_name: str = None) -> bool:
        """Upload a single file to Azure Blob Storage"""
        try:
            if blob_name is None:
                # Create blob name with folder structure
                blob_name = str(file_path.relative_to(file_path.anchor))

            # Get file metadata
            metadata = self.get_file_metadata(file_path)

            # Create blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )

            # Upload file with metadata
            with open(file_path, 'rb') as data:
                blob_client.upload_blob(
                    data,
                    overwrite=True,
                    metadata=metadata,
                    content_type=metadata['content_type']
                )

            self.stats['uploaded_files'] += 1
            self.stats['total_size'] += file_path.stat().st_size
            print(f"✅ Uploaded: {file_path.name}")
            return True

        except AzureError as e:
            print(f"❌ Error uploading {file_path.name}: {e}")
            self.stats['error_files'] += 1
            return False
        except Exception as e:
            print(f"❌ Unexpected error uploading {file_path.name}: {e}")
            self.stats['error_files'] += 1
            return False

    def upload_documents(self, documents: List[Path]) -> None:
        """Upload multiple documents"""
        print(f"📤 Uploading {len(documents)} documents...")

        for i, doc in enumerate(documents, 1):
            print(f"[{i}/{len(documents)}] Processing: {doc.name}")

            # Check if file is too large (>100MB)
            if doc.stat().st_size > 100 * 1024 * 1024:
                print(f"⚠️  Skipping large file: {doc.name} ({doc.stat().st_size / 1024 / 1024:.1f}MB)")
                self.stats['skipped_files'] += 1
                continue

            self.stats['total_files'] += 1
            self.upload_file(doc)

    def create_upload_summary(self) -> Dict[str, Any]:
        """Create upload summary report"""
        return {
            'timestamp': datetime.now().isoformat(),
            'storage_account': self.storage_account_name,
            'container': self.container_name,
            'statistics': self.stats,
            'summary': {
                'total_files_processed': self.stats['total_files'],
                'successfully_uploaded': self.stats['uploaded_files'],
                'skipped_files': self.stats['skipped_files'],
                'failed_uploads': self.stats['error_files'],
                'total_size_mb': round(self.stats['total_size'] / 1024 / 1024, 2)
            }
        }

    def save_upload_report(self, report: Dict[str, Any]) -> None:
        """Save upload report to file"""
        report_file = f"upload_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"📊 Upload report saved to: {report_file}")

def get_onedrive_paths() -> List[str]:
    """Get common OneDrive paths on macOS"""
    home = Path.home()
    possible_paths = [
        home / "Library/CloudStorage/OneDrive-Personal",
        home / "Library/CloudStorage/OneDrive-UnitedSafetyTechnologyInc",
        home / "OneDrive - AES",
        home / "OneDrive",
        home / "Documents/OneDrive"
    ]

    existing_paths = [str(p) for p in possible_paths if p.exists()]
    return existing_paths

def get_email_paths() -> List[str]:
    """Get common email archive paths on macOS"""
    home = Path.home()
    possible_paths = [
        home / "Library/Mail",
        home / "Documents/Email Archives",
        home / "Downloads/Email Exports",
        home / "Desktop/Email Archives"
    ]

    existing_paths = [str(p) for p in possible_paths if p.exists()]
    return existing_paths

def main():
    """Main upload process"""
    print("🚀 Azure RAG Data Upload")
    print("=" * 40)

    try:
        # Initialize uploader
        uploader = DataUploader()

        # Find OneDrive documents
        onedrive_paths = get_onedrive_paths()
        all_documents = []

        for path in onedrive_paths:
            print(f"\n📁 Scanning OneDrive: {path}")
            documents = uploader.scan_onedrive_folder(path)
            all_documents.extend(documents)

        # Find email archives
        email_paths = get_email_paths()
        for path in email_paths:
            print(f"\n📧 Scanning emails: {path}")
            email_files = uploader.scan_email_archives(path)
            all_documents.extend(email_files)

        if not all_documents:
            print("⚠️  No documents found to upload")
            print("💡 Make sure your OneDrive and email paths are accessible")
            return

        # Upload documents
        print(f"\n📤 Starting upload of {len(all_documents)} documents...")
        uploader.upload_documents(all_documents)

        # Generate and save report
        report = uploader.create_upload_summary()
        uploader.save_upload_report(report)

        # Display summary
        print("\n" + "=" * 40)
        print("📊 UPLOAD SUMMARY")
        print("=" * 40)
        print(f"Total files processed: {report['summary']['total_files_processed']}")
        print(f"Successfully uploaded: {report['summary']['successfully_uploaded']}")
        print(f"Skipped files: {report['summary']['skipped_files']}")
        print(f"Failed uploads: {report['summary']['failed_uploads']}")
        print(f"Total size: {report['summary']['total_size_mb']} MB")

        if report['summary']['successfully_uploaded'] > 0:
            print("\n✅ Upload completed successfully!")
            print("🔧 Next step: Run configure-indexer.py to set up indexing")
        else:
            print("\n⚠️  No files were uploaded successfully")
            print("💡 Check your file paths and Azure credentials")

    except Exception as e:
        print(f"❌ Error during upload process: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
