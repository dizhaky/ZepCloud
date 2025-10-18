"""
Document processing utilities integrating OlmoCR and RAG-Anything
"""
import requests
import logging
from config_elasticsearch import Config
import mimetypes
from typing import Dict, Any, Optional
from .olmocr_processor import OlmoCRProcessor
from .raganything_processor import RAGAnythingProcessor

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Process documents for indexing with OlmoCR and RAG-Anything integration"""

    def __init__(self):
        self.tika_url = f"{Config.TIKA_HOST}/tika"
        self.olmocr_processor = OlmoCRProcessor()
        self.raganything_processor = RAGAnythingProcessor()

    def extract_text(self, file_content: bytes, mime_type: str, file_name: str = "") -> Dict[str, Any]:
        """
        Extract text from document using Apache Tika or OlmoCR

        Args:
            file_content: File content as bytes
            mime_type: MIME type of the file
            file_name: Name of the file

        Returns:
            Dictionary with extracted content and metadata
        """
        result = {
            "content": "",
            "multimodal_content": {},
            "processing_method": "tika",
            "error": None
        }

        # Try OlmoCR first for PDFs and images
        if self.olmocr_processor.enabled and self._should_use_olmocr(mime_type):
            try:
                olmocr_result = self.olmocr_processor.process_document(file_name, file_content, mime_type)
                if olmocr_result.get("content"):
                    result.update(olmocr_result)
                    return result
            except Exception as e:
                logger.warning(f"OlmoCR processing failed, falling back to Tika: {e}")

        # Fall back to Tika for other files or if OlmoCR fails
        try:
            result["content"] = self._extract_with_tika(file_content, mime_type)
            result["processing_method"] = "tika"
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            result["error"] = str(e)

        return result

    def _should_use_olmocr(self, mime_type: str) -> bool:
        """Determine if file should be processed with OlmoCR"""
        olmocr_types = [
            "application/pdf",
            "image/jpeg",
            "image/png",
            "image/tiff",
            "image/bmp"
        ]
        return mime_type in olmocr_types

    def _extract_with_tika(self, file_content: bytes, mime_type: str) -> str:
        """Extract text using Apache Tika"""
        if not Config.ENABLE_OCR:
            return ""

        try:
            headers = {
                'Content-Type': mime_type or 'application/octet-stream',
                'Accept': 'text/plain'
            }

            response = requests.put(
                self.tika_url,
                data=file_content,
                headers=headers,
                timeout=60
            )

            if response.status_code == 200:
                text = response.text.strip()
                logger.debug(f"Extracted {len(text)} characters with Tika")
                return text
            else:
                logger.warning(f"Tika returned status {response.status_code}")
                return ""

        except requests.exceptions.Timeout:
            logger.warning("Tika request timed out")
            return ""
        except Exception as e:
            logger.error(f"Tika text extraction failed: {e}")
            return ""

    def should_process_file(self, file_name: str, file_size: int, modified_date=None) -> bool:
        """Determine if file should be processed"""

        # Check file size
        if file_size > Config.MAX_FILE_SIZE_BYTES:
            logger.debug(f"Skipping {file_name}: too large ({file_size} bytes)")
            return False

        # Check file extension
        if Config.FILE_TYPE_FILTER_ENABLED:
            ext = '.' + file_name.rsplit('.', 1)[-1].lower() if '.' in file_name else ''
            if ext in Config.EXCLUDED_FILE_EXTENSIONS:
                logger.debug(f"Skipping {file_name}: excluded extension {ext}")
                return False

        # Check modified date
        if Config.DATE_FILTER_ENABLED and modified_date:
            date_filter = Config.get_date_filter()
            if date_filter and modified_date < date_filter:
                logger.debug(f"Skipping {file_name}: too old ({modified_date})")
                return False

        return True

    def extract_metadata(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Extract common metadata from M365 item"""
        return {
            'file_name': item.get('name', ''),
            'file_size': item.get('size', 0),
            'file_type': item.get('file', {}).get('mimeType', ''),
            'file_extension': self._get_extension(item.get('name', '')),
            'created_date': item.get('createdDateTime'),
            'modified_date': item.get('lastModifiedDateTime'),
            'created_by': self._get_user_name(item.get('createdBy')),
            'modified_by': self._get_user_name(item.get('lastModifiedBy')),
            'url': item.get('webUrl', ''),
            'web_url': item.get('webUrl', '')
        }

    def process_document_with_rag_anything(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Process document with RAG-Anything for enhanced features"""
        return self.raganything_processor.process_document(document)

    def _get_extension(self, filename: str) -> str:
        """Get file extension"""
        return '.' + filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

    def _get_user_name(self, user_obj: Dict[str, Any]) -> str:
        """Extract user display name from Graph API user object"""
        if not user_obj:
            return ''
        user = user_obj.get('user', {})
        return user.get('displayName', user.get('email', ''))

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics from all processors"""
        return {
            "olmocr": self.olmocr_processor.get_processing_stats(),
            "raganything": self.raganything_processor.get_processing_stats(),
            "tika_enabled": Config.ENABLE_OCR,
            "date_filter_enabled": Config.DATE_FILTER_ENABLED,
            "max_file_size_mb": Config.MAX_FILE_SIZE_MB
        }
