import base64
import hashlib
import hmac
import os
import time

from .config import settings


def now_ts() -> int:
    return int(time.time())


def b64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))


def sign_payload(payload: str) -> str:
    return hmac.new(settings.session_secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()


def make_session(username: str) -> str:
    expires = now_ts() + settings.session_ttl_seconds
    nonce = b64url_encode(os.urandom(12))
    payload = f"{username}|{expires}|{nonce}"
    return f"{b64url_encode(payload.encode('utf-8'))}.{sign_payload(payload)}"


def verify_session(token: str | None) -> str | None:
    if not token or "." not in token or not settings.session_secret:
        return None
    encoded, signature = token.rsplit(".", 1)
    try:
        payload = b64url_decode(encoded).decode("utf-8")
    except Exception:
        return None
    if not hmac.compare_digest(signature, sign_payload(payload)):
        return None
    parts = payload.split("|")
    if len(parts) != 3:
        return None
    username, expires, _nonce = parts
    try:
        if int(expires) < now_ts():
            return None
    except ValueError:
        return None
    if username != settings.username:
        return None
    return username


def verify_password(username: str, password: str) -> bool:
    if username != settings.username or not settings.password_sha256:
        return False
    digest = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return hmac.compare_digest(digest, settings.password_sha256)
