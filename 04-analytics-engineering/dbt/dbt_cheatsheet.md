## Difference between ETL and ELT

# 🧾 ETL vs ELT — One-Page Cheatsheet

## 🔄 Definitions
**ETL (Extract → Transform → Load)**  
Data is transformed *before* loading into the data warehouse.

**ELT (Extract → Load → Transform)**  
Raw data is loaded first, then transformed *inside* the data warehouse.

## 🧱 Architecture Flow
**ETL:** Source → ETL Engine (Spark / Python) → Data Warehouse  
**ELT:** Source → Data Warehouse → Transform (SQL / dbt)

## 📊 Comparison
| Aspect | ETL | ELT |
|---|---|---|
| Transformation timing | Before load | After load |
| Transformation location | External system | Warehouse |
| Data loaded | Cleaned | Raw + modeled |
| Scalability | Limited | High |
| Flexibility | Low | High |
| Cost | Compute-heavy | Storage-heavy |
| Debugging | Harder | Easier |

## 🛠️ Tools
**ETL:** Spark, Airflow + Python, Informatica, Talend  
**ELT:** dbt, BigQuery, Snowflake, Redshift, Fivetran, Airbyte

## 🚀 Use ETL When
Legacy systems, limited warehouse compute, heavy pre-processing, strict exposure rules

## ⚡ Use ELT When
Cloud warehouses, analytics/BI, fast iteration, multiple models, dbt workflows

## 🧠 Key Takeaways
ETL = transform first  
ELT = load first  
`dbt = the T in ELT`

## 🎯 Interview Line
“ETL transforms data before loading; ELT transforms data inside the warehouse.”

# 🧾 dbt (Data Build Tool) Cheatsheet

dbt (data build tool) is a transformation tool used in ELT pipelines. It runs inside your data warehouse (BigQuery, Snowflake, Redshift) and uses SQL + Jinja for transformations, testing, and documentation. dbt is the "T" in ELT.

## Core Concepts

| Concept   | Description |
|-----------|-------------|
| Model     | SQL file that builds a table or view |
| ref()     | References another dbt model |
| source()  | References raw/source tables |
| Seed      | CSV files loaded as tables |
| Snapshot  | Tracks historical changes (SCD) |
| Test      | Data quality checks |
| Macro     | Reusable SQL logic |

## Common Commands

```bash
dbt init my_project
dbt run
dbt run --select model_name
dbt test
dbt compile
dbt seed
dbt docs generate
dbt docs serve
dbt clean
dbt debug
```

## Project Structure
```bash
models/
  staging/        # Clean & standardize raw data
  intermediate/   # Reusable transformations
  marts/          # Fact & dimension tables
```

### Example Models

### Staging Model
```sql
-- models/staging/stg_customers.sql
select
    id,
    upper(first_name) as first_name,
    upper(last_name) as last_name,
    created_at
from {{ source('raw', 'customers') }}
```

### Mart Model
```sql
-- models/marts/fct_orders.sql
select
    o.id as order_id,
    c.id as customer_id,
    c.first_name,
    c.last_name,
    o.amount
from {{ ref('stg_customers') }} c
join {{ ref('stg_orders') }} o
on c.id = o.customer_id
```

## Testing Example
```yaml
version: 2

models:
  - name: stg_customers
    columns:
      - name: id
        tests:
          - not_null
          - unique
```


## Materializations
| Type        | Description           |
| ----------- | --------------------- |
| view        | Default, lightweight  |
| table       | Fully materialized    |
| incremental | Only new/updated rows |
| ephemeral   | Temporary, in-memory  |


## Incremental Model Config
```sql
{{ config(materialized='incremental', unique_key='id') }}
```

## Best Practices

- Always use ref() to manage dependencies

- Keep staging models simple (no business logic)

- Put business logic in marts

- Add tests to critical columns

- Use dbt docs serve to view the DAG

## Useful Jinja Helpers

- {{ ref('model_name') }}

- {{ source('schema', 'table') }}

- {{ var('var_name') }}

- {{ config(...) }}

## TL;DR

- dbt = SQL-based transformation layer

- Models = tables/views

- Tests = data quality

- Docs = auto-generated

- Modern analytics engineering standard

## DBT projct structure - 

### dbt_project.yml

- The main configuration file for a dbt project.
- Think of it as the “settings file” that tells dbt:
    - What your project is called (name)

    - Where your models, macros, seeds, and tests live (source-paths, macro-paths, etc.)

    - Default configurations for your models, like whether they should be view, table, or incremental

    - Which profile to use (profile) to connect to your data warehouse (BigQuery, Snowflake, Redshift)

    - How seeds and snapshots should behave

- Every dbt project must have a dbt_project.yml at the root — without it, dbt won’t know how to build your models.

```yaml
# dbt_project.yml
name: 'my_dbt_project'         # Project name
version: '1.0.0'
config-version: 2

# Where your models live
source-paths: ["models"]
analysis-paths: ["analysis"]
test-paths: ["tests"]
data-paths: ["data"]
macro-paths: ["macros"]

# The target database and schema for dbt models
profile: 'default'

# Default model configurations
models:
  my_dbt_project:               # Replace with your project name
    +materialized: view         # Default materialization for all models
    staging:
      +materialized: view       # Staging models as views
    marts:
      +materialized: table      # Marts as tables or incremental
    intermediate:
      +materialized: ephemeral  # Intermediate models as ephemeral

# Seeds configuration (CSV files loaded into warehouse)
seeds:
  my_dbt_project:
    +quote_columns: false
    +schema: analytics

# Snapshots configuration
snapshots:
  my_dbt_project:
    +target_schema: snapshots

```

- If you put a SQL file in models/staging/, dbt will know to build it as a view in your warehouse.
- If you put a SQL file in models/marts/, dbt will build it as a table.
- It also tells dbt where to find seeds, snapshots, tests, and macros.

💡 TL;DR: dbt_project.yml is like the “control panel” for your dbt project. It tells dbt how and where to build all your models.

## Macros

### What is a dbt Macro?

- A macro is like a reusable function in dbt.
- Written in Jinja, which is dbt’s templating language.
- Macros let you reuse SQL snippets, apply dynamic logic, or build dynamic queries across multiple models.
- Think of them like functions in Python or methods in programming, but for SQL in dbt.

### Why Use Macros?

- Avoid repeating SQL — write once, use many times.
- Dynamic queries — e.g., automatically reference tables, schema, or dates.
- Maintain consistency — changes in one macro propagate everywhere it’s used.
- Parameterization — you can pass arguments to macros.

### Example 1: Simple Macro
```sql
-- macros/uppercase.sql
{% macro uppercase(column_name) %}
    upper({{ column_name }})
{% endmacro %}
```

Usage in a model:
```sql
select
    {{ uppercase('first_name') }} as first_name,
    {{ uppercase('last_name') }} as last_name
from {{ ref('stg_customers') }}
```
Result: first_name and last_name are converted to uppercase dynamically.

### Example 2: Macro with Arguments
```sql
-- macros/calc_tax.sql
{% macro calc_tax(amount, rate=0.1) %}
    {{ amount }} * {{ rate }}
{% endmacro %}
```

Usage:
```sql
select
    order_id,
    {{ calc_tax('amount') }} as tax
from {{ ref('fct_orders') }}
```

This calculates a 10% tax for each order, and you can override the rate if needed.

### Example 3: Using Macros for Reusable SQL Logic
```sql
-- macros/join_customers_orders.sql
{% macro join_customers_orders(customers, orders) %}
    select
        c.id as customer_id,
        c.first_name,
        c.last_name,
        o.id as order_id,
        o.amount
    from {{ ref(customers) }} c
    join {{ ref(orders) }} o
    on c.id = o.customer_id
{% endmacro %}
```

Usage:
```sql
{{ join_customers_orders('stg_customers', 'stg_orders') }}
```

Instead of writing the JOIN logic multiple times, you can reuse this macro everywhere.

### TL;DR

- Macro = reusable SQL function in dbt
- Written in Jinja
- Use it for dynamic queries, repeated logic, parameterization
- Makes your project cleaner, easier to maintain, and consistent

## DBT Models

### What is a dbt Model?

- A dbt model is a SQL file that defines a table or view in your data warehouse.
- When you run dbt run, dbt compiles your model and creates a table or view in the target schema.
- Models are the “T” in ELT — they transform raw data into analytics-ready data.

### dbt Key Points

1. Models
    - Models are SQL files.
    - Each file in the `models/` folder is a dbt model.  
  **Example:** `models/staging/stg_customers.sql`

2. Materialization
    - A model can be one of the following:
        - `view`
        - `table`
        - `incremental`
        - `ephemeral`
    - Default materialization is `view`, but it can be configured per model.

3. Dependency Management
    - Use `{{ ref('other_model') }}` to reference other models.
    - dbt automatically builds a DAG (Directed Acyclic Graph) based on `ref()` calls.

4. Testing
    - Tests can be defined in `schema.yml` for each model.
    - Common test examples:
        - `unique`
        - `not_null`
        - `relationships`

### Example 1: Simple Staging Model
```sql
-- models/staging/stg_customers.sql
select
    id,
    upper(first_name) as first_name,
    upper(last_name) as last_name,
    created_at
from {{ source('raw', 'customers') }}
```

- This model standardizes customer names.
- References raw data using {{ source(...) }}.

### Example 2: Fact Model Using ref()
```sql
-- mart for end users
-- models/marts/fct_orders.sql
select
    o.id as order_id,
    c.id as customer_id,
    c.first_name,
    c.last_name,
    o.amount
from {{ ref('stg_customers') }} c
join {{ ref('stg_orders') }} o
on c.id = o.customer_id
```

- Uses ref() to reference staging models.
- Ensures dbt knows the build order.

### Example 3: Incremental Model
```sql
-- models/marts/fct_orders_incremental.sql
{{ config(materialized='incremental', unique_key='id') }}

select
    id,
    customer_id,
    amount,
    order_date
from {{ ref('stg_orders') }}

{% if is_incremental() %}
    where order_date > (select max(order_date) from {{ this }})
{% endif %}
```
- Only loads new or updated rows.
- Useful for large tables.

### Best Practices for Models

- Use staging models for cleaning/standardizing raw data.
- Use marts for business logic, metrics, and fact/dimension tables.
- Keep models modular — one transformation per model if possible.
- Always use ref() instead of hardcoding table names.
- Add tests in schema.yml to ensure data quality.

## DBT seeds

### What is a dbt Seed?

- Seed files are CSV files that you include in your dbt project.
- dbt can load these CSVs directly into your data warehouse as tables.
- They are useful for static reference data like country codes, product categories, lookup tables, or configuration values.
- Seed tables behave just like regular dbt models, and you can reference them using {{ ref() }}.

### How to Use dbt Seeds

1. Create a data/ folder in your dbt project.
2. Add a CSV file. Example: data/countries.csv
    ```csv
    country_code,country_name
    US,United States
    CA,Canada
    GB,United Kingdom
    ```
3. Run the seed command:
    ```sql
    dbt seed
    ```
    - dbt will create a table in your warehouse, usually in your default schema.

4. Reference the seed in your models:
    ```sql
    select
        c.country_code,
        c.country_name,
        o.order_id,
        o.amount
    from {{ ref('countries') }} c
    join {{ ref('stg_orders') }} o
    on c.country_code = o.country_code
    ```

### Seed Configurations (in dbt_project.yml)
```yaml
seeds:
  my_dbt_project:
    +quote_columns: false   # Don’t quote column names
    +schema: analytics      # Optional: specify target schema
```

## DBT sanpshots

### What is a dbt Snapshot?

- Snapshots allow you to track changes in your source data over time.
- They are useful for slowly changing dimensions (SCDs) — e.g., customer info that changes but you want to keep history.
- dbt creates a table that records old and new versions of rows, so you can see how data evolved.

### How Snapshots Work

- A snapshot is defined in the snapshots/ folder.
- Each snapshot has:
    1. Unique key – identifies the row (like id).
    2. Check columns – columns that, if changed, create a new version.
- dbt will insert a new row whenever data changes in the check columns, and mark the previous row as inactive.

### Example Snapshot

```sql
-- snapshots/customers_snapshot.sql
{% snapshot customers_snapshot %}

    {{
      config(
        target_schema='snapshots',
        unique_key='id',
        strategy='check',
        check_cols=['first_name','last_name','email']
      )
    }}

    select
        id,
        first_name,
        last_name,
        email,
        updated_at
    from {{ source('raw','customers') }}

{% endsnapshot %}
```

Explanation:

- strategy='check' → dbt checks columns listed in check_cols to see if a row has changed.
- unique_key='id' → identifies the row uniquely.
- target_schema='snapshots' → where snapshot table will be created.

### Running Snapshots
```sql
dbt snapshot
```
- This builds the snapshot tables in your warehouse.
- Each run updates the history table with new versions if data changed.

### Use Cases

- Track customer profile changes
- Track price changes for products
- Track status changes in orders
- Useful for audit and historical analysis

## DBT tests

### What are dbt Tests?

- Tests in dbt are data quality checks you define to ensure your models are producing correct data.
- They are written declaratively in YAML, not SQL.
- dbt runs tests with the command:
    ```sql
    dbt test
    ```
- Tests can be built-in or custom.

### Built-in Tests

dbt provides common tests you can apply to columns in your models:

| Test Name         | Description                               |
| ----------------- | ----------------------------------------- |
| `unique`          | Ensures all values in a column are unique |
| `not_null`        | Ensures no nulls in the column            |
| `accepted_values` | Ensures values are from a predefined list |
| `relationships`   | Ensures foreign key relationships exist   |


#### Example: Basic Column Tests

```yaml
version: 2

models:
  - name: stg_customers
    columns:
      - name: id
        tests:
          - not_null
          - unique
      - name: country
        tests:
          - accepted_values:
              values: ['US', 'CA', 'GB']
```

- id column must be unique and not null.
- country column must only contain US, CA, GB.

#### Example: Relationships Test

```yaml
version: 2

models:
  - name: fct_orders
    columns:
      - name: customer_id
        tests:
          - relationships:
              to: ref('stg_customers')
              field: id
```
- Ensures that customer_id in fct_orders exists in stg_customers.id.

### Custom Tests

- You can create SQL files in tests/ folder.
- A custom test returns rows that fail the test.
- dbt considers a test failed if the query returns any rows.

Example custom test:
```sql
-- tests/orders_amount_positive.sql
select *
from {{ ref('fct_orders') }}
where amount < 0
```
- Returns any orders with negative amount.

### Running Tests
```bash
dbt test
```

- dbt executes all tests defined in YAML or custom SQL.
- Failing tests are reported in the terminal.

## DBT analyses

### What are dbt Analyses?

- Analyses are SQL files used for ad-hoc or exploratory queries in dbt.
- Stored in the analysis/ folder of your project.
- Unlike models, analyses are not materialized in your warehouse automatically — you run them manually.
- Useful for things like reports, experiments, or intermediate queries.

### Key Points

- Stored in analysis/ folder.
- Can reference models using {{ ref('model_name') }}.
- Run manually with:
```bash
dbt run-operation <analysis_name>
```
or simply query them through dbt IDEs.

### Example Analysis

```sql
-- analysis/top_customers.sql
select
    c.id as customer_id,
    c.first_name,
    c.last_name,
    sum(o.amount) as total_spent
from {{ ref('stg_customers') }} c
join {{ ref('fct_orders') }} o
on c.id = o.customer_id
group by 1, 2, 3
order by total_spent desc
limit 10
```

- Shows top 10 customers by total spending.
- Can be used for reporting or exploratory analysis.

### Differences Between Models and Analyses

| Feature        | Model                          | Analysis                 |
| -------------- | ------------------------------ | ------------------------ |
| Materialized   | Yes (table, view, incremental) | No (run manually)        |
| Purpose        | Transform data for analytics   | Explore / ad-hoc queries |
| DAG dependency | Part of dbt DAG                | Not part of DAG          |
| Reusable       | Yes, can be referenced         | Usually one-off          |

## DBT sources

### What are dbt Sources?

- dbt Sources represent raw data tables that already exist in your data warehouse.
- They are not created by dbt — dbt only references them.
- Sources are defined in YAML files, usually alongside your models.
- They help with:
    - Clear separation between raw data and transformed data
    - Documentation
    - Data freshness & testing

## Why Use Sources?

Without sources:
```sql
select * from raw.customers
```

With sources:
```sql
select * from {{ source('raw', 'customers') }}
```

### Benefits:

- Lineage tracking (raw → staging → marts)
- Built-in tests (freshness, not_null)
- Safer refactoring (schema/table changes in one place)
- Better docs

## Defining a Source (YAML)
```yaml
version: 2

sources:
  - name: raw
    schema: raw
    tables:
      - name: customers
      - name: orders
```

### 📍 Usually placed in:
```bash
models/staging/schema.yml
```

### Using a Source in a Model
```sql
select
    id,
    first_name,
    last_name,
    created_at
from {{ source('raw', 'customers') }}
```
- raw → source name
- customers → table name

### Adding Tests to Sources
```yaml
version: 2

sources:
  - name: raw
    schema: raw
    tables:
      - name: customers
        columns:
          - name: id
            tests:
              - not_null
              - unique
```

Run with:
```bash
dbt test
```

### Source Freshness (Very Important 🚨)

Freshness checks ensure data is arriving on time.

```yaml
sources:
  - name: raw
    schema: raw
    tables:
      - name: orders
        freshness:
          warn_after:
            count: 12
            period: hour
          error_after:
            count: 24
            period: hour
        loaded_at_field: updated_at
```

Run freshness checks:
```bash
dbt source freshness
```

## Sources vs Models
| Feature        | Source     | Model              |
| -------------- | ---------- | ------------------ |
| Created by dbt | ❌ No       | ✅ Yes              |
| Defined in     | YAML       | SQL                |
| Represents     | Raw tables | Transformed tables |
| Can be tested  | ✅ Yes      | ✅ Yes              |
| Used with      | `source()` | `ref()`            |


## Best Practices

- Always use sources for raw data
- Never ref() raw tables
- Add freshness checks for critical pipelines
- Use sources → staging → marts pattern