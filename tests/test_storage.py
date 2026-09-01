from __future__ import annotations

from app import storage


def test_create_and_get_link(tmp_path):
    db_path = str(tmp_path / "t.db")
    storage.init_db(db_path)
    storage.create_link(db_path, "abc123", "https://example.com")

    row = storage.get_link(db_path, "abc123")
    assert row["target_url"] == "https://example.com"


def test_get_link_increments_clicks(tmp_path):
    db_path = str(tmp_path / "t.db")
    storage.init_db(db_path)
    storage.create_link(db_path, "abc123", "https://example.com")

    storage.get_link(db_path, "abc123")
    storage.get_link(db_path, "abc123")

    with storage.connect(db_path) as conn:
        clicks = conn.execute(
            "SELECT clicks FROM links WHERE slug = ?", ("abc123",)
        ).fetchone()["clicks"]
    assert clicks == 2


def test_get_link_stats_does_not_increment_clicks(tmp_path):
    db_path = str(tmp_path / "t.db")
    storage.init_db(db_path)
    storage.create_link(db_path, "abc123", "https://example.com")

    storage.get_link(db_path, "abc123")  # one real click
    storage.get_link_stats(db_path, "abc123")
    storage.get_link_stats(db_path, "abc123")

    row = storage.get_link_stats(db_path, "abc123")
    assert row["clicks"] == 1


def test_slug_exists(tmp_path):
    db_path = str(tmp_path / "t.db")
    storage.init_db(db_path)
    assert storage.slug_exists(db_path, "nope") is False
    storage.create_link(db_path, "nope", "https://example.com")
    assert storage.slug_exists(db_path, "nope") is True


def test_create_and_get_paste(tmp_path):
    db_path = str(tmp_path / "t.db")
    storage.init_db(db_path)
    storage.create_paste(db_path, "p1", "hello world", "text")

    row = storage.get_paste(db_path, "p1")
    assert row["content"] == "hello world"
    assert row["syntax"] == "text"


def test_get_paste_missing_returns_none(tmp_path):
    db_path = str(tmp_path / "t.db")
    storage.init_db(db_path)
    assert storage.get_paste(db_path, "missing") is None
