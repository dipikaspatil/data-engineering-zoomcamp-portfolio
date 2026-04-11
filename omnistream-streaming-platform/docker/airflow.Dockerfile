# docker/airflow.Dockerfile
FROM apache/airflow:2.8.1-python3.11

USER root
# 1. Install system dependencies
RUN apt-get update && \
    apt-get install -y default-jdk libpq-dev postgresql-client git && \
    apt-get clean

# 2. Force the AIRFLOW_HOME and PATH for all users
ENV AIRFLOW_HOME=/opt/airflow
ENV PATH="${PATH}:/home/airflow/.local/bin:/usr/local/bin"

# 3. Copy entrypoint with correct permissions
COPY --chown=airflow:root entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER airflow

# 4. Install providers WITHOUT upgrading the core airflow version
# Using constraints ensures we don't accidentally pull Airflow 3.x
# Install Airflow providers WITH constraints
RUN pip install --no-cache-dir \
    "apache-airflow-providers-postgres" \
    "apache-airflow-providers-google" \
    "apache-airflow-providers-apache-flink" \
    "psycopg2-binary" \
    "confluent-kafka" \
    "flask-session" \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.8.1/constraints-3.11.txt"

# Install dbt separately WITHOUT constraints
RUN pip install --no-cache-dir dbt-bigquery==1.7.7

ENTRYPOINT ["/entrypoint.sh"]