#!/bin/bash

echo "🚀 Starting Omnistream Airflow Initialization..."

# 1. Install System Dependencies
apt-get update && apt-get install -y default-jdk gcc g++ sudo libpq-dev

# --- 2. SET GLOBAL JAVA PATHS ---
export JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:/bin/java::")
export PATH="$JAVA_HOME/bin:$PATH"

# --- 3. INSTALL DEPENDENCIES ---
echo "pip: Installing dependencies with official constraints..."

# Define the Airflow version and Python version for the constraints URL
AIRFLOW_VERSION=2.8.1
PYTHON_VERSION="$(python3 --version | cut -d " " -f 2 | cut -d "." -f 1-2)"
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

echo "pip: Installing dependencies..."
python3 -m pip install --upgrade pip

# Install Airflow using the constraints file + your project-specific extras
python3 -m pip install "apache-airflow[postgres,google,amazon]==${AIRFLOW_VERSION}" \
    --constraint "${CONSTRAINT_URL}" \
    psycopg2-binary \
    apache-flink==1.19.0 \
    confluent-kafka \
    flask-session  # Adding this explicitly just in case

# Ensure the local bin is in PATH so 'airflow' command works
export PATH=$PATH:/root/.local/bin

# Add this to ensure the root-installed binaries are accessible
chmod -R 755 /root/.local/bin

# --- 4. INITIALIZE & START ---
echo "Initializing Airflow DB..."
python3 -m airflow db migrate

echo "Creating Admin User..."
python3 -m airflow users create \
    --username admin \
    --firstname Omni \
    --lastname Stream \
    --role Admin \
    --email admin@omnistream.com \
    --password admin || true

# Fix ownership (silencing the read-only warning for the key)
chown -R airflow: /opt/airflow 2>/dev/null || true

echo "Starting Airflow services..."
python3 -m airflow scheduler &
exec python3 -m airflow webserver