## docker-compose details

# Kestra + PostgreSQL Docker Compose Setup

This README explains the Docker Compose configuration used to run Kestra with supporting services in a production-like local environment.

The setup includes:
- Kestra orchestrator
- PostgreSQL database for Kestra metadata
- PostgreSQL database for NY Taxi project data
- pgAdmin for database inspection
- Persistent volumes for data durability

---

## Architecture Overview

Services in this setup:

- kestra  
  Main workflow orchestrator (UI, scheduler, executor)

- kestra_postgres  
  PostgreSQL database used internally by Kestra

- pgdatabase  
  PostgreSQL database for NY Taxi project data

- pgadmin  
  Web-based UI to inspect PostgreSQL databases

All services communicate over the same Docker network using service names.

---

## Volumes

Three named Docker volumes are defined:

- ny_taxi_postgres_data  
  Persists NY Taxi PostgreSQL database files

- kestra_postgres_data  
  Persists Kestra metadata such as flows, executions, task states, queues, and logs metadata

- kestra_data  
  Persists Kestra internal storage including flow definitions, execution artifacts, and task outputs

Volumes ensure data is not lost when containers are restarted or recreated.

---

## pgdatabase (NY Taxi PostgreSQL)

This service runs a PostgreSQL database used for the NY Taxi project.

Configuration details:
- Image: postgres:18
- Database name: ny_taxi
- Username: root
- Password: root
- Port 5432 exposed to the host
- Data persisted using ny_taxi_postgres_data volume

This database is used for ingestion, transformations, and analytics workflows.

---

## pgadmin

pgAdmin provides a web-based interface to inspect and manage PostgreSQL databases.

Configuration details:
- Image: dpage/pgadmin4
- Access URL: http://localhost:8085
- Default login email: admin@admin.com
- Default password: root

pgAdmin depends on pgdatabase and is mainly used for learning, debugging, and inspection.

---

## kestra_postgres (Kestra Metadata Database)

This PostgreSQL instance is dedicated to Kestra’s internal metadata.

Configuration details:
- Image: postgres:18
- Database name: kestra
- Username: kestra
- Password: k3str4
- Data persisted using kestra_postgres_data volume
- Includes a healthcheck to ensure the database is ready before Kestra starts

This database stores:
- flow definitions
- executions
- task states
- queues
- logs metadata

---

## kestra (Main Kestra Server)

This is the core Kestra service responsible for orchestration.

Key details:
- Image: kestra/kestra:v1.1
- Always pulls the image on startup
- Runs as root to allow access to the Docker socket
- Command used: server standalone

Responsibilities:
- Hosts the Kestra Web UI
- Schedules workflows
- Executes tasks
- Launches Docker-based tasks

---

## Kestra Volumes

Kestra mounts the following volumes:

- kestra_data mounted to /app/storage  
  Stores flows, executions, and task outputs

- /var/run/docker.sock mounted inside the container  
  Allows Kestra to launch Docker containers dynamically

- /tmp/kestra-wd mounted to /tmp/kestra-wd  
  Used as a working directory for task execution and temporary files

---

## Kestra Configuration

Kestra is configured via the KESTRA_CONFIGURATION environment variable.

Key configuration aspects:
- PostgreSQL is used for repository, queue, and metadata storage
- Basic authentication is enabled for the Web UI
- Local storage is backed by a Docker volume
- Task temporary directories are explicitly configured
- Public URL is set to http://localhost:8080

Kestra connects to its PostgreSQL database using the service name kestra_postgres.

---

## Ports

The following ports are exposed:

- 8080  
  Kestra Web UI

- 8081  
  Internal APIs and worker communication

---

## Startup Dependencies

Service startup order is managed using depends_on:

- kestra depends on kestra_postgres
- pgdatabase depends on kestra
- pgadmin depends on pgdatabase

This ensures services start in the correct order.

---

## Running the Stack

To start all services:
docker-compose up

To stop all services:
docker-compose down

To stop services and remove all volumes:
docker-compose down -v

---

## Summary

This Docker Compose setup provides:
- A realistic local Kestra environment
- Persistent storage for workflows and metadata
- Isolated databases for orchestration and analytics
- Docker-based task execution
- Easy inspection of databases using pgAdmin

It is well suited for development, experimentation, and learning Kestra.

## 🐳 Docker Containers (Kestra Zoomcamp)

| CONTAINER ID | IMAGE                 | COMMAND                   | CREATED        | STATUS           | PORTS                                             | NAMES                             |
|--------------|---------------------|---------------------------|----------------|-----------------|--------------------------------------------------|----------------------------------|
| dd7923a5fe7d | dpage/pgadmin4       | "/entrypoint.sh"          | About an hour ago | Up About an hour | 0.0.0.0:8085->80/tcp, [::]:8085->80/tcp        | kestra_practice-pgadmin-1       |
| 0b30d909d2c7 | postgres:18          | "docker-entrypoint.s…"    | About an hour ago | Up About an hour | 0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp   | kestra_practice-pgdatabase-1    |
| a79d06a7e254 | kestra/kestra:v1.1   | "docker-entrypoint.s…"    | About an hour ago | Up About an hour | 0.0.0.0:8080-8081->8080-8081/tcp, [::]:8080-8081->8080-8081/tcp | kestra_practice-kestra-1        |
| a957e0438b08 | postgres:18          | "docker-entrypoint.s…"    | About an hour ago | Up About an hour (healthy) | 5432/tcp                                      | kestra_practice-kestra_postgres-1 |

## Flow 01_hello_world.yaml

### Flow details - 

- 5 tasks: 3 log tasks and a sleep task
- flow takes an input called name.
- variable that takes the name input to generate a full welcome message.
- An output is generated from the return task and is logged in a later log task.
- trigger to execute this flow every day at 10am.
- Plugin Defaults are used to make both log tasks send their messages as ERROR level.
- concurrency limit of 2 executions. Any further ones made while 2 are running will fail.

### How to run flow - 

- For practice simply create it in Kestra and execute it. 

Note - Current Kestra server in Docker compose is Standalone so it will not pick from mounted path /app/storage of server

![01_hello_world](../kestra_practice/images/01_hello_world.png)

## Flow 02_python

### Flow details - 

- This flow will install the pip package in a Docker container, and use kestra's Python library to generate outputs (number of downloads of the Kestra Docker image) and metrics (duration of the script).

- In Kestra, there are two common ways to run Python, and they look similar but behave very differently.

#### 1️⃣ scripts.Python → Inline Python

```yaml
type: io.kestra.core.tasks.scripts.Python
```

- Runs inline Python code
- No explicit container configuration
- Uses Kestra’s default execution environment

#### 2️⃣ plugin.scripts.python.Script → Docker-based Python
```yaml
type: io.kestra.plugin.scripts.python.Script
```

- Runs Python inside a Docker container
- You fully control:
    - Python version
    - OS
    - Dependencies

### Log analysis

```log
DEBUG Use uv: uv 0.6.17
```

- Kestra uses uv instead of pip:
    - Much faster
    - Deterministic dependency resolution
    - Better caching

```log
Compiling dependencies with uv
Installing packages with uv
Installed dependencies: requests, kestra, ...
```

### Summary
#### Python Script Execution (Docker)
- Uses Docker runner
- Installs Python dynamically (default: 3.13)
- Uses `uv` for dependency management
- Pulls container image
- Runs script
- Cleans up container + volumes
- Caches dependencies

![02_python](../kestra_practice/images/02_python.png)

## 03_getting_started_data_pipeline

✅ High-level Overview

- Extract: Download JSON from an API (Extract Data via HTTP REST API)
- Transform: Filter only specific fields using a Python script (Transform Data in Python)
- Query: Run SQL on the transformed JSON using DuckDB (Query Data with DuckDB)

![03_getting_started_data_pipeline](../kestra_practice/images/03_getting_started_data_pipeline.png)

## 04_postgres_taxi

### Local DB: Load Taxi Data to Postgres

✅ Big picture: what this flow does

- This flow loads NYC taxi CSV data into Postgres in an idempotent way:
- User selects taxi type, year, month
- CSV is downloaded from GitHub
- Data is copied into a staging table
- A unique hash ID is generated per row
- Data is merged into the final table (no duplicates)
- Same logic works for yellow OR green taxis
- Classic ELT-style pipeline.

🧠 Mental model summary

| Layer     | Purpose                   |
| --------- | ------------------------- |
| Inputs    | Parameterize the pipeline |
| Variables | Build dynamic names       |
| Extract   | Download raw data         |
| Staging   | Safe bulk loading         |
| Hash ID   | Idempotency               |
| Merge     | Incremental load          |
| Cleanup   | Resource hygiene          |

![04_postgres_taxi](../kestra_practice/images/04_postgres_taxi_1.png)

![04_postgres_taxi_2](../kestra_practice/images/04_postgres_taxi_2.png)


## 05_postgres_taxi_scheduled

### Local DB: Learn Scheduling and Backfills

Schedule the same pipeline from 04 shown above to run on 1st of every month at 9 AM UTC for green taxi and 10 AM for yellow taxi 

### What “Backfill” Means in Kestra

- Normally, scheduled flows only run from the current time forward.
- Backfill means you want to run the flow for a past date or a range of past dates.
- Kestra allows this without modifying the schedule, using the UI trigger.

### Backfill execution steps - 

- Navigate to your flow: 05_postgres_taxi_scheduled in the UI.
- Goto subtab - Triggers and click Backfill executions
- Set start and end date
- Execute flow

## ELT Pipelines in Kestra: Google Cloud Platform

- Extract: Firstly, we extract the dataset from GitHub
- Load: Next, we load this dataset (in this case, a csv file) into a data lake (Google Cloud Storage)
- Transform: Finally, we can create a table inside of our data warehouse (BigQuery) which uses the data from our data lake to perform our transformations.

- The reason for loading into the data warehouse before transforming means we can utilize the cloud's performance benefits for transforming large datasets. What might take a lot longer for a local machine, can take a fraction of the time in the cloud.


## 06_gcp_kv.yaml

### This flow is about centralized configuration using Kestra’s Key–Value (KV) store.

🧠 Big picture: what this flow does

06_gcp_kv stores GCP configuration values (project, region, bucket, dataset) in Kestra’s KV store, so that:

- You don’t hardcode them in every flow
- Other flows can read them dynamically
- Changing GCP settings = update one place only

Think of it as environment variables managed by Kestra.

🔑 What is the KV store?

Kestra KV store is:

- Persistent
- Namespace-scoped
- Accessible from any flow or task

You can:

- Set a value
- Get a value
- Use it in templates: {{ kv('KEY_NAME') }}

### Set GCP Project ID

Example - 

```yaml
- id: gcp_project_id
  type: io.kestra.plugin.core.kv.Set
  key: GCP_PROJECT_ID
  kvType: STRING
  value: kestra-sandbox
```

Stores
```text
GCP_PROJECT_ID = "kestra-sandbox"
``

🔧 Used later for:

- BigQuery
- GCS
- Dataflow
- Any GCP plugin


### 📦 Where are these values stored?

- In Kestra’s internal database
- Scoped to the zoomcamp namespace
- Persist even if Kestra restarts

You can view them in the UI:

- Namespace → Key-Value Store

### 🧠 How other flows use these values

Anywhere in Kestra (YAML, SQL, scripts):

```yaml
{{ kv('GCP_PROJECT_ID') }}
{{ kv('GCP_BUCKET_NAME') }}
{{ kv('GCP_DATASET') }}
```

Example
```yaml
bucket: "{{ kv('GCP_BUCKET_NAME') }}"
projectId: "{{ kv('GCP_PROJECT_ID') }}"
```

![06_gcp_kv](../kestra_practice/images/06_gcp_kv.png)

![06_gcp_kv_2](../kestra_practice/images/06_gcp_kv_2.png)

## 07_gcp_setup

While 06_gcp_kv stores GCP configuration in Kestra, 07_gcp_setup usually creates the actual GCP resources that your pipelines will need:

- GCS Bucket (for storing raw or processed CSVs)
- BigQuery Dataset (for analytics queries and tables)
- Optional: IAM roles, service accounts, or permissions

This flow provisions the GCP resources your pipelines will need:

- GCS bucket → for storing raw/processed CSVs
- BigQuery dataset → for analytics tables
- It uses values from the KV store, which were set in 06_gcp_kv.

### For this flow, need GCP_CREDS

#### What GCP_CREDS is for

- GCP_CREDS should contain your service account key JSON as a string
- Kestra uses it to authenticate with GCP for creating buckets, datasets, etc.
- Without it, any GCP task will fail with authentication errors.

#### How to fix

- Create a service account in GCP
- Go to: IAM & Admin → Service Accounts → Create Service Account
- Give it roles needed for your flows:

    - Storage Admin → for GCS
    - BigQuery Admin → for dataset/table creation
    - Note - I simply gave owner role

- Download JSON key
- This is the credentials file Kestra needs
- Store it in Kestra KV
    - Add a task to 06_gcp_kv:
    ```yaml
    - id: gcp_creds
  type: io.kestra.plugin.core.kv.Set
  key: GCP_CREDS
  kvType: STRING
  value: |
    {
      "type": "service_account",
      "project_id": "your-project-id",
      "private_key_id": "...",
      "private_key": "-----BEGIN PRIVATE KEY-----\n...",
      "client_email": "...",
      "client_id": "...",
      ...
    }
    ```
    - Keep the entire JSON content as the value. Kestra will inject it into tasks referencing {{kv('GCP_CREDS')}}.

#### Issue

`Error - your GCP organization has disabled creating service account keys.`

##### Why this is happening

- Policy enforced: iam.disableServiceAccountKeyCreation
- Effect: You cannot create JSON keys for service accounts
- Reason: Google recommends using more secure authentication methods like Workload Identity or Application Default Credentials (ADC).

##### Use Application Default Credentials (ADC)

ADC lets Kestra use the credentials of the logged-in user or the VM/container’s service account.

- How to set it up locally:
    - Install and authenticate with gcloud:
    ```bash
    gcloud auth login
    gcloud auth application-default login
    ```
    - This creates a credential file in ~/.config/gcloud/application_default_credentials.json
    - Kestra and most GCP SDKs can use it automatically




## Setup Google Cloud Platform (GCP)

### Setup Google Cloud Platform

When you’re using Google Cloud (and for some Google Workspace apps), you’re going to need to authenticate inside of Kestra. The best way to do this is by using a Service Account.

#### Create Service Account inside of Google Cloud

- Service Account: In Google Cloud, a service account is a special type of Google account used by an application or a virtual machine (VM) instance, rather than a human user. It's an identity that allows your workloads to make authorized API calls.

- Authentication: When your application needs to interact with Google Cloud APIs (like reading from Cloud Storage or writing to BigQuery), it needs to prove its identity. A `service account key` serves as that proof.

```text
IAM -> Service Accounts
```

Name - dipika_zoomcamp
Role - owner

For this Service account, create key



