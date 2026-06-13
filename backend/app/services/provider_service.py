"""
Provider Service — Cryptographic key handling (BYOK) and credentials utility.
"""

import base64
import logging
from cryptography.fernet import Fernet
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ProviderService:
    """Manages encryption and decryption of provider credentials."""

    def __init__(self) -> None:
        key = settings.encryption_key
        # Fernet requires a 32-byte base64-encoded key.
        # Ensure we have a valid key format, falling back to a deterministic derivation or generated key if invalid.
        try:
            # Check if it's already a valid Fernet key
            base64.urlsafe_b64decode(key.encode())
            if len(base64.urlsafe_b64decode(key.encode())) == 32:
                self.fernet = Fernet(key.encode())
            else:
                raise ValueError("Key must be 32 bytes")
        except Exception:
            # Fallback: Hash or pad key to fit 32 bytes base64 requirement
            padded = key.ljust(32)[:32].encode()
            b64_key = base64.urlsafe_b64encode(padded)
            self.fernet = Fernet(b64_key)

    def encrypt_key(self, raw_key: str) -> str:
        """Encrypt API key for database storage."""
        if not raw_key:
            return ""
        return self.fernet.encrypt(raw_key.encode()).decode()

    def decrypt_key(self, encrypted_key: str) -> str:
        """Decrypt database API key back into plain text."""
        if not encrypted_key:
            return ""
        try:
            return self.fernet.decrypt(encrypted_key.encode()).decode()
        except Exception as e:
            logger.error(f"Failed to decrypt provider API key: {e}")
            return ""


_provider_service: ProviderService | None = None


def get_provider_service() -> ProviderService:
    """Singleton getter for ProviderService."""
    global _provider_service
    if _provider_service is None:
        _provider_service = ProviderService()
    return _provider_service
