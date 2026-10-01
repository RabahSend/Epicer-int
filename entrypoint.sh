#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
python - <<'PY'
import os
import time

import psycopg

host = os.environ.get("POSTGRES_HOST", "db")
port = os.environ.get("POSTGRES_PORT", "5432")
user = os.environ.get("POSTGRES_USER", "epicerint")
password = os.environ.get("POSTGRES_PASSWORD", "epicerint")
dbname = os.environ.get("POSTGRES_DB", "epicerint")

for attempt in range(30):
    try:
        with psycopg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=dbname,
            connect_timeout=3,
        ):
            print("PostgreSQL is ready.")
            break
    except Exception as exc:
        print(f"Attempt {attempt + 1}/30: {exc}")
        time.sleep(2)
else:
    raise SystemExit("PostgreSQL did not become ready in time.")
PY

python manage.py migrate --noinput

exec "$@"
