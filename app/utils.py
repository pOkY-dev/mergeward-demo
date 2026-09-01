"""Валідація й генерація slug'ів/id — окремо від routes.py, щоб можна
було юніт-тестувати без Flask test client."""

from __future__ import annotations

import secrets
import string
from urllib.parse import urlparse

_SLUG_ALPHABET = string.ascii_lowercase + string.digits
_ALLOWED_SCHEMES = {"http", "https"}


def generate_slug(length: int = 7) -> str:
    return "".join(secrets.choice(_SLUG_ALPHABET) for _ in range(length))


def generate_paste_id(length: int = 10) -> str:
    return "".join(secrets.choice(_SLUG_ALPHABET) for _ in range(length))


def is_valid_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    return parsed.scheme in _ALLOWED_SCHEMES and bool(parsed.netloc)
