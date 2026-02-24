# Module 5 Homework: Data Platforms with Bruin
In this homework, we'll use Bruin to build a complete data pipeline, from ingestion to reporting.

https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/05-data-platforms/homework.md


## Setup Steps for Homework

### Install Bruin CLI

```bash
curl -LsSf https://getbruin.com/install/cli | sh
```

### Initialize your project

```bash
bruin init zoomcamp my-pipeline
```

Instead of bruin init, which creates a new folder, you can manually create the structure or run the init command and move the files. The easiest way is:

```bash
bruin init zoomcamp .
```

(The . tells Bruin to put the files directly in the current folder instead of creating a new sub-folder).

### Configure your database connection
Note - .bruin.tml was not created by init command mentioned above. So I had to create it manually.


Edit .bruin.yml to use DuckDB:

```yaml
default_environment: default
environments:
  default:
    connections:
      duckdb:
        - name: duckdb-default
          path: duckdb.db
```

- The beauty of DuckDB is that you don't actually need to install a database server (like you do with PostgreSQL or MySQL). It is "serverless" and runs entirely inside the Bruin process.

- Bruin will create the database file (the duckdb.db file mentioned in your config) automatically the first time you run a pipeline.

- However, you do need the Python library so Bruin can write to it if you're using Python assets.

1. Install the Python Requirements
Run below command inside virtual environment to ensure your environment has what it needs:

Note - virtual environment reates a private sandbox for your project so you don't mess with the system settings.


```bash
python3 -m venv my_project_env

source my_project_env/bin/activate

pip install duckdb pandas pyarrow
```

- duckdb: The engine.
- pandas/pyarrow: Needed to handle the NYC Taxi .parquet files.

### Verify the pipeline template

- Your project should now include:
```
.bruin.yml
```
- pipeline/ folder (with pipeline.yml and asset Python files)
- assets/ (optional depending on template)

Follow the tutorial in the module README to run a sample pipeline on NYC taxi data.

### Create the Real Ingestion Script
Open (or create) pipeline/assets/ingestion/trips.py and replace the test code with this logic, which is designed to fetch the Parquet files.

### Fix parameters of pipeline.yml

Open pipeline/pipeline.yml and setup all required parameters like - name, schedule etc

### Fix the Staging Asset (assets/staging/trips.sql)

Open this file and replace its contents with a simple SQL cleaning script. This asset depends on the ingestion script we wrote earlier.

### Fix the Report Asset (assets/reports/trips_report.sql)
Open this file and update it to aggregate the data from staging:

### Fix the Lookup Asset (assets/ingestion/payment_lookup.asset.yml)
Open this file and update it

#### Why Bruin uses .asset.yml:

- Bruin ecosystem, .asset.yml is a double extension used as a "marker." It tells the Bruin engine: "Hey, don't just treat this as a random configuration file; this is a functional Asset that represents a table in the database."

- Filtering: Your project might have dozens of .yml files (pipeline config, environment variables, CI/CD settings). By requiring .asset.yml, Bruin knows exactly which ones it needs to parse to build your data lineage.

- Asset Type Identification: It allows Bruin to distinguish between a SQL asset (which usually lives in a .sql file with a header) and a Seed/External asset (which needs a YAML file to define its properties).



### Check lineage 

```bash
bruin lineage pipeline
```

### Dry run

```bash
bruin run ./pipeline --start-date 2022-01-01 --end-date 2022-02-01 --dry-run
```
The --dry-run flag will show you the order of operations without actually executing code

### 3. Run a Specific Month
To test that your environment and the script are working together, run this command to process just January 2022:

```bash
bruin run --start-date 2022-01-01 --end-date 2022-02-01
```

🔍 What to expect in your terminal:
You should see a task-by-task breakdown. It will look something like this:

- ingestion.payment_lookup: Completed (Seed)

- ingestion.trips: Running... (You'll see your "Downloading..." message)

- staging.trips: Completed (SQL)

- reports.trips_report: Completed (SQL)

🛠️ How to check the results
Once the run finishes, your data will be sitting in a local DuckDB file (usually named duckdb.db or whatever is defined in your connections.yml).

You can check if the data actually landed by running this command in your terminal to query the final report:

```bash
bruin query "SELECT * FROM reports.trips_report LIMIT 10"
```

### Dependency chain jsut for understanding

```code
ingestion.trips ----------------> staging.trips ➔ reports.trips_report
ingestion.payment_lookup_asset ↗
```

### Few Basic questions about setup - 

1. Will pipeline/assets/ingestion/trips.py be part of virtual envt?

No, the script itself (trips.py) is not "inside" the virtual environment, but it runs using the Python interpreter from that environment.

Think of it this way:
- The Virtual Environment (venv): Is your toolbox. It contains the Python version and the libraries (pandas, duckdb, pyarrow).
- The Script (trips.py): Is your blueprint. It’s just a text file that sits in your project folder.
- Bruin: Is the foreman. It reads the blueprint and uses the tools in your toolbox to build the data table.

2. How Bruin knows which environment to use:
By default, Bruin looks for a command named python. If your virtual environment is active in your terminal, the command python points to your venv, and everything works perfectly.

If you want to be 100% sure Bruin always uses your virtual environment (even if you forget to activate it), you can explicitly set it in your .bruin.yml:

```yaml
# .bruin.yml
default_environment: default
environments:
  default:
    connections:
      duckdb:
        - name: duckdb-default
          path: duckdb.db
# Point this to the actual python file inside your venv folder
python_command: ./bin/python
```

Steps to check if it's working:
- Activate your venv: source bin/activate (or your specific path).

- Run validation: bruin validate ..

- Run the pipeline: bruin run ..

If you get an error saying `ModuleNotFoundError: No module named 'pandas'`, it means Bruin is using your system Python instead of your virtual environment. 

If that happens, setting the python_command in .bruin.yml as shown above will fix it.


## Homework Questions and answers - 

### Question 1: Bruin Pipeline Structure

Question: What are the required files/directories?

- bruin.yml and assets/

- .bruin.yml and pipeline.yml (assets can be anywhere)

- .bruin.yml and pipeline/ with pipeline.yml and assets/

- pipeline.yml and assets/ only


✅ Answer:
```code
.bruin.yml and pipeline/ with pipeline.yml and assets/
```
- .bruin.yml: This is the root configuration file. It lives in the base directory of your project and defines your connections (like DuckDB, BigQuery, or Snowflake) and environment-level settings.

- pipeline/ folder: This is the container for your data workflow.

- pipeline.yml: Defines the pipeline name, schedule, and global variables for that specific workflow.

- assets/: The directory where your actual Python scripts (.py) and SQL transformations (.sql) reside.

```plaintext
my-project/
├── .bruin.yml          <-- Connection & Env Config
└── my-taxi-pipeline/   <-- Pipeline Directory
    ├── pipeline.yml    <-- Pipeline Metadata
    └── assets/         <-- SQL and Python Assets
```

### Question 2: Materialization Strategies

You're building a pipeline that processes NYC taxi data organized by month based on pickup_datetime. Which incremental strategy is best for processing a specific interval period by deleting and inserting data for that time period? 

Options: append, replace, time_interval, view

✅ Answer:
```code
time_interval - incremental based on a time column
```

- How it works: When you run the pipeline for a specific period (e.g., January 2024), Bruin automatically deletes any existing rows in that date range and then inserts the fresh data.

- The Benefit: It ensures idempotency. If you run the same job twice, the result remains the same because the old data for that interval is cleared out before the new data is written.

| Strategy | Best Use Case | Risk |
|----------|---------------|------|
| append | Simple logging where data never changes | High risk of duplicate rows if a job is retried |
| replace | Small lookup tables or dimensions | Very slow and expensive for large historical datasets |
| time_interval | Taxi trips, sensor data, or logs | Requires a reliable timestamp column (e.g., pickup_datetime) |
| view | Simple transformations that don't need to be stored | Can be slow to query if the underlying logic is complex |


### Question 3: Pipeline Variables

You have a variable defined in pipeline.yml:
variables: 
    taxi_types: 
        type: array 
        items: 
            type: string 
        default: ["yellow", "green"]
How do you override this when running the pipeline to only process yellow taxis? 

- bruin run --taxi-types yellow

- bruin run --var taxi_types=yellow

- bruin run --var 'taxi_types=["yellow"]'

- bruin run --set taxi_types=["yellow"]

✅ Answer:
```
bruin run --var 'taxi_types=["yellow"]'
```

When overriding variables in Bruin via the CLI, you must adhere to two specific rules:

- The --var Flag: This is the standard flag used to pass runtime overrides to the pipeline.

- JSON-Compatible Formatting: Since the variable was defined as an array of string items in your pipeline.yml, the override must also be a valid JSON array.

Passing just taxi_types=yellow would likely result in a type mismatch error because the pipeline expects a list/array, not a single string.


### Question 4: Running with Dependencies

You've modified the ingestion/trips.py asset and want to run it plus all downstream assets. Which command should you use? 

- bruin run ingestion.trips --all
- bruin run ingestion/trips.py --downstream
- bruin run pipeline/trips.py --recursive
- bruin run --select ingestion.trips+

✅ Answer:
```code
bruin run ingestion/trips.py --downstream
```
Behavior: Executes the targeted asset first, then identifies all children in the lineage graph and executes them in order.

### Question 5: Quality Checks

You want to ensure the pickup_datetime column in your trips table never has NULL values. Which quality check should you add to your asset definition? 

- name: unique
- name: not_null
- name: positive
- name: accepted_values, value: [not_null]

✅ Answer:
```code
name: not_null
```
The not_null check is the standard validator used to ensure a column contains no empty or missing values.

If this check fails during a run, Bruin will flag it as an error, helping you catch data integrity issues before they propagate to your reports.

### Question 6: Lineage and Dependencies

After building your pipeline, you want to visualize the dependency graph between assets. Which Bruin command should you use?

- bruin graph
- bruin dependencies
- bruin lineage
- bruin show

✅ Answer:
```code
bruin lineage
```
bruin lineage - Displays the "Map" (the execution graph) so you can see which assets depend on others.

Question 7: First-Time Run

You're running a Bruin pipeline for the first time on a new DuckDB database. What flag should you use to ensure tables are created from scratch?

- --create
- --init
- --full-refresh
- --truncate


✅ Answer:
```code
--full-refresh
```
In Bruin (and similar data tools), the --full-refresh flag is the standard way to ignore existing state or incremental logic and rebuild everything from the ground up.

Initial Setup: When running against a brand-new DuckDB database, the tables don't exist yet. While some strategies might create them automatically, a full refresh ensures that the entire schema is properly initialized.

Overriding Incremental Logic: If you are using the time_interval or append strategies, Bruin normally only looks at new data. Using --full-refresh tells Bruin to drop the existing tables (if any) and recreate them using the entire history defined by your start_date.

Comparison of Run Flags

| Flag | Purpose |
|------|---------|
| `--full-refresh` | Drops and recreates all tables; processes all historical data from the start_date. |
| `--start-date` | Limits the run to a specific beginning point in time. |
| `--end-date` | Limits the run to a specific stopping point in time. |
| `--var` | Overrides specific pipeline variables (like taxi_types). |
 

## Troubleshoot project setup and execution 

### bruin clean . && bruin validate ./pipeline - not showing all aseets

No log files found, nothing to clean up...

Validating pipelines in './pipeline' for 'default' environment...

Pipeline: nyc_taxi (.)
  No issues found

✓ Successfully validated 1 assets across 1 pipeline, all good.
(my_project_env) niteshmishra@Mac hw5 % bruin validate ./pipeline/assets

Validating pipelines in './pipeline/assets' for 'default' environment...
An error occurred: no pipelines found in path './pipeline/assets'

```
we have a bit of a "good news, bad news" situation here.

The good news: Your syntax is now perfect! No warnings, no errors.
The bad news: It says "Validated 1 assets".

If your pipeline is complete, that number should be 4 (
    the Python ingestion, 
    the CSV seed, 
    the staging SQL, and 
    the report SQL). 
Since it only sees 1, Bruin is likely only looking at the root of your folder and not "recursively" searching through your assets subfolders.
```

```
Since your pipeline.yml doesn't define where the assets are, Bruin is just sitting in the root folder, seeing the pipeline.yml itself, and not looking into your assets/ subdirectories.

In Bruin, if you don't explicitly tell it where the assets live, it doesn't always go hunting for them recursively.

🛠️ The Fix: Add the assets path
You need to add a small section to your pipeline.yml to tell Bruin to look inside your folders. Add this block (usually at the bottom or just after start_date):
```

In pipeline.yml add assets path
```
YAML

# Add this section to tell Bruin where your files are!
assets:
  - path: assets/
```

🧪 Why it only found "1 asset" before:
It was likely counting the pipeline.yml itself as the "pipeline entity" or finding one file by accident in the root. By adding the assets path, you are giving Bruin a map to find your .py, .sql, and .asset.yml files.

### `bruin lineage` not showing recursive view

```bash
hw5 % bruin lineage ./pipeline/assets/staging/trips.sql

Lineage: 'staging.trips'

Upstream Dependencies
========================
- ingestion.trips (assets/ingestion/trips.py)
- ingestion.payment_lookup (assets/ingestion/payment_lookup.asset.yml)

Total: 2


Downstream Dependencies
========================
- reports.trips_report (assets/reports/trips_report.sql)

Total: 1
```

```bash
hw5 % bruin lineage ./pipeline/assets/reports/trips_report.sql

Lineage: 'reports.trips_report'

Upstream Dependencies
========================
- staging.trips (assets/staging/trips.sql)

Total: 1


Downstream Dependencies
========================
Asset has no downstream dependencies.
```

If Staging knows its parents, but Report only shows its immediate parent, it means Bruin is currently defaulting to a "shallow" lineage view (showing only one level up) rather than a "recursive" view.

In some versions of the Bruin CLI, bruin lineage on a specific file defaults to the immediate neighbors.

🛠️ The "Full Tree" Command
To see the entire ancestry all the way back to the ingestion files from the perspective of the report, try adding the --full or -f flag:

```bash
hw5 % bruin lineage ./pipeline/assets/reports/trips_report.sql --full

Lineage: 'reports.trips_report'

Upstream Dependencies
========================
- staging.trips (assets/staging/trips.sql)
- ingestion.trips (assets/ingestion/trips.py)
- ingestion.payment_lookup (assets/ingestion/payment_lookup.asset.yml)

Total: 3


Downstream Dependencies
========================
Asset has no downstream dependencies.
```

### bruin run failed

```bash
bruin run ./pipeline --start-date 2022-01-01 --end-date 2022-02-01
Analyzed the pipeline 'nyc_taxi' with 4 assets.

Pipeline: nyc_taxi (.)
  No issues found

✓ Successfully validated 4 assets across 1 pipeline, all good.

Interval: 2022-01-01T00:00:00Z - 2022-02-01T00:00:00Z

Starting the pipeline execution...

[17:22:32] Running:  ingestion.trips
[17:22:32] Running:  ingestion.payment_lookup
[17:22:32] Failed: ingestion.payment_lookup (0s)
[17:22:32] Failed: ingestion.trips (1ms)

==================================================

FAIL ingestion.payment_lookup UUU
FAIL ingestion.trips
UPSTREAM FAILED reports.trips_report
UPSTREAM FAILED staging.trips


bruin run completed with failures in 1ms

 ✗ Assets executed      2 failed / 2 skipped
 ✗ Quality checks       3 skipped


2 assets failed
├── ingestion.payment_lookup
│   └── destination connection duckdb-default not found
└── ingestion.trips
    └── there's no secret with the name 'duckdb-default'.
```

#### 🛠️ The Fix: Create the Connection
Bruin needs a connections.yml file to know where your DuckDB database lives.

Create a file named .bruin.yml (or connections.yml depending on your setup, but .bruin.yml in the root is the modern standard) in your hw5 folder.

Add the following configuration:
```yaml
connections:
  duckdb:
    duckdb-default: # Use the name as a key instead of a list item
      path: "duckdb.db"
```

#### 🔍 Why it's failing specifically:
ingestion.payment_lookup: It's looking for the connection to write the CSV data into.

ingestion.trips: Even though it's Python, you specified connection: duckdb-default in the metadata, so Bruin tries to verify that connection before it even starts the script.

#### 🚀 Let's verify the connections
After you create that file, run this command to see if Bruin "sees" the database now:

```bash
bruin connections list
If duckdb-default shows up in that list, you are cleared for takeoff!
```

output - 
```
hw5 % bruin connections list

Environment: default
+------+------+
| TYPE | NAME |
+------+------+
+------+------+

```

It should not be empty

#### 🧪 One small check on pipeline.yml
In your pipeline.yml, you already have:

```yaml
default_connections:
  duckdb: duckdb-default
```

This is perfect, but it only works if duckdb-default is actually defined in your environment's connections.

Try creating that .bruin.yml file and running the pipeline again.
