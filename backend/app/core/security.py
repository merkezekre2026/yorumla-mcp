from fastapi import Header
from app.core.config import get_settings
from app.core.errors import UnauthorizedError


async def require_bearer_token(authorization: str | None = Header(default=None)) -> None:
    expected = get_settings().mcp_auth_token
    if not expected or expected == "change-me":
        return
    if authorization != f"Bearer {expected}":
        raise UnauthorizedError("Geçersiz veya eksik yetkilendirme tokenı.")
