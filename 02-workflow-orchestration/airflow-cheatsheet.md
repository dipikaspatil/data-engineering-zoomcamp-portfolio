> Created while learning Apache Airflow as part of Data Engineering Zoomcamp

## What is Airflow ?

Airflow is a workflow orchestration tool.

In simple terms 👇
Airflow helps you define, schedule, and monitor data pipelines.

### ✅ Define workflows as code

You write pipelines in Python.

```python
extract >> transform >> load
```

This is called a DAG (Directed Acyclic Graph).

### ✅ Schedule workflows

Example:

every day at 6 AM

every hour

on demand

### ✅ Handle dependencies

Task B waits for Task A

Task C runs only if A & B succeed

### ✅ Monitor & retry

See failures in UI

Retry failed tasks automatically

Get logs per task

## Key Airflow Concepts (Very Important)

| Term       | Meaning                                  |
|------------|------------------------------------------|
| DAG        | Workflow definition                      |
| Task       | One unit of work                         |
| Operator   | How a task runs (Python, Bash, SQL, etc.)|
| Scheduler  | Decides when tasks run                  |
| Executor   | Decides how tasks run                   |
| Web UI     | Monitor everything                      |


## 1️⃣ DAG (Directed Acyclic Graph)
What it is

A DAG is the workflow itself.

- Defined in Python
- Describes tasks + their order
- “Acyclic” = no loops (task can’t depend on itself)

Mental model

🧠 Blueprint of your pipeline
```text
Extract → Transform → Load
```

Example - 
```python
with DAG("etl_pipeline") as dag:
    ...
```

👉 Airflow does not run the DAG file line-by-line
It reads it and schedules tasks from it.

## 2️⃣ Task
What it is

A task is a single unit of work inside a DAG.

Examples:

- Run a SQL query
- Call an API
- Run a Python function
- Execute a Bash command

Key points

- Atomic (do one thing)
- Can succeed / fail / retry independently
- Each task = one node in the DAG

Mental model

🧠 One step in the workflow

```text
Download data
```

## 3️⃣ Operator

What it is

An Operator defines HOW a task runs.

A task = instance of an operator

Common operators

## Airflow Operators

| Operator           | Use                     |
|-------------------|------------------------|
| `PythonOperator`   | Run Python function     |
| `BashOperator`     | Run shell command       |
| `PostgresOperator` | Run SQL                 |
| `DockerOperator`   | Run Docker container    |
| `EmptyOperator`    | Dummy / dependency only |

Example

```python
PythonOperator(
    task_id="clean_data",
    python_callable=clean_fn
)
```

Mental model

🧠 The tool used to perform the task

4️⃣ Sensor
What it is

A Sensor is a special type of operator
that waits for something to happen.

Examples

- Wait for a file to arrive
- Wait for a table to exist
- Wait for another DAG to finish

Example

```python
FileSensor(
    task_id="wait_for_file",
    filepath="/data/input.csv"
)
```

Important behavior

- Keeps checking (“polling”)
- Can block resources if misused

Mental model

🧠 A door guard waiting for permission

```text
“Don’t start until X exists”
```

## 5️⃣ Scheduler
What it is

The Scheduler decides WHEN tasks should run.

It:

- Scans DAGs
- Checks schedules
- Checks dependencies
- Sends runnable tasks to the executor

Example logic

```text
Is it 6 AM?
Are upstream tasks successful?
→ Yes → schedule task
```

Mental model

🧠 Air traffic controller

## DAG basics (example snippet)

### 1. What is a DAG?

A DAG (Directed Acyclic Graph) is the core concept in Airflow. It defines the workflow: what tasks to run and in which order.

- Directed: The tasks have a defined order.
- Acyclic: There are no loops; tasks don’t repeat in a cycle.
- Graph: Represents tasks as nodes and dependencies as edges.

### 2. DAG Components

- DAG: The workflow container.
- Task: A unit of work (like running a Python function or Bash command).
- Operator: Defines what a task does (PythonOperator, BashOperator, etc.).
- Dependencies: Define the order of execution (task1 >> task2).

### 3. Example DAG

#### 1 - Traditional DAG

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

# 1. Define a Python function for the task
def say_hello():
    print("Hello Airflow!")

# 2. Define the DAG
with DAG(
    dag_id="example_hello_dag",
    start_date=datetime(2026, 1, 1),
    schedule_interval="@daily",  # runs daily
    catchup=False,               # don't backfill
    tags=["example"]
) as dag:

    # 3. Define tasks
    task1 = PythonOperator(
        task_id="say_hello_task",
        python_callable=say_hello
    )

    task2 = PythonOperator(
        task_id="say_hello_again_task",
        python_callable=lambda: print("Hello again!")
    )

    # 4. Set task dependencies
    task1 >> task2  # task2 runs after task1
```
Explanation

- dag_id: Unique identifier for the DAG.
- start_date: When the DAG starts scheduling.
- schedule_interval: How often to run (@daily, @hourly, cron format, etc.).
- catchup: If False, Airflow won’t run past missed intervals.
- PythonOperator: Runs a Python function as a task.
- task1 >> task2: Defines task dependencies.

#### 2 - Using the @dag decorator (Preferred)

```python
from airflow.decorators import dag, task
from datetime import datetime

# 1. Define the DAG with a decorator
@dag(
    dag_id="decorator_example_dag",
    start_date=datetime(2026, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["example"]
)
def my_decorator_dag():

    # 2. Define tasks using the @task decorator
    @task
    def task1():
        print("Hello from Task 1")
        return "Task 1 finished"

    @task
    def task2(msg):
        print(f"Task 2 received: {msg}")
        return "Task 2 finished"

    @task
    def task3(msg):
        print(f"Task 3 received: {msg}")

    # 3. Set dependencies using Python variables
    t1_result = task1()
    t2_result = task2(t1_result)
    task3(t2_result)

# 4. Instantiate the DAG
dag = my_decorator_dag()

```

Explanation

- @dag decorator replaces the traditional with DAG(...) as dag: block.
- @task decorator replaces PythonOperator, making it simpler to define tasks as Python functions.
- Task dependencies are defined naturally by function calls:
```python
t1_result = task1()
t2_result = task2(t1_result)  # task2 runs after task1
task3(t2_result)              # task3 runs after task2
```
- The DAG is instantiated at the end with:
```python
dag = my_decorator_dag()
```

✅  Tip - Data can be passed between tasks (e.g., msg)—this is called XCom under the hood.

## Upstream / Downstream

### 1. Concept

In Airflow, tasks have dependencies:

- Upstream task: Must run before the current task.

- Downstream task: Runs after the current task.

Think of it as a flow of data/work:

```text
task1 → task2 → task3
```

- task1 is upstream of task2
- task2 is downstream of task1
- task2 is upstream of task3
- task3 is downstream of task2

### 2. Setting Dependencies

There are two main ways:

#### a) Using >> and << operators

```python
task1 >> task2  # task1 is upstream of task2
task3 << task2  # task2 is upstream of task3 (same as task2 >> task3)
```

#### b) Using set_upstream() and set_downstream()

```python
task2.set_upstream(task1)      # task1 runs before task2
task2.set_downstream(task3)    # task3 runs after task2
```

### 3. Example 

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def task_fn(name):
    print(f"Running {name}")

with DAG("upstream_downstream_dag",
         start_date=datetime(2026,1,1),
         schedule_interval="@daily",
         catchup=False) as dag:

    task1 = PythonOperator(
        task_id="task1",
        python_callable=lambda: task_fn("task1")
    )
    task2 = PythonOperator(
        task_id="task2",
        python_callable=lambda: task_fn("task2")
    )
    task3 = PythonOperator(
        task_id="task3",
        python_callable=lambda: task_fn("task3")
    )

    # Set dependencies
    task1 >> task2 >> task3
```


Explanation:

- task1 → upstream of task2, downstream of nothing
- task2 → downstream of task1, upstream of task3
- task3 → downstream of task2, upstream of nothing




✅ Tip

You can check upstream/downstream tasks programmatically:

```python
print(task2.upstream_task_ids)  # {'task1'}
print(task2.downstream_task_ids)  # {'task3'}
```

This is super useful for dynamic DAGs or debugging.

## default arguments

default_args is a dictionary of default parameters that you can pass to your DAG.

These defaults apply to all tasks in the DAG unless a task overrides them.

Helps avoid repetition and ensures consistency.

Common use cases:

- owner: Who “owns” the DAG/task
- depends_on_past: Whether task depends on previous run
- retries: How many times to retry on failure
- retry_delay: Time between retries
- email / email_on_failure: Notifications

```python
from airflow.decorators import dag, task
from datetime import datetime, timedelta

# 1. Default arguments (applied to all tasks)
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email": ["team@example.com"],
    "email_on_failure": True
}

# 2. Define the DAG using the @dag decorator
@dag(
    dag_id="full_example_decorator_dag",
    start_date=datetime(2026, 1, 1),
    schedule_interval="@daily",
    default_args=default_args,
    catchup=False,
    tags=["example"]
)
def full_example_dag():

    # 3. Task 1
    @task
    def task1():
        print("Hello from Task 1")
        return "Task 1 finished"

    # 4. Task 2 (depends on Task 1)
    @task
    def task2(msg):
        print(f"Task 2 received: {msg}")
        return "Task 2 finished"

    # 5. Task 3 (depends on Task 2)
    @task
    def task3(msg):
        print(f"Task 3 received: {msg}")

    # 6. Task 4 (demonstrate upstream/downstream relationships)
    @task
    def task4():
        print("Task 4 can run in parallel with Task 2")
        return "Task 4 finished"

    # --- Set dependencies ---
    t1_result = task1()          # Task 1 runs first
    t2_result = task2(t1_result) # Task 2 runs after Task 1
   

    t4_result = task4()          # Task 4 runs independently, can start anytime like task1. Can execute parallel to task 1
    t3_result = task3([t2_result, t4_result]) # task3 depends on both task2 and task4

# 7. Instantiate the DAG
dag = full_example_dag()

```

## Chain

### 1. What is airflow.models.base.BaseOperator.chain()?

- chain is a utility function that lets you link multiple tasks together in order without writing multiple >> statements.

- Useful when you have a long linear sequence of tasks or when you want to connect multiple tasks dynamically.

### 2. How chain works

- Each argument is treated as a step in the DAG.
- If an argument is a list of tasks, every task in the previous step connects to every task in the current step.

### 3. Example

- a → [b, d]
- This means:

```css
a → b
a → d
```

- chain(a, [b, d], [c, e])

```css
a → b
a → d
b → c
b → e
d → c
d → e
```

- Root task - a
- Intermediate tasks - [b, d]
- Leaf tasks: [c, e]
- Parallelism:
    - b and d can run simultaneously.
    - c and e also can run in parallel, but must wait for upstream tasks.

#### What happens when you trigger the DAG in UI

- DAG Run starts → a executes first.
- Once a succeeds → b and d are scheduled in parallel.
- Once b and d succeed → c and e scheduled in parallel.
- DAG completes when c and e succeed.

#### Graph view 

```css
        a
      /   \
     b     d
    / \   / \
   c   e c   e
```

### Syntax
```python
from airflow.models.base import chain

chain(task1, [task2, task3], task4)
```

## XCOMs (Cross-Communication)

### What are XComs?

- XCom = Cross-Communication.
- Mechanism to pass small amounts of data between tasks in a DAG.
- Stored in Airflow's metadata database.
- Only suitable for lightweight data (strings, numbers, JSON).
- ⚠️ Avoid large files or dataframes — use storage like S3, GCS, or DB instead.

### How to use XComs

#### 1. Push data

- From a PythonOperator / @task-decorated function:

```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(start_date=datetime(2026,1,1), schedule="@daily", catchup=False)
def xcom_example():

    @task
    def push_data():
        return "Hello XCom"  # Auto-pushed when using @task

    push_data()
```

- Using xcom_push in traditional PythonOperator:
```python
from airflow.operators.python import PythonOperator

def my_func(ti):
    ti.xcom_push(key='message', value='Hello XCom')

task = PythonOperator(
    task_id='push_task',
    python_callable=my_func
)
```

#### 2. Pull data

- From a PythonOperator / @task function:

```python
@task
def pull_data(ti):
    msg = ti.xcom_pull(task_ids='push_data')  # Pulls return value of push_data
    print(msg)  # Output: Hello XCom
```

- Using xcom_pull in traditional PythonOperator:

```python
def pull_func(ti):
    msg = ti.xcom_pull(task_ids='push_task', key='message')
    print(msg)
```

### List XComs:

```bash
airflow tasks xcom_pull <dag_id> <task_id>
airflow tasks xcom_list <dag_id>
```

### Example using XCOM

```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(start_date=datetime(2026,1,1), schedule="@daily", catchup=False)
def xcom_dag():

    @task
    def push():
        return {"count": 10}

    @task
    def pull(data):
        print(f"Received data: {data}")

    pull(push())

xcom_dag()
```

- Output in logs:
```logs
Received data: {'count': 10}
```

## Sensor

### What are Sensors?

- Sensors are special Airflow operators that wait for a condition to be met.
- They keep checking (“poke”) until:
    - the condition is true ✅
    - or they timeout ❌
- Common use cases:
    - Wait for a file to arrive
    - Wait for a table/partition
    - Wait for another DAG/task

### Key Sensor Concepts

#### Airflow Sensor Parameters

| Term              | Meaning                                                |
|-------------------|--------------------------------------------------------|
| **poke_interval** | How often (in seconds) the sensor checks the condition |
| **timeout**       | Max time (in seconds) to wait before failing           |
| **mode**          | How the sensor runs (`poke` or `reschedule`)           |
| **soft_fail**     | Mark task as SKIPPED instead of FAILED on timeout      |

### Sensor Modes (Important!)

#### 1. poke (default)
- Sensor occupies a worker slot while waiting
- Simple but inefficient for long waits

```python
mode="poke"
```

#### 2. reschedule (recommended)
- Sensor releases worker slot between checks
- Best practice for production

```python
mode="reschedule"
```

✅ Always prefer reschedule unless you have a good reason

### Commonly Used Sensors

#### 1. FileSensor

Wait for a file to exist.

```python
from airflow.sensors.filesystem import FileSensor

wait_for_file = FileSensor(
    task_id="wait_for_file",
    filepath="/tmp/data.csv",
    poke_interval=30,
    timeout=300,
    mode="reschedule"
)
```

#### 2. ExternalTaskSensor

Wait for a task in another DAG.

```python
from airflow.sensors.external_task import ExternalTaskSensor

wait_for_upstream = ExternalTaskSensor(
    task_id="wait_for_external_task",
    external_dag_id="upstream_dag",
    external_task_id="task_a",
    poke_interval=60,
    timeout=600,
    mode="reschedule"
)
```

#### 3. TimeSensor

Wait until a specific time of day.

```python
from airflow.sensors.time_sensor import TimeSensor
from datetime import time

wait_until_6am = TimeSensor(
    task_id="wait_until_6am",
    target_time=time(6, 0, 0)
)
```

#### 4. SQL Sensor

Wait for a condition in a database.

```python
from airflow.providers.postgres.sensors.postgres import PostgresSensor

wait_for_data = PostgresSensor(
    task_id="wait_for_data",
    postgres_conn_id="postgres_default",
    sql="SELECT 1 FROM my_table LIMIT 1",
    poke_interval=60,
    timeout=300,
    mode="reschedule"
)
```

#### 5. Custom Python Sensor

Use your own logic.

```python
from airflow.sensors.base import BaseSensorOperator

class MySensor(BaseSensorOperator):
    def poke(self, context):
        return True  # condition met
```

## Best Practices

- ✅ Use mode="reschedule"
- ✅ Keep poke_interval reasonable
- ❌ Don’t use sensors for heavy computation
- ❌ Don’t wait on large data movement

## When NOT to use Sensors

- Long waits → use event-driven pipelines
- Waiting on large files → use storage + metadata checks
- High-frequency polling → consider Deferrable Sensors

## Deferrable Sensors (Advanced)

- Introduced to reduce resource usage
- Use async triggers
- Ideal for cloud-scale pipelines

## Sensors vs Triggers

`Sensors wait for conditions using polling, while triggers enable event-driven async execution via deferrable operators that don’t occupy workers.`

Mental Model (Easy to Remember)

🕒 Sensor → “Are we there yet?” (keeps asking)

🔔 Trigger → “Ring me when it’s ready” (gets notified)

High-level Difference
| Feature        | Sensors              | Triggers                       |
| -------------- | -------------------- | ------------------------------ |
| Purpose        | Wait for a condition | Power async / deferrable tasks |
| Introduced     | Early Airflow        | Airflow 2.x                    |
| Execution      | Polling              | Event-driven                   |
| Resource usage | Can be heavy         | Very lightweight               |
| Runs where     | Worker               | Triggerer process              |

### Sensors
- What they do
    - Sensors poll repeatedly until a condition is met
    - Example conditions:
        - File exists
        - Table has rows
        - Another DAG finishes

- How they work
    - Check condition every poke_interval
    - Stop when condition is true or timeout occurs

```python
FileSensor(
    task_id="wait_for_file",
    filepath="/tmp/data.csv",
    mode="reschedule"
)
```

#### Pros

✅ Simple

✅ Easy to understand

✅ Great for short waits


#### Cons

❌ Polling based

❌ Can still be inefficient

❌ Poor choice for long waits

### Triggers
- What they do
    - Triggers enable async waiting
    - Used internally by Deferrable Operators
    - Wake tasks only when an event occurs

- How they work
    1. Task defers itself
    2. Trigger runs asynchronously
    3. Trigger fires → task resumes

🧠 No polling, no worker usage

#### Where Triggers Run

| Component     | Role                              |
| ------------- | --------------------------------- |
| **Triggerer** | Runs trigger logic                |
| **Scheduler** | Resumes deferred task             |
| **Worker**    | Executes task after trigger fires |


#### Triggers Example (Conceptual)

```python
class MyTrigger(BaseTrigger):
    async def run(self):
        while not condition_met:
            await asyncio.sleep(30)
        yield TriggerEvent(True)
```

⚠️ Triggers are not used directly in DAGs
They are used by deferrable operators

## Deferrable Sensors (Best of both worlds)

| Classic Sensor | Deferrable Sensor |
| -------------- | ----------------- |
| Polling        | Event-driven      |
| Uses worker    | Uses triggerer    |
| Slower         | Scales better     |


```python
FileSensor(
    task_id="wait_for_file",
    filepath="/tmp/data.csv",
    deferrable=True
)
```

## Airflow CLI (Docker / docker-compose) 🐳

Assumes:

- You are using docker-compose
- Airflow services like airflow-webserver, airflow-scheduler
- Airflow home: /opt/airflow

#### 1. Basic Docker-Compose Commands

Start Airflow (foreground logs)
```bash
docker-compose up
```

Start Airflow (background)
```bash
docker-compose up -d
```

Stop services
```bash
docker-compose down
```

Stop + remove volumes (⚠️ deletes metadata DB)
```bash
docker-compose down -v
```

#### 2. Run Airflow CLI Commands (One-off)

Use docker-compose run for CLI commands

Check Airflow version

```bash
docker-compose run --rm airflow-webserver airflow version
```

List DAGs
```bash
docker-compose run --rm airflow-webserver airflow dags list
```

List DAG tasks
```bash
docker-compose run --rm airflow-webserver airflow tasks list <dag_id>
```

Show DAG details
```bash
docker-compose run --rm airflow-webserver airflow dags show <dag_id>
```

#### 3. Trigger & Manage DAG Runs

Trigger DAG manually
```bash
docker-compose run --rm airflow-webserver airflow dags trigger <dag_id>
```

Pause a DAG
```bash
docker-compose run --rm airflow-webserver airflow dags pause <dag_id>
```

Unpause a DAG
```bash
docker-compose run --rm airflow-webserver airflow dags unpause <dag_id>
```

#### 4. Task-Level Commands

Run a task manually (debugging)
```bash
docker-compose run --rm airflow-webserver \
  airflow tasks run <dag_id> <task_id> 2026-01-01
```

Clear task instances
```bash
docker-compose run --rm airflow-webserver \
  airflow tasks clear <dag_id>
```

#### 5. Logs & Debugging

View service logs
```bash
docker-compose logs airflow-webserver
docker-compose logs airflow-scheduler
```

Follow logs
```bash
docker-compose logs -f airflow-scheduler
```

#### 6. Exec into a Running Container

Enter webserver container
```bash
docker-compose exec airflow-webserver bash
```

Enter scheduler container
```bash
docker-compose exec airflow-scheduler bash
```

📌 Useful for:

Inspecting /opt/airflow/dags

Checking /tmp

Debugging files & configs

#### 7. Inspect DAGs Folder Inside Container
```bash
docker-compose exec airflow-webserver ls -l /opt/airflow/dags
```

#### 8. Database & Metadata

Initialize metadata DB
```bash
docker-compose run --rm airflow-webserver airflow db migrate
```

Check DB status
```bash
docker-compose run --rm airflow-webserver airflow db check
```

#### 9. User Management

Create admin user
```bash
docker-compose run --rm airflow-webserver airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com
```

List users
```bash
docker-compose run --rm airflow-webserver airflow users list
```

#### 10. Variables & Connections

List variables
```bash
docker-compose run --rm airflow-webserver airflow variables list
```

Set variable
```bash
docker-compose run --rm airflow-webserver \
  airflow variables set ENV dev
```

List connections
```bash
docker-compose run --rm airflow-webserver airflow connections list
```

#### 11. Advanced / Power User

Open Python shell inside container
```bash
docker-compose exec airflow-webserver python
```

Check Airflow config
```bash
docker-compose run --rm airflow-webserver airflow config list
```

#### Debugging & Local Testing

Test a Single Airflow Task (No Scheduler)
```bash
docker-compose run --rm airflow-webserver \
  airflow tasks test <dag_id> <task_id> <execution_date>

# Example
docker-compose run --rm airflow-webserver \
  airflow tasks test check_dag read_file 2026-01-29
```

To identify DAG import or parsing errors after an Airflow upgrade, use `airflow dags list-import-errors`, which reports Python exceptions preventing DAGs from loading.
```bash
docker-compose run --rm airflow-webserver \
  airflow dags list-import-errors
```

## 🔗 Connections & Variables

### 1️⃣ Connections
Connections are Airflow’s way to store credentials and endpoints (databases, APIs, cloud services).

List connections
```bash
docker-compose run --rm airflow-webserver airflow connections list
```

Add a connection
```bash
docker-compose run --rm airflow-webserver \
  airflow connections add 'my_postgres' \
  --conn-type 'postgres' \
  --conn-host 'postgres' \
  --conn-login 'airflow' \
  --conn-password 'airflow' \
  --conn-schema 'airflow' \
  --conn-port 5432

```

Get a connection
```bash
docker-compose run --rm airflow-webserver \
airflow connections get my_postgres
```

Delete a connection
```bash
docker-compose run --rm airflow-webserver \
airflow connections delete my_postgres
```

Connections are stored in Airflow metadata DB, accessible in the UI under Admin → Connections.

### 2️⃣ Variables
Variables are key-value pairs stored in Airflow metadata DB, useful for runtime parameters.

List all variables
```bash
docker-compose run --rm airflow-webserver airflow variables list
```

Get a variable
```bash
docker-compose run --rm airflow-webserver airflow variables get my_var
```

Use --default to avoid errors if it’s missing:
```bash
docker-compose run --rm airflow-webserver airflow variables get my_var --default 'default_value'
```

Set a variable
```bash
docker-compose run --rm airflow-webserver airflow variables set my_var '42'
```

Delete a variable
```bash
docker-compose run --rm airflow-webserver airflow variables delete my_var
```

### Export / Import variables

Export all variables to JSON:
```bash
docker-compose run --rm airflow-webserver airflow variables export /tmp/variables.json
```

Import variables from JSON:
```bash
docker-compose run --rm airflow-webserver airflow variables import /tmp/variables.json
```

#### Notes / Tips

- Connections → credentials / endpoints
- Variables → runtime parameters / config values
- Both are stored in Airflow metadata DB and can be managed via CLI, UI, or API



