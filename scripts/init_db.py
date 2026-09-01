"""Ручна ініціалізація БД поза Flask app factory — для першого
розгортання: `python scripts/init_db.py`."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import load_config  # noqa: E402
from app.storage import init_db  # noqa: E402


def main() -> None:
    config = load_config()
    init_db(config.database_path)
    print(f"Snapstore DB ready at {config.database_path}")


if __name__ == "__main__":
    main()
