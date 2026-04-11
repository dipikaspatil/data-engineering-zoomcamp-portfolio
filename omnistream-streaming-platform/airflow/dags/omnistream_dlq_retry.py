from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from google.cloud import bigquery, storage
from confluent_kafka import Producer
from airflow.models import Variable
import json
import os

PROJECT_ID = Variable.get("GCP_PROJECT_ID")
DATASET = "omnistream_staging"
TABLE = "dlq_control"
BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "redpanda:9092")

def fetch_retryable(**context):
    client = bigquery.Client(project=PROJECT_ID)
    query = f"""
    SELECT dlqId, sourceTopic, recordType, payloadGcsPath, retryCount, maxRetries
    FROM `{PROJECT_ID}.{DATASET}.{TABLE}`
    WHERE status = 'RETRYABLE'
      AND errorClassification = 'TRANSIENT'
      AND retryCount < maxRetries
      AND TIMESTAMP_MILLIS(nextRetryAt) <= CURRENT_TIMESTAMP()
    ORDER BY nextRetryAt
    LIMIT 100
    """
    rows = list(client.query(query).result())
    context["ti"].xcom_push(key="retry_rows", value=[dict(r.items()) for r in rows])

def publish_retries(**context):
    rows = context["ti"].xcom_pull(key="retry_rows")
    if not rows:
        return

    producer = Producer({"bootstrap.servers": BOOTSTRAP})
    storage_client = storage.Client(project=PROJECT_ID)

    for row in rows:
        topic = {
            "geo": "retry_geo_data",
            "finance": "retry_finance_data",
            "aviation": "retry_aviation_data",
        }.get(row["recordType"])

        if not topic:
            continue

        gcs_path = row["payloadGcsPath"]
        if not gcs_path:
            continue

        # payloadGcsPath is now a prefix/folder, not a full object name
        _, _, remainder = gcs_path.partition("gs://")
        bucket_name, _, prefix = remainder.partition("/")

        blobs = list(storage_client.list_blobs(bucket_name, prefix=prefix))
        if not blobs:
            raise Exception(f"No files found for prefix: {gcs_path}")

        # We expect exactly one file in this folder
        blob = blobs[0]
        dlq_json = blob.download_as_text()

        # GCS stores full DlqRecord JSON; publish only the original raw payload
        dlq_record = json.loads(dlq_json)
        raw_payload = dlq_record.get("rawPayload")

        if not raw_payload:
            raise Exception(f"rawPayload missing in DLQ object: {blob.name}")

        producer.produce(topic, raw_payload.encode("utf-8"))

    producer.flush()

def mark_retried(**context):
    rows = context["ti"].xcom_pull(key="retry_rows")
    if not rows:
        return

    client = bigquery.Client(project=PROJECT_ID)
    updates = []
    for row in rows:
        updates.append(f"""
        UPDATE `{PROJECT_ID}.{DATASET}.{TABLE}`
        SET retryCount = retryCount + 1,
            lastRetriedAt = UNIX_MILLIS(CURRENT_TIMESTAMP()),
            nextRetryAt = UNIX_MILLIS(TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)),
            status = 'RETRIED'
        WHERE dlqId = '{row["dlqId"]}'
        """)

    for stmt in updates:
        client.query(stmt).result()

with DAG(
    dag_id="omnistream_dlq_retry",
    start_date=datetime(2026, 3, 31),
    schedule="*/30 * * * *",
    catchup=False,
    default_args={"retries": 1, "retry_delay": timedelta(minutes=5)},
) as dag:
    t1 = PythonOperator(task_id="fetch_retryable", python_callable=fetch_retryable)
    t2 = PythonOperator(task_id="publish_retries", python_callable=publish_retries)
    t3 = PythonOperator(task_id="mark_retried", python_callable=mark_retried)

    t1 >> t2 >> t3