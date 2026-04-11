#!/bin/bash
set -e

echo "Waiting for Postgres..."
export PGPASSWORD="$POSTGRES_PASSWORD"

# Wait for DB
until pg_isready -h postgres -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do
  echo "Postgres is unavailable - sleeping"
  sleep 2
done

echo "Postgres is up! Initializing Airflow 2.8.1..."

# 1. Initialize Database
airflow db migrate

# 2. Create Admin
echo "Creating Admin User..."
airflow users create \
    --username admin \
    --firstname Omni \
    --lastname Stream \
    --role Admin \
    --email admin@omnistream.com \
    --password admin || true

echo "Starting Airflow..."
exec airflow standalone