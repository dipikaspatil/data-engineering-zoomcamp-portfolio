"""
Simple Airflow DAG to demonstrate:
1. Running Bash commands
2. Task dependencies
3. Mixing Bash and Python operators
"""

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime


# Python function to read and print the contents of the file
def read_file():
    """
    Reads the file created by the Bash task
    and prints its contents to the task logs.
    """
    with open("/tmp/dummy", "r") as f:
        print(f.read())


# Define the DAG and its configuration
with DAG(
    dag_id="check_dag",
    start_date=datetime(2026, 1, 1),   # DAG will not run before this date
    schedule="@daily",                 # Run once per day
    catchup=False,                     # Do not backfill missed runs
    description="DAG to check data using Bash and Python tasks",
    tags=["data_engineering"],
) as dag:

    # Task 1: Create a file using a Bash command
    create_file = BashOperator(
        task_id="create_file",
        bash_command='echo "Hi there!" > /tmp/dummy',
    )

    # Task 2: Verify that the file exists
    # The task fails if the file does not exist
    check_file = BashOperator(
        task_id="check_file_exists",
        bash_command="test -f /tmp/dummy",
    )

    # Task 3: Read and print the file contents using Python
    read_file_task = PythonOperator(
        task_id="read_file",
        python_callable=read_file,
    )

    # Define task execution order
    # create_file → check_file_exists → read_file
    create_file >> check_file >> read_file_task
