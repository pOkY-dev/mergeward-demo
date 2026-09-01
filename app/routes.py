"""HTTP-ендпоінти Snapstore: короткі посилання + pastebin. Тонкий шар над
storage.py/utils.py/security.py — без бізнес-логіки тут, лише
парсинг запиту/HTTP-статуси."""

from __future__ import annotations

from flask import Blueprint, abort, current_app, jsonify, redirect, request

from app import storage
from app.security import require_api_key, verify_webhook_signature
from app.utils import generate_paste_id, generate_slug, is_valid_url

bp = Blueprint("snapstore", __name__)


@bp.get("/health")
def health():
    return jsonify({"status": "ok"})


@bp.post("/api/links")
def create_link():
    data = request.get_json(silent=True) or {}
    target_url = data.get("url", "").strip()
    if not is_valid_url(target_url):
        return jsonify({"error": "invalid url"}), 400

    db_path = current_app.config["DATABASE_PATH"]
    slug = data.get("slug") or generate_slug()
    if storage.slug_exists(db_path, slug):
        return jsonify({"error": "slug already taken"}), 409

    storage.create_link(db_path, slug, target_url)
    return jsonify({"slug": slug, "url": f"{current_app.config['BASE_URL']}/{slug}"}), 201


@bp.get("/<slug>")
def follow_link(slug: str):
    db_path = current_app.config["DATABASE_PATH"]
    row = storage.get_link(db_path, slug)
    if row is None:
        abort(404)
    return redirect(row["target_url"], code=302)


@bp.post("/api/pastes")
def create_paste():
    data = request.get_json(silent=True) or {}
    content = data.get("content", "")
    if not content.strip():
        return jsonify({"error": "content required"}), 400
    if len(content) > 100_000:
        return jsonify({"error": "content too large"}), 413

    syntax = data.get("syntax", "text")
    db_path = current_app.config["DATABASE_PATH"]
    paste_id = generate_paste_id()
    storage.create_paste(db_path, paste_id, content, syntax)
    return jsonify({"id": paste_id}), 201


@bp.get("/p/<paste_id>")
def view_paste(paste_id: str):
    db_path = current_app.config["DATABASE_PATH"]
    row = storage.get_paste(db_path, paste_id)
    if row is None:
        abort(404)
    return jsonify({"id": row["id"], "content": row["content"], "syntax": row["syntax"]})


@bp.get("/api/admin/stats")
@require_api_key
def admin_stats():
    # Мінімальна адмін-ручка — досить, щоб продемонструвати
    # require_api_key, не претендує на повну адмінку.
    db_path = current_app.config["DATABASE_PATH"]
    with storage.connect(db_path) as conn:
        links = conn.execute("SELECT COUNT(*) AS n FROM links").fetchone()["n"]
        pastes = conn.execute("SELECT COUNT(*) AS n FROM pastes").fetchone()["n"]
    return jsonify({"links": links, "pastes": pastes})


@bp.post("/api/webhooks/deploy")
def deploy_webhook():
    secret = current_app.config.get("WEBHOOK_SECRET")
    signature = request.headers.get("X-Hub-Signature-256")
    if not verify_webhook_signature(secret or "", request.get_data(), signature):
        return jsonify({"error": "invalid signature"}), 401
    # Реальний деплой-хук навмисно НЕ виконує жодних shell-команд тут —
    # просто підтверджує прийом підпису. Будь-яка майбутня "запусти
    # скрипт після деплою"-фіча — свідомо гарне місце для перевірки
    # mergeward на реальному PR (Р8/heuristics: curl|sh, shell=True тощо).
    return jsonify({"status": "accepted"}), 202
