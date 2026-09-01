"""Конфігурація Snapstore: усе з env, нічого не хардкодиться в коді.
ADMIN_API_KEY/WEBHOOK_SECRET навмисно без дефолтів — відсутність .env
одразу видно (401/невалідний підпис), а не мовчки працює з дефолтним
паролем."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    database_path: str
    admin_api_key: str | None
    webhook_secret: str | None
    base_url: str


def load_config() -> Config:
    return Config(
        database_path=os.environ.get("SNAPSTORE_DB", "snapstore.db"),
        admin_api_key=os.environ.get("ADMIN_API_KEY"),
        webhook_secret=os.environ.get("WEBHOOK_SECRET"),
        base_url=os.environ.get("BASE_URL", "http://localhost:5000"),
    )
