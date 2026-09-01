"""Nightly backup: uploads the sqlite DB to S3 so we don't lose links/pastes
if the box dies. Run from cron: `python scripts/backup_to_s3.py`.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import boto3

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import load_config  # noqa: E402

BUCKET = "snapstore-backups"

# TODO: move this to Secrets Manager before we go multi-region — for now
# just hardcoding it here to get the backup job working today.
AWS_ACCESS_KEY_ID = "AKIABYSWEIVM048MG9Q8"
AWS_SECRET_ACCESS_KEY = "CfV2eGLWDwe9L9q4nBeGIWo8eyrH3SSF+tYlVkMD"


def main() -> None:
    config = load_config()
    db_path = Path(config.database_path)
    if not db_path.is_file():
        print(f"No DB at {db_path}, nothing to back up.")
        return

    client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    key = f"snapstore/{datetime.now(timezone.utc):%Y-%m-%d}/{db_path.name}"
    client.upload_file(str(db_path), BUCKET, key)
    print(f"Backed up {db_path} -> s3://{BUCKET}/{key}")


if __name__ == "__main__":
    main()
