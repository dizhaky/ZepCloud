from __future__ import annotations

from io import BytesIO
from typing import Tuple

from loguru import logger
import magic  # type: ignore
from PyPDF2 import PdfReader  # type: ignore
from docx import Document as DocxDocument  # type: ignore

from .graph_client import GraphClient


SUPPORTED_MIME_PREFIXES = (
    "text/plain",
    "text/csv",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
)


def extract_text_from_file(content: bytes, mime_type: str) -> str:
    """Extract plaintext from common file types: PDF, DOCX, TXT, CSV.

    Returns an empty string on unsupported types or extraction failure.
    """
    try:
        if not mime_type or mime_type == "application/octet-stream":
            detected = magic.Magic(mime=True).from_buffer(content)
            mime_type = detected or mime_type
    except Exception as exc:  # pragma: no cover - lib specific
        logger.warning("MIME detection failed: {}", exc)

    try:
        if mime_type.startswith("text/plain") or mime_type.startswith("text/csv"):
            return content.decode("utf-8", errors="replace")
        if mime_type.startswith("application/pdf"):
            text_parts = []
            reader = PdfReader(BytesIO(content))
            for page in reader.pages:
                text_parts.append(page.extract_text() or "")
            return "\n".join(text_parts).strip()
        if mime_type.startswith(
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ):
            doc = DocxDocument(BytesIO(content))
            return "\n".join(p.text for p in doc.paragraphs)
    except Exception as exc:  # pragma: no cover - file specific
        logger.error("Text extraction failed: {}", exc)
        return ""

    logger.debug("Unsupported MIME type for extraction: {}", mime_type)
    return ""


async def download_file(graph: GraphClient, drive_id: str, file_id: str) -> Tuple[bytes, str]:
    """Download file content and return (content, mime_type)."""
    meta = await graph.get_file_metadata(drive_id, file_id)
    content = await graph.get_file_content(drive_id, file_id)
    mime_type = meta.get("file", {}).get("mimeType") or meta.get("@microsoft.graph.downloadUrl", "application/octet-stream")
    return content, mime_type


async def apply_organization(
    graph: GraphClient,
    drive_id: str,
    file_id: str,
    new_name: str,
    new_path: str,
) -> bool:
    """Rename and/or move a file in M365 under the given drive."""
    renamed = await graph.update_file_name(drive_id, file_id, new_name)
    moved = await graph.move_file(drive_id, file_id, new_path, new_name=new_name)
    return renamed and moved
