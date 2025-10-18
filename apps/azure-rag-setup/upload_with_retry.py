#!/usr/bin/env python3
"""
Improved upload script with retry logic and progress tracking
Resolves timeout issues and enables resumable uploads
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from azure.storage.blob import BlobServiceClient
from tenacity import retry, stop_after_attempt, wait_exponential
from tqdm import tqdm
from logger import setup_logging
from config_manager import get_config_manager

# Initialize shared utilities
config = get_config_manager()
logger = setup_logging('upload-retry', level='INFO')


class ProgressTracker:
    """Track upload progress to enable resume capability"""

    def __init__(self, progress_file='upload_progress.json'):
        self.progress_file = Path(progress_file)
        self.uploaded = self._load()

    def _load(self) -> Dict[str, Any]:
        """Load progress from file"""
        if self.progress_file.exists():
            try:
                return json.loads(self.progress_file.read_text())
            except Exception:
                return {}
        return {}

    def is_uploaded(self, file_path: Path) -> bool:
        """Check if file was already uploaded"""
        key = str(file_path)
        if key not in self.uploaded:
            return False
        # Verify file hasn't changed since upload
        current_hash = self._file_hash(file_path)
        return self.uploaded[key].get('hash') == current_hash

    def mark_uploaded(self, file_path: Path, blob_name: str) -> None:
        """Mark file as uploaded"""
        self.uploaded[str(file_path)] = {
            'uploaded_at': datetime.now().isoformat(),
            'hash': self._file_hash(file_path),
            'size': file_path.stat().st_size,
            'blob_name': blob_name
        }
        self._save()

    def _file_hash(self, file_path: Path) -> str:
        """Quick hash of first and last 1KB for change detection"""
        try:
            with open(file_path, 'rb') as f:
                file_size = file_path.stat().st_size
                start = f.read(1024)
                if file_size > 1024:
                    f.seek(-min(1024, file_size), 2)
                    end = f.read(1024)
                else:
                    end = b''
            return hashlib.md5(start + end).hexdigest()
        except Exception:
            return ''

    def _save(self) -> None:
        """Save progress to file"""
        self.progress_file.write_text(json.dumps(self.uploaded, indent=2))


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    reraise=True
)
def upload_blob_with_retry(blob_client, file_path: Path) -> None:
    """Upload blob with exponential backoff retry"""
    with open(file_path, 'rb') as data:
        blob_client.upload_blob(
            data,
            overwrite=True,
            timeout=300,  # 5 minutes timeout
            connection_timeout=60  # 1 minute connection timeout
        )


class ImprovedUploader:
    """Improved document uploader with retry logic"""

    def __init__(self):
        self.storage_account_name = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
        self.storage_key = os.getenv('AZURE_STORAGE_ACCOUNT_KEY')
        self.container_name = os.getenv('AZURE_STORAGE_CONTAINER_NAME', 'training-data')

        # Use config manager for connection string
        try:
            connection_string = config.get_connection_string()
            self.blob_service = BlobServiceClient.from_connection_string(connection_string)
            self.container_client = self.blob_service.get_container_client(self.container_name)
        except Exception as e:
            logger.error(f"Failed to initialize Azure Storage: {e}")
            raise ValueError(f"Azure Storage credentials not found: {e}")

        # Initialize progress tracker
        self.tracker = ProgressTracker()

    def collect_files(self) -> List[Path]:
        """Collect all supported files from OneDrive locations"""
        print("📂 Scanning for files...")

        search_paths = [
            Path.home() / "Library/CloudStorage/OneDrive-Personal",
            Path.home() / "Library/CloudStorage/OneDrive-UnitedSafetyTechnologyInc",
        ]

        # Supported file extensions
        extensions = [
            # Documents
            '*.pdf', '*.PDF',
            '*.docx', '*.DOCX', '*.doc', '*.DOC',
            '*.txt', '*.TXT', '*.md', '*.MD', '*.rtf', '*.RTF',
            # Spreadsheets
            '*.xlsx', '*.XLSX', '*.xls', '*.XLS', '*.csv', '*.CSV',
            # Data
            '*.json', '*.JSON', '*.xml', '*.XML',
            # Email
            '*.msg', '*.MSG', '*.eml', '*.EML',
            # Web
            '*.html', '*.HTML', '*.htm', '*.HTM'
        ]

        all_files = []
        for path in search_paths:
            if path.exists():
                for ext in extensions:
                    all_files.extend(path.rglob(ext))

        # Remove duplicates
        all_files = list(set(all_files))

        print(f"   Found {len(all_files)} files")
        return all_files

    def filter_files(self, files: List[Path]) -> List[Path]:
        """Filter out already uploaded files"""
        files_to_upload = []
        for file in files:
            if not self.tracker.is_uploaded(file):
                files_to_upload.append(file)

        print(f"   Already uploaded: {len(files) - len(files_to_upload)}")
        print(f"   To upload: {len(files_to_upload)}")
        return files_to_upload

    def upload_file(self, file_path: Path) -> Dict[str, Any]:
        """Upload a single file with retry logic"""
        try:
            # Generate blob name
            blob_name = f"documents/{file_path.name}"
            blob_client = self.container_client.get_blob_client(blob_name)

            # Upload with retry
            upload_blob_with_retry(blob_client, file_path)

            # Mark as uploaded
            self.tracker.mark_uploaded(file_path, blob_name)

            return {
                'status': 'success',
                'file': str(file_path),
                'blob_name': blob_name,
                'size': file_path.stat().st_size
            }
        except Exception as e:
            return {
                'status': 'failed',
                'file': str(file_path),
                'error': str(e)
            }

    def upload_all(self, files: List[Path]) -> Dict[str, Any]:
        """Upload all files with progress tracking"""
        stats = {
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'total_size': 0,
            'failed_files': []
        }

        if not files:
            print("✅ No files to upload")
            return stats

        print(f"\n📤 Uploading {len(files)} files...")

        # Upload with progress bar
        for file in tqdm(files, desc="Uploading", unit="file"):
            result = self.upload_file(file)

            if result['status'] == 'success':
                stats['success'] += 1
                stats['total_size'] += result['size']
            else:
                stats['failed'] += 1
                stats['failed_files'].append({
                    'file': result['file'],
                    'error': result['error']
                })
                tqdm.write(f"❌ Failed: {file.name}: {result['error']}")

        return stats

    def generate_report(self, stats: Dict[str, Any]) -> None:
        """Generate upload report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"upload_report_{timestamp}.json"

        report = {
            'timestamp': datetime.now().isoformat(),
            'statistics': stats,
            'success_rate': f"{stats['success'] / max(stats['success'] + stats['failed'], 1) * 100:.1f}%",
            'total_size_mb': f"{stats['total_size'] / 1024 / 1024:.2f}"
        }

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📊 Upload Report:")
        print(f"   Success: {stats['success']}")
        print(f"   Failed: {stats['failed']}")
        print(f"   Success Rate: {report['success_rate']}")
        print(f"   Total Size: {report['total_size_mb']} MB")
        print(f"   Report saved to: {report_file}")

        if stats['failed'] > 0:
            print(f"\n⚠️  Failed files: {stats['failed']}")
            for failure in stats['failed_files'][:5]:  # Show first 5
                print(f"   - {Path(failure['file']).name}: {failure['error']}")


def main():
    """Main upload process"""
    print("🚀 Azure RAG - Improved Document Upload")
    print("=" * 50)

    try:
        # Initialize uploader
        uploader = ImprovedUploader()

        # Collect files
        all_files = uploader.collect_files()

        if not all_files:
            print("❌ No files found in OneDrive locations")
            return 1

        # Filter already uploaded
        files_to_upload = uploader.filter_files(all_files)

        if not files_to_upload:
            print("✅ All files are already uploaded")
            return 0

        # Upload files
        stats = uploader.upload_all(files_to_upload)

        # Generate report
        uploader.generate_report(stats)

        # Return status
        if stats['failed'] == 0:
            print("\n✅ Upload completed successfully!")
            return 0
        elif stats['success'] > 0:
            print(f"\n⚠️  Upload completed with {stats['failed']} failures")
            return 0
        else:
            print("\n❌ Upload failed")
            return 1

    except Exception as e:
        print(f"❌ Error during upload: {e}")
        return 1


if __name__ == "__main__":
    exit(main())

