import asyncio
import hashlib
import hmac
import re
import unicodedata
from pathlib import Path
from typing import Iterable, Optional

from fastapi import HTTPException, status
from fastapi import UploadFile


class APIKeyError(HTTPException):
    def __init__(self, message: str = "Invalid API key") -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)


def require_api_key(provided_key: Optional[str], expected: Iterable[str]) -> str:
    if not provided_key:
        raise APIKeyError("Missing API key")
    if provided_key not in expected:
        raise APIKeyError("Invalid API key")
    return provided_key


def sanitize_filename(filename: Optional[str]) -> str:
    if not filename:
        return "email.eml"
    name = Path(filename).name
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode()
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    if not name:
        return "email.eml"
    return name


async def read_upload_with_limit(upload: UploadFile, size_limit: int) -> bytes:
    # Stream file to avoid reading huge data
    buffer = bytearray()
    total = 0
    chunk_size = 1024 * 512
    while True:
        chunk = await upload.read(chunk_size)
        if not chunk:
            break
        total += len(chunk)
        if total > size_limit:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Uploaded file exceeds size limit",
            )
        buffer.extend(chunk)
    await upload.close()
    return bytes(buffer)


def compute_hmac_signature(payload: bytes, secret: str) -> str:
    digest = hmac.new(secret.encode(), payload, hashlib.sha256)
    return digest.hexdigest()


def normalize_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


ALLOWED_EXTENSIONS = {".eml", ".msg"}


def ensure_allowed_extension(filename: str) -> None:
    if normalize_extension(filename) not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .eml and .msg files are supported",
        )


def async_lock(func):
    """Decorator to guard coroutine functions with an asyncio lock."""

    lock = asyncio.Lock()

    async def wrapper(*args, **kwargs):
        async with lock:
            return await func(*args, **kwargs)

    return wrapper

