from __future__ import annotations

import pytest

from app import create_app


@pytest.fixture
def client(tmp_path):
    db_path = str(tmp_path / "test.db")
    app = create_app(database_path=db_path)
    app.config["TESTING"] = True
    app.config["ADMIN_API_KEY"] = "test-admin-key"
    with app.test_client() as client:
        yield client


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_create_and_follow_link(client):
    resp = client.post("/api/links", json={"url": "https://example.com"})
    assert resp.status_code == 201
    slug = resp.get_json()["slug"]

    follow = client.get(f"/{slug}", follow_redirects=False)
    assert follow.status_code == 302
    assert follow.headers["Location"] == "https://example.com"


def test_create_link_rejects_invalid_url(client):
    resp = client.post("/api/links", json={"url": "not-a-url"})
    assert resp.status_code == 400


def test_create_link_rejects_duplicate_slug(client):
    client.post("/api/links", json={"url": "https://example.com", "slug": "mine"})
    resp = client.post("/api/links", json={"url": "https://example.org", "slug": "mine"})
    assert resp.status_code == 409


def test_unknown_slug_404(client):
    resp = client.get("/does-not-exist")
    assert resp.status_code == 404


def test_create_and_view_paste(client):
    resp = client.post("/api/pastes", json={"content": "print('hi')", "syntax": "python"})
    assert resp.status_code == 201
    paste_id = resp.get_json()["id"]

    view = client.get(f"/p/{paste_id}")
    assert view.status_code == 200
    assert view.get_json()["content"] == "print('hi')"


def test_paste_requires_content(client):
    resp = client.post("/api/pastes", json={"content": "  "})
    assert resp.status_code == 400


def test_paste_rejects_oversized_content(client):
    resp = client.post("/api/pastes", json={"content": "x" * 100_001})
    assert resp.status_code == 413


def test_admin_stats_requires_api_key(client):
    resp = client.get("/api/admin/stats")
    assert resp.status_code == 401

    resp_ok = client.get("/api/admin/stats", headers={"X-API-Key": "test-admin-key"})
    assert resp_ok.status_code == 200
    assert resp_ok.get_json() == {"links": 0, "pastes": 0}


def test_admin_stats_rejects_wrong_key(client):
    resp = client.get("/api/admin/stats", headers={"X-API-Key": "wrong"})
    assert resp.status_code == 401


def test_deploy_webhook_rejects_missing_signature(client):
    resp = client.post("/api/webhooks/deploy", json={"event": "deploy"})
    assert resp.status_code == 401
