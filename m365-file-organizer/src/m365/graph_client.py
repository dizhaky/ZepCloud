from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx
from loguru import logger
from tenacity import (RetryCallState, retry, retry_if_exception_type,
                      stop_after_attempt, wait_exponential)

from config.settings import settings
from .auth import M365Auth

GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"


class M365Error(Exception):
    """Raised for Microsoft 365/Graph related failures."""


@dataclass
class GraphClientConfig:
    timeout_seconds: float = 30.0
    max_retries: int = 3


def _before_sleep_log(retry_state: RetryCallState) -> None:
    exc = retry_state.outcome.exception() if retry_state.outcome else None
    logger.warning(
        "Retrying Graph call (attempt {}), error: {}",
        retry_state.attempt_number,
        exc,
    )


def retryable():
    return retry(
        reraise=True,
        stop=stop_after_attempt(GraphClientConfig.max_retries if hasattr(GraphClientConfig, 'max_retries') else 3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(M365Error),
        before_sleep=_before_sleep_log,
    )


class GraphClient:
    """Lightweight async wrapper around Microsoft Graph REST endpoints.

    We use httpx with bearer tokens from Device Code flow. This keeps
    the client fully async and lets us implement precise retry handling.
    """

    def __init__(self, auth: Optional[M365Auth] = None, *, timeout_seconds: float = 30.0) -> None:
        self._auth = auth or M365Auth()
        self._client: Optional[httpx.AsyncClient] = None
        self._timeout = timeout_seconds

    async def __aenter__(self) -> "GraphClient":
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    async def _ensure_client(self) -> None:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self._timeout)

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _headers(self) -> Dict[str, str]:
        token = await self._auth.get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

    async def _handle_response(self, resp: httpx.Response) -> Any:
        if resp.status_code == 429:
            # Surface as retryable
            retry_after = resp.headers.get("Retry-After")
            logger.warning("Graph 429 rate limit; Retry-After={} seconds", retry_after)
            raise M365Error(f"Rate limited: {resp.text}")
        if resp.is_success:
            if resp.headers.get("Content-Type", "").startswith("application/json"):
                return resp.json()
            return resp.content
        text = resp.text
        logger.error("Graph call failed: {} {} -> {}", resp.request.method, resp.request.url, resp.status_code)
        raise M365Error(f"Graph error {resp.status_code}: {text}")

    @retryable()
    async def default_drive_id(self) -> str:
        await self._ensure_client()
        assert self._client is not None
        headers = await self._headers()
        resp = await self._client.get(f"{GRAPH_BASE_URL}/me/drive", headers=headers)
        data = await self._handle_response(resp)
        return data.get("id")

    @retryable()
    async def list_drives(self) -> List[Dict[str, Any]]:
        await self._ensure_client()
        assert self._client is not None
        headers = await self._headers()
        resp = await self._client.get(f"{GRAPH_BASE_URL}/me/drives", headers=headers)
        data = await self._handle_response(resp)
        return data.get("value", [])

    @retryable()
    async def list_files(self, drive_id: str, folder_path: Optional[str] = None) -> List[Dict[str, Any]]:
        await self._ensure_client()
        assert self._client is not None
        headers = await self._headers()
        if folder_path:
            url = f"{GRAPH_BASE_URL}/drives/{drive_id}/root:/{folder_path}:/children"
        else:
            url = f"{GRAPH_BASE_URL}/drives/{drive_id}/root/children"
        resp = await self._client.get(url, headers=headers)
        data = await self._handle_response(resp)
        return data.get("value", [])

    @retryable()
    async def get_file_content(self, drive_id: str, file_id: str) -> bytes:
        await self._ensure_client()
        assert self._client is not None
        headers = await self._headers()
        url = f"{GRAPH_BASE_URL}/drives/{drive_id}/items/{file_id}/content"
        resp = await self._client.get(url, headers=headers)
        content = await self._handle_response(resp)
        assert isinstance(content, (bytes, bytearray))
        return bytes(content)

    @retryable()
    async def get_file_metadata(self, drive_id: str, file_id: str) -> Dict[str, Any]:
        await self._ensure_client()
        assert self._client is not None
        headers = await self._headers()
        url = f"{GRAPH_BASE_URL}/drives/{drive_id}/items/{file_id}"
        resp = await self._client.get(url, headers=headers)
        data = await self._handle_response(resp)
        assert isinstance(data, dict)
        return data

    @retryable()
    async def update_file_name(self, drive_id: str, file_id: str, new_name: str) -> bool:
        await self._ensure_client()
        assert self._client is not None
        headers = await self._headers()
        headers["Content-Type"] = "application/json"
        url = f"{GRAPH_BASE_URL}/drives/{drive_id}/items/{file_id}"
        payload = {"name": new_name}
        resp = await self._client.patch(url, headers=headers, json=payload)
        _ = await self._handle_response(resp)
        return True

    @retryable()
    async def move_file(self, drive_id: str, file_id: str, new_path: str, new_name: Optional[str] = None) -> bool:
        """Move the file under a new folder path. Optionally rename."""
        await self._ensure_client()
        assert self._client is not None
        headers = await self._headers()
        headers["Content-Type"] = "application/json"
        url = f"{GRAPH_BASE_URL}/drives/{drive_id}/items/{file_id}"
        parent_ref = {"path": f"/drive/root:{'/' if not new_path.startswith('/') else ''}{new_path}"}
        payload: Dict[str, Any] = {"parentReference": parent_ref}
        if new_name:
            payload["name"] = new_name
        resp = await self._client.patch(url, headers=headers, json=payload)
        _ = await self._handle_response(resp)
        return True

    @retryable()
    async def search_files(self, query: str, drive_id: Optional[str] = None) -> List[Dict[str, Any]]:
        await self._ensure_client()
        assert self._client is not None
        headers = await self._headers()
        if drive_id:
            url = f"{GRAPH_BASE_URL}/drives/{drive_id}/root/search(q='{query}')"
        else:
            url = f"{GRAPH_BASE_URL}/me/drive/root/search(q='{query}')"
        resp = await self._client.get(url, headers=headers)
        data = await self._handle_response(resp)
        return data.get("value", [])
