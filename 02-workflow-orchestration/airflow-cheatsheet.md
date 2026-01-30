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

## Sample practice project
### Instructions
#### Step 1: Defining the DAG
Create a dag file check_dag.py. Then, define a DAG with the identifier check_dag.

We expect check_dag to run every day at midnight from the 1st of January 2025. 

Also, the DAG should have the following description "DAG to check data" and belongs to the data_engineering team.

#### Step 2: Creating the Tasks
We want to add three tasks to this DAG.

The first task executes the following Bash command: echo "Hi there!" >/tmp/dummy, to create a file dummy in the tmp directory with "Hi there!". The task's name should be create_file

Use the @task.bash decorator for Bash commands.

The second task executes the following  Bash command: test -f /tmp/dummy, to verify that the file dummy exists in the tmp directory. The task's name should be check_file

The third task executes the following Python function:

print(open('/tmp/dummy', 'rb').read())
to read and print on the standard output the content of the dummy file.

#### Step 3: Defining the dependencies
You should define the dependencies to get the order of execution:

create-file -> check_file_exists -> read_file

Finally, make sure that you have no errors by going to the Airflow UI. You should be able to see your DAG.