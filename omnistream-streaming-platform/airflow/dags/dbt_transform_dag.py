from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator


default_args = {
    "owner": "omnistream",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="omnistream_dbt_transform",
    default_args=default_args,
    description="Run dbt models for OmniStream",
    start_date=datetime(2026, 4, 3),
    schedule="*/15 * * * *",
    catchup=False,
    tags=["omnistream", "dbt", "bigquery"],
) as dag:

    dbt_debug = BashOperator(
        task_id="dbt_debug",
        bash_command="""
        cd /opt/airflow/dbt && \
        dbt debug --profiles-dir /opt/airflow/dbt
        """,
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="""
        cd /opt/airflow/dbt && \
        dbt run --profiles-dir /opt/airflow/dbt
        """,
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="""
        cd /opt/airflow/dbt && \
        dbt test --profiles-dir /opt/airflow/dbt
        """,
    )

    dbt_debug >> dbt_run >> dbt_test