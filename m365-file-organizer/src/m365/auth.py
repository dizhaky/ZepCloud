from __future__ import annotations

import asyncio
from typing import Optional

from azure.identity.aio import DeviceCodeCredential
from loguru import logger

from config.settings import settings


class M365Auth:
    """Azure AD authentication for Microsoft Graph using device code flow.

    Note: For web flows (authorization code), integrate with FastAPI later.
    """

    def __init__(self) -> None:
        self._credential: Optional[DeviceCodeCredential] = None

    async def _get_credential(self) -> DeviceCodeCredential:
        if self._credential is None:
            logger.info("Initializing DeviceCodeCredential for Azure AD")
            self._credential = DeviceCodeCredential(
                client_id=settings.azure_client_id,
                tenant_id=settings.azure_tenant_id,
                prompt_callback=lambda dc: logger.info(
                    "To sign in, use code {user_code} at {verification_uri}",
                    user_code=dc["user_code"],
                    verification_uri=dc["verification_uri"]
                ),
            )
        return self._credential

    async def get_access_token(self) -> str:
        """Acquire an access token for Microsoft Graph."""
        credential = await self._get_credential()
        token = await credential.get_token("https://graph.microsoft.com/.default")
        return token.token

    async def validate_token(self) -> bool:
        try:
            token = await self.get_access_token()
            valid = bool(token and len(token) > 0)
            logger.debug("Token validation result: {}", valid)
            return valid
        except Exception as exc:  # pragma: no cover - network/interactive
            logger.error("Token validation failed: {}", exc)
            return False

    async def close(self) -> None:
        if self._credential is not None:
            await self._credential.close()
            self._credential = None
