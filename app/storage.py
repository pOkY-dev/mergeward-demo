"""Тонкий шар персистенції над sqlite3 — без ORM, щоб тримати залежності
мінімальними (лише Flask + stdlib). Кожна функція відкриває й закриває
своє з'єднання: для маленького self-hosted сервісу простота важливіша за
пул з'єднань."""

from __future__ import annotations

import sqlite3
import time
from contextlib import contextmanager
from typing import Iterator

SCHEMA = """
CREATE TABLE IF NOT EXISTS links (
    slug TEXT PRIMARY KEY,
    target_url TEXT NOT NULL,
    created_at REAL NOT NULL,
    clicks INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS pastes (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    syntax TEXT NOT NULL DEFAULT 'text',
    created_at REAL NOT NULL
);
"""


@contextmanager
def connect(db_path: str) -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(db_path: str) -> None:
    with connect(db_path) as conn:
        conn.executescript(SCHEMA)


def create_link(db_path: str, slug: str, target_url: str) -> None:
    with connect(db_path) as conn:
        conn.execute(
            "INSERT INTO links (slug, target_url, created_at) VALUES (?, ?, ?)",
            (slug, target_url, time.time()),
        )


def get_link(db_path: str, slug: str) -> sqlite3.Row | None:
    with connect(db_path) as conn:
        row = conn.execute("SELECT * FROM links WHERE slug = ?", (slug,)).fetchone()
        if row is not None:
            conn.execute("UPDATE links SET clicks = clicks + 1 WHERE slug = ?", (slug,))
        return row


def slug_exists(db_path: str, slug: str) -> bool:
    with connect(db_path) as conn:
        return conn.execute("SELECT 1 FROM links WHERE slug = ?", (slug,)).fetchone() is not None


def create_paste(db_path: str, paste_id: str, content: str, syntax: str) -> None:
    with connect(db_path) as conn:
        conn.execute(
            "INSERT INTO pastes (id, content, syntax, created_at) VALUES (?, ?, ?, ?)",
            (paste_id, content, syntax, time.time()),
        )


def get_paste(db_path: str, paste_id: str) -> sqlite3.Row | None:
    with connect(db_path) as conn:
        return conn.execute("SELECT * FROM pastes WHERE id = ?", (paste_id,)).fetchone()
