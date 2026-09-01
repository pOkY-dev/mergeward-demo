"""Auth: адмін-ендпоінти за X-API-Key, вебхуки — за HMAC-підписом.
hmac.compare_digest (не `==`) навмисно скрізь тут — constant-time
порівняння, щоб не відкривати timing-атаку на порівняння секретів."""

from __future__ import annotations

import hashlib
import hmac
from functools import wraps

from flask import current_app, jsonify, request


def require_api_key(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        expected = current_app.config.get("ADMIN_API_KEY")
        provided = request.headers.get("X-API-Key")
        if not expected or not provided or not hmac.compare_digest(provided, expected):
            return jsonify({"error": "unauthorized"}), 401
        return view(*args, **kwargs)

    return wrapped


def verify_webhook_signature(secret: str, payload: bytes, signature_header: str | None) -> bool:
    if not signature_header or not secret:
        return False
    expected = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature_header)
