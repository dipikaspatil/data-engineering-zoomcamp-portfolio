# Phase 5 - dbt layer (analytics)

This should sit between your raw/staging warehouse tables and the dashboard layer.

## Goal:

- convert raw ingested data into clean, query-friendly analytics models
- standardize field names and timestamps
- create marts specifically for dashboard use

## What Phase 5 should include:

- staging models
    - stg_geo_data
    - stg_aviation_data
    - stg_finance_data

- intermediate models if needed
    - unify schemas
    - deduplicate
    - normalize timestamps

- marts
    - mart_event_volume_by_hour
    - mart_event_volume_by_source
    - mart_latest_geo_events
    - mart_finance_symbol_activity
    - mart_aviation_activity

## Clean story:
```
stream ingestion → BigQuery raw tables → dbt models → dashboard
```

## dbt structure

```
models/
  staging/
    stg_geo_data.sql
    stg_aviation_data.sql
    stg_finance_data.sql

  intermediate/
    int_geo_clean.sql
    int_aviation_clean.sql
    int_finance_clean.sql
    int_events_unified.sql

  marts/
    mart_event_volume_by_hour.sql
    mart_event_volume_by_source.sql
    mart_geo_activity.sql
    mart_aviation_activity.sql
    mart_finance_activity.sql
```

## What each layer should do

### 1. Staging layer

Purpose: clean raw tables with minimal transformation.

For each source:

- rename columns consistently
- cast types correctly
- standardize timestamps
- remove obvious bad records
- keep it close to source data

Examples:

- stg_geo_data
- stg_aviation_data
- stg_finance_data

### 2. Intermediate layer

Purpose: apply business logic and make the data easier to use.

Typical tasks:

- deduplication
- timestamp normalization
- source tagging
- field standardization
- optional union into common schema

Especially useful:

- int_events_unified

Unified schema:

- event_id
- source_type
- event_timestamp
- event_date
- event_hour
- event_type
- record_source
- latitude / longitude for geo when present
- symbol for finance when present
- flight_id or aircraft identifier for aviation when present

### 3. Mart layer

Purpose: dashboard-ready models.

These should be simple and directly queryable by BI tools.

Marts:

- mart_event_volume_by_hour
    - Columns:
        - event_date
        - event_hour
        - source_type
        - event_count
    - Use for:
        - line chart of records over time

- mart_event_volume_by_source
    - Columns:
        - source_type
        - event_count
    - Use for:
        - bar or pie chart by domain

- mart_geo_activity
    - Columns:
        - event_date
        - event_hour
        - geo_event_type
        - location_name
        - event_count
    - Use for:
        - geo trends
        - recent geo activity

- mart_aviation_activity
    - Columns:
        - event_date
        - event_hour
        - aviation_event_type
        - flight_id
        - event_count
    - Use for:
        - flight event volume
        - activity by type

- mart_finance_activity
    - Columns:
        - event_date
        - event_hour
        - symbol
        - update_count
    - Use for:
        - top active symbols
        - finance update trends

## Initial 6 models to unlock phase6

- stg_geo_data
- stg_aviation_data
- stg_finance_data
- int_events_unified
- mart_event_volume_by_hour
- mart_event_volume_by_source

## deliverables by phase 5

- dbt project initialized
- sources defined
- staging models for 3 domains
- at least 1 intermediate unified model
- at least 2 mart models
- tests on key columns
- documentation for model lineage

## priority order
- stg_geo_data
- stg_aviation_data
- stg_finance_data
- int_events_unified
- mart_event_volume_by_hour
- mart_event_volume_by_source

## dbt project structure

```
dbt_omnistream/
  dbt_project.yml
  models/
    staging/
      sources.yml
      stg_geo_data.sql
      stg_aviation_data.sql
      stg_finance_data.sql

    intermediate/
      int_events_unified.sql

    marts/
      mart_event_volume_by_hour.sql
      mart_event_volume_by_source.sql

    schema.yml
```

## Commands to run

```bash
dbt debug
dbt deps
dbt seed
dbt run
dbt test

# only one phase
dbt run --select staging intermediate marts
dbt test --select staging intermediate marts

# model by model
dbt run --select stg_geo_data stg_aviation_data stg_finance_data
dbt run --select int_events_unified
dbt run --select mart_event_volume_by_hour mart_event_volume_by_source
dbt test
```

## implementation order

- Step A - Get sources.yml working.
- Step B - Build stg_geo
- Step C - Build stg_aviation
- Step D - Build stg_finance
- Step E - Build int_events_unified
- Step F - Build the two marts

## Implementation

```bash
dbt run --select "stg_geo stg_finance stg_aviation"

# Output
...
21:00:09  3 of 3 START sql view model omnistream_gold.stg_geo ............................ [RUN]
21:00:09  1 of 3 START sql view model omnistream_gold.stg_aviation ....................... [RUN]
21:00:09  2 of 3 START sql view model omnistream_gold.stg_finance ........................ [RUN]
21:00:10  3 of 3 OK created sql view model omnistream_gold.stg_geo ....................... [CREATE VIEW (0 processed) in 1.40s]
21:00:10  1 of 3 OK created sql view model omnistream_gold.stg_aviation .................. [CREATE VIEW (0 processed) in 1.40s]
21:00:10  2 of 3 OK created sql view model omnistream_gold.stg_finance ................... [CREATE VIEW (0 processed) in 1.40s]
...
21:00:10  Finished running 3 view models in 0 hours 0 minutes and 3.48 seconds (3.48s).
21:00:11
21:00:11  Completed successfully
...

dbt run --select int_events_unified

# Output

...
21:01:43  1 of 1 START sql view model omnistream_gold.int_events_unified ................. [RUN]
21:01:45  1 of 1 OK created sql view model omnistream_gold.int_events_unified ............ [CREATE VIEW (0 processed) in 1.71s]
21:01:45
21:01:45  Finished running 1 view model in 0 hours 0 minutes and 3.57 seconds (3.57s).
21:01:45
21:01:45  Completed successfully
...

dbt run --select "mart_event_volume_by_hour mart_event_volume_by_source"

# Output

...
21:03:12  2 of 2 START sql table model omnistream_gold.mart_event_volume_by_source ....... [RUN]
21:03:12  1 of 2 START sql table model omnistream_gold.mart_event_volume_by_hour ......... [RUN]
21:03:16  1 of 2 OK created sql table model omnistream_gold.mart_event_volume_by_hour .... [CREATE TABLE (3.0 rows, 13.9 KiB processed) in 3.42s]
21:03:16  2 of 2 OK created sql table model omnistream_gold.mart_event_volume_by_source .. [CREATE TABLE (3.0 rows, 13.7 KiB processed) in 3.43s]
21:03:16
21:03:16  Finished running 2 table models in 0 hours 0 minutes and 5.69 seconds (5.69s).
21:03:16
21:03:16  Completed successfully
...

## Test

dbt test --select "int_events_unified mart_event_volume_by_hour mart_event_volume_by_source"

# Output
Complete successfully

## Validate the outputs with:

bq query --use_legacy_sql=false \
'select * from `de-zoomcamp-2026-486900.omnistream_gold.mart_event_volume_by_source`'

# Output
+-------------+-------------+
| source_type | event_count |
+-------------+-------------+
| aviation    |         560 |
| geo         |          23 |
| finance     |           4 |
+-------------+-------------+

(venv) niteshmishra@Mac dbt % bq query --use_legacy_sql=false \
'select * from `de-zoomcamp-2026-486900.omnistream_gold.mart_event_volume_by_hour`
 order by event_date desc, event_hour desc
 limit 20'

 # Output 
 
+------------+------------+-------------+-------------+
| event_date | event_hour | source_type | event_count |
+------------+------------+-------------+-------------+
| 2026-03-30 |          9 | geo         |           8 |
| 2026-03-30 |          8 | geo         |           3 |
| 2026-03-30 |          1 | geo         |           6 |
| 2026-03-30 |          0 | geo         |           6 |
| 2026-03-30 |          0 | finance     |           4 |
| 2026-03-30 |          0 | aviation    |         560 |
+------------+------------+-------------+-------------+


dbt run --select int_events_unified

# Output

...
21:09:48
21:09:49  1 of 1 START sql view model omnistream_gold.int_events_unified ................. [RUN]
21:09:51  1 of 1 OK created sql view model omnistream_gold.int_events_unified ............ [CREATE VIEW (0 processed) in 1.59s]
21:09:51
21:09:51  Finished running 1 view model in 0 hours 0 minutes and 3.42 seconds (3.42s).
21:09:51
21:09:51  Completed successfully
...


```

Note - In virtual envt - install 

```bash
python3 -m pip install --upgrade pip

which -a dbt
# Output
/Users/niteshmishra/new/data-engineering-zoomcamp-portfolio/08-capstone/docker/venv/bin/dbt


python3 -m pip install dbt-bigquery
# Output
dbt --version
Core:
  - installed: 1.11.7
  - latest:    1.11.7 - Up to date!

Plugins:
  - bigquery: 1.11.1 - Up to date!

python3 -m site --user-base
# Output
/Users/niteshmishra/Library/Python/3.13

export PATH="$HOME/Library/Python/3.11/bin:$PATH"



```