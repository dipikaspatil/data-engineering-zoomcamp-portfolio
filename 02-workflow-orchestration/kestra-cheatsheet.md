# Kestra Cheatsheet 🚀



---

## 🧠 Mental Model (Airflow ➜ Kestra)

* DAG (Python) ➜ Flow (YAML)
* Operator ➜ Task / Plugin
* Scheduler‑centric ➜ Event‑driven by default
* XComs ➜ Inputs & Outputs

## 🆚 Airflow Mapping (Quick)

| Airflow     | Kestra       |
| ----------- | ------------ |
| DAG         | Flow         |
| Operator    | Task         |
| XCom        | Outputs      |
| Python only | Any language |
| Scheduler   | Triggers     |

Based on Video series of Zoomcamp for Kestra - 
https://www.youtube.com/playlist?list=PLEK3H8YwZn1p-pCYj46rRhA0HcdXXxzzP


## What is Kestra? Data Engineering Zoomcamp - 2.1.2

👉 Definition

Kestra is an open-source workflow orchestration tool.

It lets you define and run data pipelines and workflows using a declarative `YAML` format — similar to other orchestrators but with a UI and event-driven features.

| Concept | Brief note                                                      |
| ----------- | ------------------------------------------------------------------- |
| Kestra      | Orchestrator for workflows/pipelines (YAML + UI)
| YAML flows  | Like DAGs but declarative
| Tasks       | Units of work orchestration executes
| Triggers    | Cron or event-based 
| UI          | Built-in for dashboards/logs

## Installing Kestra: Data Engineering Zoomcamp - 2.2.1

```yaml
volumes:
  ny_taxi_postgres_data:
    driver: local
  kestra_postgres_data:
    driver: local
  kestra_data:
    driver: local

services:
  pgdatabase:
    image: postgres:18
    environment:
      POSTGRES_USER: root
      POSTGRES_PASSWORD: root
      POSTGRES_DB: ny_taxi
    ports:
      - "5432:5432"
    volumes:
      - ny_taxi_postgres_data:/var/lib/postgresql
    depends_on:
      kestra:
        condition: service_started

  pgadmin:
    image: dpage/pgadmin4
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@admin.com
      - PGADMIN_DEFAULT_PASSWORD=root
    ports:
      - "8085:80"
    depends_on:
      pgdatabase:
        condition: service_started

  kestra_postgres:
    image: postgres:18
    volumes:
      - kestra_postgres_data:/var/lib/postgresql
    environment:
      POSTGRES_DB: kestra
      POSTGRES_USER: kestra
      POSTGRES_PASSWORD: k3str4
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -d $${POSTGRES_DB} -U $${POSTGRES_USER}"]
      interval: 30s
      timeout: 10s
      retries: 10

  kestra:
    image: kestra/kestra:v1.1
    pull_policy: always
    # Note that this setup with a root user is intended for development purpose.
    # Our base image runs without root, but the Docker Compose implementation needs root to access the Docker socket
    # To run Kestra in a rootless mode in production, see: https://kestra.io/docs/installation/podman-compose
    user: "root"
    command: server standalone
    volumes:
      - kestra_data:/app/storage
      - /var/run/docker.sock:/var/run/docker.sock
      - /tmp/kestra-wd:/tmp/kestra-wd
    environment:
      KESTRA_CONFIGURATION: |
        datasources:
          postgres:
            url: jdbc:postgresql://kestra_postgres:5432/kestra
            driverClassName: org.postgresql.Driver
            username: kestra
            password: k3str4
        kestra:
          server:
            basicAuth:
              username: "admin@kestra.io" # it must be a valid email address
              password: Admin1234!
          repository:
            type: postgres
          storage:
            type: local
            local:
              basePath: "/app/storage"
          queue:
            type: postgres
          tasks:
            tmpDir:
              path: /tmp/kestra-wd/tmp
          url: http://localhost:8080/
    ports:
      - "8080:8080"
      - "8081:8081"
    depends_on:
      kestra_postgres:
        condition: service_started
```

## Learn the Kestra Concepts: Data Engineering Zoomcamp - 2.2.2

### Core Concepts

### 1 Flow

A Flow is a workflow definition in Kestra. Similar to DAG in Airflow.

- Written in YAML
- Defines:
  - tasks
  - triggers
  - inputs
  - error handling
- Identified by:
  - `namespace`
  - `id`

```yaml
id: my-flow
namespace: dev.analytics
```

### 2 Namespace

A Namespace is a logical grouping of flows in Kestra.

- Helps with organization, permissions, and isolation
- Think of it like folders or domains (e.g., `dev`, `prod`, `teamA`)

### 3 Task

A Task is a single unit of work inside a Flow in Kestra.

- Executed in order unless parallelized
- Examples:
  - Run a script
  - Execute SQL
  - Call an API
  - Trigger another flow

```yaml
task:
    - id: extract
      type: io.kestra.plugin.scripts.python.Script
```

### 4 Plugin

Plugins provide additional task types in Kestra.

- Each plugin targets a specific technology or action, e.g.:
  - Scripts (`Python`, `Bash`)
  - JDBC (databases)
  - Docker
  - Cloud services (`GCP`, `AWS`, `Azure`)
- Format: Plugins are usually packaged and referenced in YAML when defining tasks

```yaml
type: io.kestra.plugin.<category>.<plugin>.<task>
```

### 5 Execution

An Execution is a single run of a Flow in Kestra.

- Has:
  - Inputs
  - State (`running`, `success`, `failed`)
  - Logs
  - Outputs
- Every triggered or manual run creates a new execution

### 6 Inputs

Inputs are parameters passed to a Flow at runtime in Kestra.

- Typed and validated to ensure correctness
- Allow flows to be dynamic and reusable

```yaml
inputs:
  - id: run_date
    type: STRING
```

Access via:
```yaml
{{ inputs.run_date }}
```

### 7 Outputs

Outputs are values produced by Tasks in a Flow.

- Can be reused by downstream tasks
- Enable data passing and chaining between tasks

```yaml
outputs:
  my_value: "{{ task.output }}"
```

Access via:
```yaml
{{ outputs.my_value }}
```

### 8 Triggers

Triggers automatically start Executions in Kestra.

- Common trigger types:
  - Schedule (cron)
  - Webhook
  - FlowTrigger
  - Kafka, S3, etc.
- Enable automation and event-driven workflows

```yaml
triggers:
  - type: io.kestra.core.models.triggers.types.Schedule
    cron: "0 0 * * *"
```

### 9 Variables & Templating

Kestra uses Pebble templates to access runtime context and make flows dynamic.

- Access variables like:
  - `{{ inputs.* }}`
  - `{{ outputs.* }}`
  - `{{ execution.id }}`
  - `{{ flow.id }}`
- Can be used in strings, commands, and configurations
- Enables dynamic values and parameterized workflows


### 10 Control Flow

Kestra supports workflow logic to control how tasks are executed:

- 🔁 Sequential (default)  
  Tasks run in order

- 🔀 Parallel  
  Tasks can run concurrently when independent
```yaml
- type: io.kestra.core.tasks.flows.Parallel
```

- 🔂 Loops
```yaml
- type: io.kestra.core.tasks.flows.ForEach
```

- ❓ Conditions
```yaml
- type: io.kestra.core.tasks.flows.Switch
```

### 11 Error Handling

Kestra supports error handling at both the flow level and task level.

- Options include:
  - Retry on failure
  - Fail the task or flow
  - Continue execution despite errors

```yaml
errors:
  - id: on_failure
    type: io.kestra.core.tasks.log.Log
```

### 12. Secrets

- Stored securely (not in YAML).
- Referenced via:
```yaml
{{ secret('MY_SECRET') }}
```
- Supports environment-based secret management.

### 13. Worker & Executor

- Executor: Where tasks actually run (local, Docker, Kubernetes).
- Worker: Polls executions and runs tasks.
- Scales horizontally.

### 14. UI & API

- Web UI for:
    - Flow editing
    - Execution monitoring
    - Logs & retries

- Everything also accessible via REST API.

### 15. Versioning

- Each flow update creates a new revision.
- Past revisions remain runnable and auditable.

#### Summary

To start building workflows in Kestra, we need to understand a number of concepts.

- Flow - a container for tasks and their orchestration logic.
- Tasks - the steps within a flow.
- Inputs - dynamic values passed to the flow at runtime.
- Outputs - pass data between tasks and flows.
- Triggers - mechanism that automatically starts the execution of a flow.
- Execution - a single run of a flow with a specific state.
- Variables - key–value pairs that let you reuse values across tasks.
- Plugin Defaults - default values applied to every task of a given type within one or more flows.
- Concurrency - control how many executions of a flow can run at the same time.



## Orchestrate Python Code: Data Engineering Zoomcamp - 2.2.3

#### 1. Using Python Scripts as Tasks

Kestra has a Python plugin (io.kestra.plugin.scripts.python.Script) that lets you run Python code directly inside a task.

```yaml
id: python-task-flow
namespace: dev.analytics
tasks:
  - id: run-python
    type: io.kestra.plugin.scripts.python.Script
    script: |
      import datetime
      today = datetime.date.today()
      print(f"Today is {today}")
    # Optional: define outputs
    outputs:
      current_date: "{{ execution.output.stdout }}"
```

- script: multi-line Python code.
- outputs: use execution.output.stdout to capture printed values.
- Access output: downstream tasks can use {{ outputs.current_date }}.

#### 2. Running a Python File

Instead of inline code, you can run a .py file:

```yaml
tasks:
  - id: run-file
    type: io.kestra.plugin.scripts.python.Script
    path: /kestra/scripts/my_script.py
    args:
      - "arg1"
      - "arg2"

```yaml
tasks:
  - id: run-file
    type: io.kestra.plugin.scripts.python.Script
    path: /kestra/scripts/my_script.py
    args:
      - "arg1"
      - "arg2"
```

- path: location of Python file in Kestra worker environment.
- args: command-line arguments passed to the script.

#### 3. Passing Inputs to Python Code

Use flow inputs to parameterize your scripts.

```yaml
inputs:
  - id: name
    type: STRING
tasks:
  - id: greet
    type: io.kestra.plugin.scripts.python.Script
    script: |
      name = "{{ inputs.name }}"
      print(f"Hello, {name}!")
```

When executing, provide name as an input:

```bash
kestra flows run --namespace dev.analytics --id python-task-flow --inputs name=Dipika
```

- Output will be `Hello, Dipika!`

#### 4. Returning Outputs from Python

Outputs allow task-to-task communication.

```yaml
tasks:
  - id: compute
    type: io.kestra.plugin.scripts.python.Script
    script: |
      x = 10
      y = 20
      print(x + y)
    outputs:
      result: "{{ execution.output.stdout }}"
      
  - id: use-result
    type: io.kestra.plugin.scripts.python.Script
    script: |
      result = "{{ outputs.compute.result }}"
      print(f"The sum was {result}")
```

- {{ outputs.compute.result }} references the previous task's output.

#### 5. Using Loops and Parallel Execution with Python Tasks

##### ForEach Example:

```yaml
tasks:
  - id: loop-python
    type: io.kestra.core.tasks.flows.ForEach
    items: ["Alice", "Bob", "Charlie"]
    task:
      id: greet
      type: io.kestra.plugin.scripts.python.Script
      script: |
        name = "{{ item }}"
        print(f"Hello, {name}!")
```

- Executes the same Python code for each element in the list.
- Each loop iteration is tracked as a separate execution.

##### Parallel Execution Example:

```yaml
tasks:
  - id: run-parallel
    type: io.kestra.core.tasks.flows.Parallel
    tasks:
      - id: task1
        type: io.kestra.plugin.scripts.python.Script
        script: print("Running Task 1")
      - id: task2
        type: io.kestra.plugin.scripts.python.Script
        script: print("Running Task 2")
```

- task1 and task2 run simultaneously.

#### ✅ Summary Workflow:

- Flow → Task → Python Script → Outputs → Next Task

- Inputs and outputs link tasks dynamically.

- Supports loops, parallel tasks, and triggers.



# 🐳 Kestra Local Docker Setup (Command Breakdown)

## 🐳 Command

    docker run --pull=always -it -p 8080:8080 --user=root \
      --name kestra --restart=always \
      -v kestra_data:/app/storage \
      -v /var/run/docker.sock:/var/run/docker.sock \
      -v /tmp:/tmp \
      kestra/kestra:latest server local

---

## 🔹 docker run
Starts a new container from a Docker image.

---

## 🔄 --pull=always
- Always pulls the latest version of the image before running
- Ensures you’re not using a stale Kestra version
- Good for learning and development
- Less common in strict production setups

---

## 🖥️ -it
- -i → interactive
- -t → allocate a terminal (TTY)

Allows you to see Kestra logs directly in your terminal.

---

## 🌐 -p 8080:8080
Maps host port 8080 to container port 8080.

Access the Kestra UI at:
http://localhost:8080

---

## 👤 --user=root
Runs the container as the root user.

Required because:
- Kestra needs access to the Docker socket
- Kestra may create files in mounted volumes

Fine for local development. Be cautious in production.

---

## 🏷️ --name kestra
Assigns a fixed name to the container: kestra.

Makes it easier to:
- Stop the container: docker stop kestra
- View logs: docker logs kestra

---

## 🔁 --restart=always
Automatically restarts the container if:
- Docker restarts
- The container crashes

Useful for long-running services like workflow orchestrators.

---

## 💾 Volumes

### kestra_data:/app/storage
- Named Docker volume
- Stores:
  - Flow definitions
  - Execution files
  - Task outputs
- Data persists even if the container is deleted

### /var/run/docker.sock:/var/run/docker.sock
- Mounts the host Docker socket into the container
- Allows Kestra to:
  - Launch Docker containers
  - Run docker.Run tasks
  - Execute Python and Bash tasks in containers

Kestra effectively becomes a Docker orchestrator.

### /tmp:/tmp
- Shares /tmp between host and container
- Used for temporary files and task artifacts

---

## 📦 kestra/kestra:latest
- Official Kestra Docker image
- latest tag points to the most recent release

---

## ▶️ server local
Command executed inside the container.

- server → starts the Kestra server
- local → runs in local mode:
  - Embedded H2 database
  - Single-node setup
  - Ideal for development and learning

In the Zoomcamp Docker Compose setup, this is replaced with PostgreSQL.

---

## 🧠 Big Picture
Runs Kestra locally in Docker, exposes the Web UI on port 8080, persists workflow data, and allows Kestra to launch Docker-based tasks.
