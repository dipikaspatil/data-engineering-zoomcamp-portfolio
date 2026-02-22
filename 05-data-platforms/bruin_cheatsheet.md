# 🐻 Bruin Cheatsheet
*DataTalksClub – Data Engineering Zoomcamp (05 Data Platforms)*

A concise, practical reference for Bruin concepts, commands, and configuration.

---

## 01 – Introduction

### What is Bruin?
- End-to-end **data platform**
- Unifies:
  - Ingestion
  - Transformations
  - Orchestration
  - Data quality checks
  - Metadata
  - Lineage
- Replaces stitching together multiple tools in a modern data stack

### Why Bruin?
- Single place for pipeline logic, dependencies, and configs
- Built-in lineage & metadata
- Strong focus on developer experience

### Key Concepts Introduced
- Pipelines
- Assets
- Materializations
- Dependencies & lineage
- Metadata
- Parameterization (variables)

---

## 02 – Getting Started

### Install Bruin CLI
```bash
curl -LsSf https://getbruin.com/install/cli | sh
bruin version
```

### IDE Support

- VS Code / Cursor extension
- Render panel to run assets & pipelines
- Optional Bruin MCP for AI-assisted pipeline development

### Initialize a Project
```bash
bruin init default my-first-pipeline
cd my-first-pipeline
```
- Initializes Git (required)
- Creates base .bruin.yml

### Project Structure

```perl
my-first-pipeline/
├── .bruin.yml            # Env configs & secrets (local only)
├── pipeline.yml          # Pipeline definition
└── assets/
    ├── ingest.asset.yml  # Ingestion asset
    ├── transform.sql     # SQL asset
    └── transform.py      # Python asset
```

#### .bruin.yml
- Environment-specific configuration
- Connection definitions
- Do not commit secrets

Example:

```yaml
default_environment: default
environments:
  default:
    connections:
      duckdb:
        - name: duckdb-default
          path: duckdb.db
```

#### pipeline.yml

- Pipeline metadata & scheduling

Example:
```yaml
name: my-pipeline
schedule: daily
start_date: "2022-01-01"
default_connections:
  duckdb: duckdb-default
```

#### Asset Types

- YAML ingest assets – source → destination
- SQL assets – transformations, checks, dependencies
- ython assets – custom logic

#### Dependencies & Lineage

- Assets define upstream/downstream relationships
- Bruin automatically builds lineage graph

#### Incremental Processing

- Use start_date / end_date variables
- Enables time-based ingestion & backfills

### CLI Commands (Quick Reference)

| Command                                           | Description                     |
| ------------------------------------------------- | ------------------------------- |
| `bruin validate`                                  | Validate configs & dependencies |
| `bruin run`                                       | Run pipeline or asset           |
| `bruin run --downstream`                          | Run asset + downstream          |
| `bruin run --full-refresh`                        | Rebuild from scratch            |
| `bruin lineage`                                   | Show dependency graph           |
| `bruin query --connection <conn> --query "<sql>"` | Run ad-hoc SQL                  |

### Notes / Gotchas

- .bruin.yml is local-only
- Git repo is mandatory
- Defaults can be overridden per asset

## 📍 03 — NYC Taxi Pipeline (Cheatsheet)

### 🏗️ Architecture Overview

Three layers:

1. Ingestion — extract raw data and store
2. Staging — clean/transform & join lookup data
3. Reports — aggregated, analytics-ready tables

All assets have dependencies that form Bruin’s execution graph (lineage).

### 📦 Project Setup
Initialize
```bash
bruin init zoomcamp my-taxi-pipeline
cd my-taxi-pipeline
```

### Project Structure
```markdown
zoomcamp/
├── .bruin.yml
├── README.md
└── pipeline/
    ├── pipeline.yml
    └── assets/
        ├── ingestion/
        ├── staging/
        └── reports/
```

(ingestion contains Python & lookup CSV, staging & reports contain SQL)

### 🔑 .bruin.yml — Connection Setup
```yaml
default_environment: default
environments:
  default:
    connections:
      duckdb:
        - name: duckdb-default
          path: duckdb.db
```

Sets DuckDB as local database connection.

### 🗓️ pipeline.yml Essentials

```yaml
name: nyc_taxi
schedule: daily
start_date: "2022-01-01"
default_connections:
  duckdb: duckdb-default

variables:
  taxi_types:
    type: array
    items:
      type: string
    default: ["yellow"]
```

Notes:

- start_date used for full refresh scheduling
- taxi_types variable lets you control which taxi types to ingest (yellow, green, etc.)
- Variables can be overridden at runtime with --var.

### 🚚 Ingestion Layer
Python Asset — trips.py

```python
"""@bruin name: ingestion.trips type: python ... materialization: type: table strategy: append ... @bruin"""
def materialize():
   start_date = os.environ["BRUIN_START_DATE"]
   end_date = os.environ["BRUIN_END_DATE"]
   taxi_types = json.loads(os.environ["BRUIN_VARS"]).get("taxi_types", ["yellow"])
   # Fetch parquet from online source
   return final_dataframe
```

Key points:

- Returns a DataFrame that Bruin persists
- Uses append strategy (adds new data)
- Reads env vars: BRUIN_START_DATE, BRUIN_END_DATE, and BRUIN_VARS for variables

### Seed Lookup File — payment_lookup.asset.yml

```yaml
name: ingestion.payment_lookup
type: duckdb.seed
parameters:
  path: payment_lookup.csv
  columns:
  - name: payment_type_id ...
    primary_key: true
    checks:
    - name: not_null
    - name: unique
  - name: payment_type_name ...
    checks:
    - name: not_null
```

- Loads a local CSV (lookup for payment types)
- Built-in quality checks run automatically after asset completes.

### 🔄 Staging Layer
SQL Asset — staging/trips.sql

```sql
/* @bruin name: staging.trips ... materialization: type: table strategy: time_interval ... @bruin */
SELECT t.pickup_datetime, …
FROM ingestion.trips t
LEFT JOIN ingestion.payment_lookup p
ON t.payment_type = p.payment_type_id
WHERE t.pickup_datetime >= '{{ start_datetime }}'
AND t.pickup_datetime < '{{ end_datetime }}'
QUALIFY ROW_NUMBER() OVER (…) = 1
```

Key points:

- time_interval strategy deletes rows in a date range then inserts new rows
- Must filter on same time window to avoid duplicates
- Uses deduplication (ROW_NUMBER() in SQL)

### 📊 Reports Layer
SQL Asset — reports/trips_report.sql

```sql
/* @bruin name: reports.trips_report ... materialization: type: table strategy: time_interval … @bruin */
SELECT CAST(pickup_datetime AS DATE) AS trip_date,
       taxi_type,
       payment_type_name AS payment_type,
       COUNT(*) AS trip_count,
       SUM(fare_amount) AS total_fare,
       AVG(fare_amount) AS avg_fare
FROM staging.trips
WHERE pickup_datetime >= '{{ start_datetime }}'
  AND pickup_datetime < '{{ end_datetime }}'
GROUP BY 1, 2, 3
```

- Builds summary counts & fare stats per date, taxi type, payment type
- Uses time_interval strategy like staging.

## 🏃‍♂️ Running the Pipeline

| Task                        | Command                                                                                  |
| --------------------------- | ---------------------------------------------------------------------------------------- |
| Validate assets             | `bruin validate ./pipeline/pipeline.yml`                                                 |
| Test run (small date range) | `bruin run ./pipeline/pipeline.yml --start-date 2022-01-01 --end-date 2022-02-01`        |
| Full refresh                | `bruin run ./pipeline/pipeline.yml --full-refresh`                                       |
| Query output                | `bruin query --connection duckdb-default --query "SELECT COUNT(*) FROM ingestion.trips"` |

### 🔄 Execution Order

- Ingestion assets (trips + lookup)
- Staging asset runs after ingestion
- Reports asset runs after staging.

### 🧠 Materialization Strategy Summary

| Strategy         | Behavior                           |
| ---------------- | ---------------------------------- |
| `table`          | Drop + recreate every run          |
| `append`         | Add rows without removing existing |
| `merge`          | Upsert based on key columns        |
| `time_interval`  | Remove rows in window then insert  |
| `delete+insert`  | Manual delete then insert          |
| `create+replace` | Create new table, replace old      |


## 04 – Bruin MCP (Model Context Protocol)

### What is Bruin MCP
Bruin MCP enables **IDE‑assisted context awareness**, giving:
- Autocomplete for pipeline & asset definitions
- Context‑aware suggestions
- Inline skeletons for Bruin objects
- Intelligent help while editing

Supported in:
- VS Code
- Cursor IDE

## 05 Deploying to Bruin Cloud

What is Bruin Cloud?
- Bruin Cloud is a fully managed infrastructure for your data pipelines.
- It is powered by the same open-source CLI tool you use locally for development. Everything lives in the same place:
    - Ingestions and transformations
    - Quality checks and monitoring
    - Lineage and metadata
    - Data governance
    - AI-powered features (automatic metadata generation, conversational data analysis)

https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/05-data-platforms/notes/05-bruin-cloud.md

## Core Concepts: Projects

### What is a Project?
- A Project is the root directory where you create your entire Bruin data pipeline. It serves as the foundation for organizing all your data assets, configurations, and connections.

### Project Initialization

```bash
bruin init zoomcamp my-pipeline
cd my-pipeline
```

### The .bruin.yml File

- Located at the root of your project, this file defines environments, connections, and secrets.
- Important: This file is always added to .gitignore to protect secrets. It stays local only and should never be pushed to your repo.


Environments
Define different environments for various stages:

```yaml
default_environment: default

environments:
  default:
    connections:
      duckdb:
        - name: duckdb-default
          path: duckdb.db
      motherduck:
        - name: motherduck
          token: <your-token>

  production:
    connections:
      bigquery:
        - name: bq-prod
          project: my-project
          dataset: production
```

### Quick Reference

```bash
# Initialize a new project
bruin init zoomcamp my-pipeline

# Navigate to your project
cd my-pipeline

# Check project is valid
bruin validate .
```

## Core Concepts: Pipelines

### What is a Pipeline?
A Pipeline is a grouping mechanism for organizing assets based on their execution schedule and configuration requirements. Within a project, you can have multiple pipelines.

### Key Characteristics

#### Single Schedule
- Each pipeline has one schedule - this is the primary reason to group assets together:
- Assets with the same schedule belong in the same pipeline
Common schedules: hourly, daily, monthly, or cron expressions

#### Pipeline Structure
Each pipeline has its own folder containing a pipeline.yml file:

```yaml
project/
├── .bruin.yml
├── pipelines/
│   ├── nyc-taxi/
│   │   ├── pipeline.yml
│   │   └── assets/
│   └── another-pipeline/
│       ├── pipeline.yml
│       └── assets/
```

### The pipeline.yml File

```yaml
name: nyc_taxi
schedule: monthly
start_date: "2019-01-01"
default_connections:
  duckdb: duckdb-default
```

### Configuration Options
| Setting | Description |
|--------|-------------|
| name | Pipeline identifier |
| schedule | When to run (cron, daily, monthly, etc.) |
| start_date | When the pipeline starts being active |
| default_connections | Which connections to use |
| variables | Custom variables for the pipeline |


### Connection Scoping
Even though connections are defined at the project level (.bruin.yml), each pipeline specifies which connections it uses.

Why this matters:

- In large organizations, different teams may need different credentials
- Prevents unnecessary exposure of secrets
- Only initializes connections needed for the specific pipeline run
- Security isolation between departments

### Quick Reference

```bash
# Validate a pipeline
bruin validate ./pipelines/nyc-taxi/pipeline.yml

# View pipeline lineage
bruin lineage ./pipelines/nyc-taxi/pipeline.yml

# Run the entire pipeline
bruin run ./pipelines/nyc-taxi/pipeline.yml
```

## Core Concepts: Assets

### What is an Asset?
An Asset is a single file that performs a specific task, almost always related to creating or updating a table or view in the destination database.

Each asset file contains two parts:
1. Definition (Configuration) - Metadata, name, type, connection
2. Content (Code) - The actual SQL, Python, or R code to execute

### Asset Types

| Type | Description | Use Case |
|------|-------------|----------|
| Python | Python scripts | Ingestion, data processing, ML models |
| SQL | SQL queries | Transformations, aggregations |
| YAML / Seed | File-based tables | Reference data, static lookups |
| R | R scripts | Statistical analysis, R-specific workflows |

### Asset Naming
The asset name can be:

- Explicitly defined in the decorator
- Inferred from file path (default behavior)
- Convention: Group assets by schema/dataset:
    - assets/raw/trips_raw.py → Creates table raw.trips_raw
    - assets/staging/trips_summary.sql → Creates table staging.trips_summary

### SQL Asset Example

```sql
@bruin.asset(
    name="staging.trips_summary",
    type="sql",
    connection="duckdb-default",
    materialization="table"
)

SELECT
    pickup_date,
    COUNT(*) as trip_count,
    SUM(fare_amount) as total_fare
FROM raw.trips_raw
WHERE pickup_date >= '{{ start_date }}'
  AND pickup_date < '{{ end_date }}'
GROUP BY pickup_date
```

### Materialization Strategies

| Strategy | Behavior |
|---------|----------|
| table | Recreates the table on each run |
| view | Creates a view (no data stored) |
| insert | Appends new data to existing table |
| incremental | Smart merge based on key columns |

## Python Asset Example (Ingestion)

```python
@bruin.asset(
    name="raw.trips_raw",
    type="python",
    connection="duckdb-default"
)
def ingest_trips():
    import requests
    import pandas as pd

    # Connect to API, fetch data
    response = requests.get("https://api.example.com/trips")
    data = response.json()

    # Return pandas DataFrame
    # Bruin handles materialization to database
    return pd.DataFrame(data)
```

## YAML/Seed Asset Example

```yaml
@bruin.asset(
    name="lookup.taxi_types",
    type="seed",
    connection="duckdb-default"
)

path: reference_data/taxi_types.csv
```

Simply loads a local CSV file and creates a table in the destination database.

### Lineage & Dependencies

Assets automatically define dependencies based on what they read:
- If Asset B reads from Asset A's table, B depends on A
- Visualized in VS Code extension
- Used for execution ordering during runs

```sql
-- This asset depends on raw.trips_raw
@bruin.asset(name="staging.trips_summary", type="sql")
SELECT * FROM raw.trips_raw  -- Creates dependency
```

### Quick Reference

```bash
# Run a specific asset
bruin run ./pipeline.yml --asset raw.trips_raw

# Run asset with all downstream dependencies
bruin run ./pipeline.yml --asset raw.trips_raw --downstream

# Run asset with all upstream dependencies
bruin run ./pipeline.yml --asset staging.trips_summary --upstream

# View lineage for an asset
bruin lineage ./pipeline.yml --asset raw.trips_raw
```

## Core Concepts: Variables

### What are Variables?
Variables are dynamically initialized each time a pipeline run is created. They allow you to parameterize your pipelines and pass dynamic values at runtime.

### Variable Types
1. Built-in Variables
Always provided by Bruin automatically:

| Variable | Description |
|---------|-------------|
| start_date | Beginning of the scheduled interval |
| end_date | End of the scheduled interval |

These dates are determined by the pipeline's schedule:

| Schedule | Start Date | End Date |
|----------|------------|----------|
| Monthly | First day of month | Last day of month |
| Daily | Start of day | End of day |
| Hourly | Start of hour | End of hour |

### SQL Assets - Jinja Format
In SQL, variables are injected using Jinja templating:

```sql
@bruin.asset(name="staging.monthly_trips", type="sql")
SELECT *
FROM raw.trips
WHERE pickup_date >= '{{ start_date }}'
  AND pickup_date < '{{ end_date }}'
```

Use the Bruin Render panel in VS Code to see the compiled query with actual values.

### Python Assets - Environment Variables
In Python, variables are accessed via environment variables:

```python
import os
from datetime import datetime

@bruin.asset(name="raw.monthly_data", type="python")
def ingest_monthly_data():
    start_date = os.environ['BRUIN_VAR_START_DATE']
    end_date = os.environ['BRUIN_VAR_END_DATE']

    # Parse and use dates to fetch data for specific period
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)

    # Loop through months in range
    # ...
```

2. Custom Variables
User-defined variables set at the pipeline level.

### Definition in pipeline.yml

```yaml
variables:
  - name: taxi_types
    type: array
    default:
      - "yellow"
```

### Override at Runtime
Change default values when creating a run:

```bash
bruin run ./pipeline.yml --var taxi_types=["green","fhv"]
```

### Accessing Custom Variables in Python

```python
import os
import json

@bruin.asset(name="example.asset", type="python")
def example_asset():
    # Custom variables are prefixed with BRUIN_VAR_
    taxi_types_json = os.environ['BRUIN_VAR_TAXI_TYPES']
    taxi_types = json.loads(taxi_types_json)

    # Use the variable in your code
    for taxi_type in taxi_types:
        # Process each taxi type
        pass
```

### VS Code Extension Panel
From the Bruin panel in VS Code/Cursor:

- Variable Override - Set custom variable values before running
- Bruin Render - See how Jinja templates are compiled with actual values
- Run Configuration - Set dates, environment, and variables

### Practical Use Cases

| Use Case | Description |
|----------|-------------|
| Date-based partitioning | Extract data for specific time periods |
| Multi-tenant processing | Run same pipeline for different customers |
| Parameterized transformations | Change logic based on variables |
| A/B testing | Test different configurations without code changes |

### Quick Reference

```bash
# Run with custom dates
bruin run ./pipeline.yml --start-date 2020-01-01 --end-date 2020-01-31

# Run with variable override (array)
bruin run ./pipeline.yml --var taxi_types=["green","fhv"]

# Run with variable override (string)
bruin run ./pipeline.yml --var customer_id=12345

# Run with full refresh (affects materialization)
bruin run ./pipeline.yml --full-refresh

# Set end date as exclusive
bruin run ./pipeline.yml --exclusive-end-date
```

## Core Concepts: Commands

### Bruin CLI Commands
Commands are how you interact with your Bruin project - running pipelines, validating configurations, querying data, and more.

### `bruin run` - Execute a Pipeline

Creates a single execution instance (a "run") of your pipeline.

Basic Usage
```bash
bruin run ./pipelines/nyc-taxi/pipeline.yml
```

Run Scope Options

| Option | Description |
|--------|-------------|
| Entire pipeline | Runs all assets in dependency order |
| Single asset | `--asset staging.trips_summary` |
| With upstream | `--asset X --upstream` — runs X plus all dependencies |
| With downstream | `--asset X --downstream` — runs X plus all dependents |

Common Run Flags

| Flag | Description |
|------|-------------|
| `--start-date DATE` | Set execution start date |
| `--end-date DATE` | Set execution end date |
| `--full-refresh` | Drop and recreate tables (overrides incremental) |
| `--exclusive-end-date` | End date is exclusive (default: inclusive) |
| `--environment ENV` | Use specific environment (dev/prod) |
| `--var KEY=VALUE` | Override custom variables |

### Example Run Commands

```bash
# Simple run
bruin run ./pipelines/nyc-taxi/pipeline.yml

# With date range
bruin run ./pipelines/nyc-taxi/pipeline.yml \
  --start-date 2020-01-01 \
  --end-date 2020-01-31

# Full refresh with variables
bruin run ./pipelines/nyc-taxi/pipeline.yml \
  --full-refresh \
  --var taxi_types=["yellow","green"] \
  --environment default

```

### `bruin validate` - Validate Pipeline

Checks for configuration issues before running:

```bash
bruin validate ./pipelines/nyc-taxi/pipeline.yml
```

Validates:
- No circular dependencies in lineage
- Asset definitions are correct
- Connections exist and are properly configured
- No broken references

Always validate before running!

### `bruin lineage` - View Dependency Graph

Visualize how assets are connected:

```bash
bruin lineage ./pipelines/nyc-taxi/pipeline.yml
```
Shows upstream and downstream relationships between assets.

### `bruin query` - Query Data

Run ad-hoc queries against your connections:

```bash
bruin query --connection duckdb-default \
  --query "SELECT * FROM ingestion.trips LIMIT 10"
```

### What is a "Run"?
A run is a single instance of pipeline execution:

- Has unique start/end times
- May run all assets or a subset
- Has its own variable values
- Creates execution logs and results

## Putting It All Together

The complete Bruin workflow:

```markdown
1. Project (root, initialized)
   └── .bruin.yml (environments, connections)

2. Pipeline (scheduled grouping)
   └── pipeline.yml (schedule, default connection, variables)

3. Assets (the actual work)
   ├── Python (ingestion, processing)
   ├── SQL (transformations)
   └── YAML/Seed (static data)

4. Commands (make it happen)
   ├── bruin run (execute)
   ├── bruin validate (check)
   └── bruin query (inspect)
```

## Quick Reference

```bash
# Initialize new project
bruin init zoomcamp my-pipeline

# Validate before running
bruin validate ./pipeline/pipeline.yml

# Run entire pipeline
bruin run ./pipeline/pipeline.yml

# Run with date range
bruin run ./pipeline/pipeline.yml \
  --start-date 2020-01-01 \
  --end-date 2020-01-31

# Run single asset with downstream
bruin run ./pipeline/pipeline.yml \
  --asset raw.trips \
  --downstream

# View lineage
bruin lineage ./pipeline/pipeline.yml

# Query a table
bruin query --connection duckdb-default \
  --query "SELECT COUNT(*) FROM staging.trips"
```