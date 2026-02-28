dlt is an open-source Python library that automates data loading from messy sources into structured tables.

## 1. Core Concepts

- Source: A function that groups related data resources.
- Resource: A generator or list that yields data (the actual data stream).
- Pipeline: The engine that moves data from source to destination.
- Destination: Where data lands (e.g., DuckDB, BigQuery, Snowflake).

## 2. Basic Pipeline Template

```python
import dlt

# 1. Define your data
data = [{"id": 1, "name": "Gemini"}, {"id": 2, "name": "User"}]

# 2. Configure the pipeline
pipeline = dlt.pipeline(
    pipeline_name="my_pipeline",
    destination="duckdb",       # or 'bigquery', 'snowflake', etc.
    dataset_name="raw_data"
)

# 3. Run it
info = pipeline.run(data, table_name="users")
print(info)
```

## 3. Useful Commands & Features

| Feature | Code / Description |
|--------|---------------------|
| Incremental Loading | `dlt.sources.incremental('created_at')` — loads only new or updated records |
| Write Disposition | `write_disposition='replace'` (overwrite) or `append` (default) |
| Schema Evolution | Automatic — new fields in JSON data are detected and added as new SQL columns |
| Credentials | Stored securely in `.dlt/secrets.toml` or via environment variables |

## 4. Normalization Rules
dlt handles the "JSON headache" automatically:

- Nested Dicts: Flattened into parent table columns (e.g., user__address__zip).

- Nested Lists: Split into sub-tables with a parent-child relationship (automatic joins).

## 5. CLI Quickstart

```bash
# Install dlt
pip install dlt

# Initialize a verified source (e.g., GitHub, HubSpot, Zendesk)
dlt init github duckdb

# Deploy to GitHub Actions (for scheduling)
dlt deploy github_pipeline.py github_actions
```

## 6. Destinations

| Database | Destination String |
|----------|--------------------|
| Local | duckdb, filesystem |
| Warehouse | bigquery, snowflake, redshift, databricks |
| Other | postgres, motherduck, lancedb |

## 7. REST API source example

Adding a REST API example is where dlt truly shines because it handles the pagination and nested JSON structures that usually make API integration a nightmare.

The below example demonstrates how to turn a standard API call into a dlt resource.

```python
import dlt
import requests

# 1. Define the resource (The Data Stream)
@dlt.resource(name="github_issues", write_disposition="append")
def get_issues(repository):
    url = f"https://api.github.com/repos/{repository}/issues"
    response = requests.get(url)
    response.raise_for_status()
    yield response.json()  # dlt automatically flattens this list of dicts

# 2. Setup the pipeline
pipeline = dlt.pipeline(
    pipeline_name="api_to_duckdb",
    destination="duckdb",
    dataset_name="github_data"
)

# 3. Run the pipeline
load_info = pipeline.run(get_issues("dlt-hub/dlt"))

print(load_info)
```

Key API Patterns
- Pagination: Use a while loop inside the resource function to fetch next pages and yield each page.

- Authentication: Pass tokens via headers in the requests.get() call.

- Secrets: Instead of hardcoding keys, use dlt.secrets.get("api_key") to pull from .dlt/secrets.toml.

### 1. Offset-Based Pagination (The Most Common)
Used when the API requires a limit (how many rows) and an offset (where to start).

```python
import dlt
import requests

@dlt.resource(name="users", write_disposition="replace")
def get_users_paginated():
    url = "https://api.example.com/users"
    limit = 100
    offset = 0
    
    while True:
        params = {"limit": limit, "offset": offset}
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # If the API returns an empty list, we are done
        if not data:
            break
            
        yield data  # dlt processes this batch while we fetch the next
        
        # Move to the next page
        offset += limit
```

### 2. Cursor/Link-Based Pagination (Modern APIs)
Used by APIs like GitHub or Stripe where the response gives you a "next page" URL or a cursor ID.

```python
@dlt.resource(name="github_events")
def get_github_events():
    url = "https://api.github.com/events"
    
    while url:
        response = requests.get(url)
        response.raise_for_status()
        
        yield response.json()
        
        # Look for the 'next' URL in the Link header (standard GitHub pattern)
        # .links is a helper in the 'requests' library
        url = response.links.get('next', {}).get('url')
```

### 3. Page-Number Pagination
Used when the API simply asks for ?page=1, ?page=2, etc.

```python
@dlt.resource(name="products")
def get_products():
    page = 1
    while True:
        response = requests.get(f"https://api.example.com/products?page={page}")
        data = response.json()
        
        if "items" not in data or len(data["items"]) == 0:
            break
            
        yield data["items"]
        page += 1
```

### Why this is "Best Practice" for dlt:
- Memory Safety: By yield-ing inside the loop, you never hold more than one page of data in your computer's RAM at a time.

- Early Loading: If you have 1,000 pages, dlt can start loading page #1 into your database while your script is still waiting for page #2 to download from the internet.

- Automatic Retries: If you wrap these in a dlt.resource, dlt can handle transient network errors for you.

## 8. Handling Secrets (.dlt/secrets.toml)
To keep your API keys safe, dlt looks for a secrets file in your project folder:

```ini

# .dlt/secrets.toml
[sources]
api_key = "your_super_secret_token"

[destination.duckdb_credentials]
database = "my_data.duckdb"
```

Pro Tip: The dlt rest_api helper
If the API follows standard patterns, you can use the built-in REST API source which allows you to define the entire API integration using just a configuration dictionary (no complex loops required).

## 9. Declarative REST API Source
The Declarative (Configuration-based) approach is the "modern" way to use dlt. Instead of writing loops for pagination and error handling, you simply define a dictionary that describes the API structure.

This is incredibly powerful because dlt handles the complexity of HTTP requests under the hood.

You can use the rest_api_source from the dlt library to map an API endpoint directly to a table.

```python
from dlt.sources.rest_api import rest_api_source

# 1. Define the API configuration
config = {
    "client": {
        "base_url": "https://api.github.com/repos/dlt-hub/dlt/",
        "auth": {
            "token": dlt.secrets.get("github_token") # Pulls from .dlt/secrets.toml
        }
    },
    "resources": [
        {
            "name": "issues",
            "endpoint": {
                "path": "issues",
                "params": {
                    "state": "open",
                    "per_page": 100
                },
                "paginator": "github" # dlt has built-in paginators for major APIs
            }
        }
    ]
}

# 2. Initialize the source
github_source = rest_api_source(config)

# 3. Run the pipeline
pipeline = dlt.pipeline(destination="duckdb", dataset_name="github_repo")
load_info = pipeline.run(github_source)
```

### 💡 Why use the Declarative approach?
- Automatic Pagination: It supports `offset, page, cursor, and specific headers` (like GitHub or Zendesk) out of the box.

- Built-in Retries: Automatically handles 5xx errors or rate limiting (429 errors).

- Cleaner Code: Your Python script stays focused on what data you want, rather than how to fetch it.

### 🔑 Adding a Secret (The .dlt/secrets.toml file)
To make the above code work securely, create a folder named .dlt in your project and a file named secrets.toml inside it:

```ini

# .dlt/secrets.toml
[sources]
github_token = "ghp_your_secret_token_here"
```

## Which one to choose?

| Use Python Function (`@resource`) if... | Use Declarative (`rest_api_source`) if... |
|---------------------------------------|------------------------------------------|
| The API is extremely non-standard | The API is a standard REST JSON API |
| You need to do complex data mangling before loading | You want to set up a pipeline in 5 minutes |
| You're already comfortable with `requests` | You want built-in pagination and retry logic |

## What happens behind the scene when we execute pipeline.run() ?

When you call pipeline.run(), dlt stops being just a Python library and starts acting like a mini-orchestrator. It isn’t just a "wrapper" for a SQL INSERT statement; it manages a multi-step lifecycle to ensure your data is structured, cleaned, and safely moved.

### 🏗️ The pipeline.run() Lifecycle

### 1. Extract (The "Yield" Phase)

dlt calls your @dlt.resource function. As your function yields data, dlt:

- Buffers the data: It doesn't load everything into memory. It collects a "batch" of items.

- Records State: If you are using incremental loading, dlt tracks the "last value" (e.g., the last timestamp) so it knows where to start next time.

### 2. Normalize (The "JSON to Table" Phase) (Transform)
This is where the magic happens. Before sending data to the database, dlt:

- Infers Schema: It looks at the JSON keys and values to decide if a field is an INT, TIMESTAMP, or STRING.

- - Flattens Nested Data: If it sees a nested dictionary, it flattens it. If it sees a list (a "one-to-many" relationship), it automatically creates a sub-table and generates a root_id to link the child rows back to the parent row.

Writes to Parquet/JSONL: It saves these normalized "files" into a local temporary storage folder (usually <pipeline_name>/load/).

### 3. Schema Sync (The "Gatekeeper" Phase)
Before the data hits the database, dlt checks the Destination Schema:

- New Columns: If your API added a new field, dlt runs an ALTER TABLE ... ADD COLUMN command automatically.

- Data Types: It ensures the incoming data matches the existing database column types.

- Version Control: It stores a versioned copy of your schema in a hidden table in your database (_dlt_loads).

### 4. Load (The "Copy" Phase)
Now that the files are ready and the tables exist, dlt performs the actual move:

- Optimized Loading: Instead of slow INSERT statements row-by-row, it uses high-speed "Bulk Load" commands like COPY (Postgres/Redshift) or INSERT INTO SELECT (BigQuery/Snowflake).

- Atomic Transactions: It ensures that a batch of data is either fully loaded or not loaded at all. If the power goes out mid-load, the database stays clean.

### 5. Cleanup & Tracking
Once the load is successful:

- Temporary Files: The local Parquet/JSONL files are deleted.

- Load Info: A summary object is returned to your Python script containing how many rows were loaded and how long it took.

### 📊 Summary

| Step | Action | Benefit |
|------|--------|---------|
| Extract | Iterate over generators | Low memory footprint |
| Normalize | Flatten JSON & create sub-tables | No manual SQL DDL needed |
| Sync | Compare & update schema | Handles API changes automatically |
| Load | Bulk file copy | Fast performance for large data |

### Pro-Tip for Debugging
If you want to see exactly what dlt is doing during run(), you can change your logging level in your script:

```python
import dlt
import logging

# This tells dlt to print every file move and SQL command to the console
logging.basicConfig(level=logging.INFO)

# ... your resource and pipeline code ...
pipeline.run(my_data, table_name="users")
```

### Visualizing the "File Room"
If you want to see the files manually without logging, you can peek into the hidden directory dlt creates while the script is running:

- extracted/: Raw data sits here briefly.

- normalized/: Cleaned, typed, and flattened files ready for the database.

- loaded/: A history of what was successfully sent (archived or deleted based on settings).

### 4. The dlt pipeline CLI (The better way)
Since you are in VS Code, you can open a terminal and run this command after your script finishes to see a "post-mortem" of the file movement:

```bash
dlt pipeline my_pipeline_name trace
```

This will show you exactly how many files were created, their sizes, and if any failed to load.

## 10 🔍 Inspecting the Pipeline Object

### 1. The trace (Audit Log)
The trace is a record of every "step" the pipeline took. It tells you exactly how many files were moved and how long each stage (Extract, Normalize, Load) took.Pythoninfo = pipeline.run(my_resource)

```python
# Get the trace of the last run
trace = pipeline.last_trace
print(trace.last_run_info) 


# This shows:
# - Number of files created
# - Total rows extracted
# - Start/End times for each step
```

### 2. The load_info (The Summary)
When you execute `info = pipeline.run()`, the info object is a goldmine of metadata about the file movement.

```python
print(info.dataset_name)      # Where the data went
print(info.loads_ids)         # Unique ID for this specific batch
print(info.metrics)           # Dictionary of rows/files processed
```

### 📁 Managing the "File Room" (Working Directory)
Every pipeline creates a local folder (usually in ~/.dlt/pipelines/ or your project root). 
The pipeline object gives you direct access to these paths:

| Property | Purpose |
|----------|---------|
| `pipeline.pipeline_storage` | The root path where all temp files live |
| `pipeline.working_dir` | The specific folder for the current run's files |
| `pipeline.drop()` | **Careful:** Deletes the local state and the destination dataset |


### 🛑 Important for your .gitignore

Since the pipeline object creates these local folders every time you run your script, make sure your .gitignore includes:

```plaintext
# Ignore dlt working directories and traces
.dlt/pipelines/
.dlt/packages/
```

## 11. 🤖 LLM-Powered Workflows with dlt

Modern data engineering with dlt shifts from "manual coding" to "AI-assisted scaffolding."

### 1. AI-Native Code Generation
dlt is designed to be "LLM-readable." Because you can define a source using a simple Python dictionary (Declarative REST API), an LLM can generate a full production-ready connector just by looking at an API's documentation.

The Workflow: Give an LLM (or Cursor) an API spec + the dlt documentation.

The Result: It generates the RESTAPIConfig dict, handles pagination, and sets up the resource decorators automatically.

Gemini said
In 2026, dlt has positioned itself as the "Data Layer" for LLMs. Because dlt is Python-first and uses a declarative approach, it is much easier for AI agents (like GPT-4, Claude 3.5/4, or specialized IDE agents like Cursor) to write and maintain data pipelines than traditional "black box" ETL tools.

Here is how you should include LLM-powered workflows in your cheatsheet.

🤖 LLM-Powered Workflows with dlt
Modern data engineering with dlt shifts from "manual coding" to "AI-assisted scaffolding."

### 1. AI-Native Code Generation
dlt is designed to be "LLM-readable." Because you can define a source using a simple Python dictionary (Declarative REST API), an LLM can generate a full production-ready connector just by looking at an API's documentation.

The Workflow: Give an LLM (or Cursor) an API spec + the dlt documentation.

The Result: It generates the RESTAPIConfig dict, handles pagination, and sets up the resource decorators automatically.

### 2. The Model Context Protocol (MCP)
dlt now supports MCP Servers. This allows your AI agent (in VS Code or Cursor) to "talk" directly to your data pipeline and your destination database.

What it does: The agent can see your table schemas, last load IDs, and even data samples.

Example Prompt: "Check why the 'sales_data' table failed to load and fix the schema mapping in my dlt script."

### 3. Loading Data into Vector Databases (RAG)
dlt isn't just for SQL anymore. It is a popular way to feed data into `Vector Stores for Retrieval-Augmented Generation (RAG)`.

```python
# Example: Loading and Embedding data into Qdrant
from dlt.destinations.qdrant import qdrant_adapter

pipeline = dlt.pipeline(destination='qdrant', dataset_name='knowledge_base')

# The adapter tells dlt which fields the LLM needs to embed
info = pipeline.run(
    qdrant_adapter(my_data, embed=["content", "title"])
)
```

### 4. LLM "Scaffolds"
dlt provides LLM Scaffolds (pre-defined templates). You can use the CLI to initialize a project that is optimized for an AI assistant:

```python
dlt init <source_name> <destination> --assistant cursor
```

This creates a .cursor/rules.mdc file that tells your AI agent exactly how to write dlt code correctly for your specific project.