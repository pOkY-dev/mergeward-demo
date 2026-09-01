from __future__ import annotations

import hashlib
import hmac

from app.security import verify_webhook_signature


def test_verify_webhook_signature_accepts_correct_signature():
    secret = "s3cr3t"
    payload = b'{"event": "deploy"}'
    digest = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    header = f"sha256={digest}"

    assert verify_webhook_signature(secret, payload, header) is True


def test_verify_webhook_signature_rejects_wrong_signature():
    assert verify_webhook_signature("s3cr3t", b"payload", "sha256=deadbeef") is False


def test_verify_webhook_signature_rejects_missing_header():
    assert verify_webhook_signature("s3cr3t", b"payload", None) is False


def test_verify_webhook_signature_rejects_missing_secret():
    assert verify_webhook_signature("", b"payload", "sha256=deadbeef") is False
