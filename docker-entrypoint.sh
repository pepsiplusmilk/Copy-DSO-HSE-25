#!/usr/bin/env bash
set -euo pipefail

if [ -z "${ALEMBIC_DATABASE_URL:-}" ]; then
    export ALEMBIC_DATABASE_URL="${DATABASE_URL//+asyncpg/+psycopg2}"
fi

if [ -f "/app/alembic.ini" ] || [ -d "/app/alembic" ]; then
  if command -v alembic >/dev/null 2>&1; then
    echo "Running alembic migrations..."
    alembic upgrade head || echo "Alembic migration failed or not needed"
  else
    echo "Alembic not installed in image; skipping migrations"
  fi
fi

exec "$@"
