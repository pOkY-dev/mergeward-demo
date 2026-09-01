"""Flask app factory — create_app() читає Config (config.py) і реєструє
routes.py. Тести й scripts/init_db.py передають окремий database_path
(тимчасовий файл), щоб не чіпати реальний snapstore.db."""

from __future__ import annotations

from flask import Flask

from app.config import load_config
from app.routes import bp
from app.storage import init_db


def create_app(database_path: str | None = None) -> Flask:
    app = Flask(__name__)
    config = load_config()

    app.config["DATABASE_PATH"] = database_path or config.database_path
    app.config["ADMIN_API_KEY"] = config.admin_api_key
    app.config["WEBHOOK_SECRET"] = config.webhook_secret
    app.config["BASE_URL"] = config.base_url

    init_db(app.config["DATABASE_PATH"])
    app.register_blueprint(bp)
    return app
