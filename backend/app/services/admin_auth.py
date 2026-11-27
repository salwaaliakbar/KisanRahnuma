"""Admin login: one shared operator password, not per-user accounts.

A token is a signed, stateless "<expiry-unix-ts>.<hmac-hex>" string (same HMAC-SHA256 +
constant-time-compare style as `consent_service.hash_external_ref` and
`whatsapp_webhook.signature_is_valid`) - no server-side session table needed.
"""
import hashlib
import hmac
import time

from fastapi import Depends, Header, HTTPException

from app.core.config import Settings, get_settings


def _sign(expires_at: int, secret: str) -> str:
    return hmac.new(secret.encode(), str(expires_at).encode(), hashlib.sha256).hexdigest()


def issue_token(settings: Settings) -> tuple[str, int]:
    expires_at = int(time.time()) + settings.admin_token_ttl_minutes * 60
    token = f"{expires_at}.{_sign(expires_at, settings.admin_token_secret)}"
    return token, expires_at


def token_is_valid(token: str, settings: Settings) -> bool:
    expires_at_raw, _, signature = token.partition(".")
    if not expires_at_raw.isdigit() or not signature:
        return False
    expires_at = int(expires_at_raw)
    if expires_at < int(time.time()):
        return False
    return hmac.compare_digest(signature, _sign(expires_at, settings.admin_token_secret))


def password_is_valid(password: str, settings: Settings) -> bool:
    return bool(settings.admin_password) and hmac.compare_digest(password, settings.admin_password)


def require_admin(authorization: str = Header(""), settings: Settings = Depends(get_settings)) -> None:
    """FastAPI dependency: 401s unless a valid "Bearer <token>" header is present."""
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token or not token_is_valid(token, settings):
        raise HTTPException(status_code=401, detail="Admin login required")
