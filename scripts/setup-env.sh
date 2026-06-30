#!/bin/bash
set -euo pipefail

echo "=== Setting up transcriptomics database ==="

DB_NAME="${TRANSCRIPTOMICS_DB:-transcriptomics}"
PG_USER="${POSTGRES_USER:-postgres}"
PG_PASSWORD="${POSTGRES_PASSWORD:-postgres}"
PG_HOST="${PG_HOST:-postgres}"

until pg_isready -h "$PG_HOST" -U "$PG_USER"; do
    echo "Waiting for PostgreSQL..."
    sleep 2
done

PGPASSWORD="$PG_PASSWORD" psql -h "$PG_HOST" -U "$PG_USER" -d postgres -tc \
    "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 ||
PGPASSWORD="$PG_PASSWORD" createdb -h "$PG_HOST" -U "$PG_USER" "$DB_NAME"

echo "Database '$DB_NAME' ready"

echo "=== Running Alembic migrations ==="
cd /app
alembic upgrade head

echo "=== Setup complete ==="
