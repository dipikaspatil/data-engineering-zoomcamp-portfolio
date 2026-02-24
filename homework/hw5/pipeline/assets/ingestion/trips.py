""" @bruin

# Set the asset name (recommended pattern: schema.asset_name).
# - Convention in this module: use an `ingestion.` schema for raw ingestion tables.
name: ingestion.trips

# Set the asset type.
# Docs: https://getbruin.com/docs/bruin/assets/python
type: python

# Pick a Python image version (Bruin runs Python in isolated environments).
# Example: python:3.11
image: python:3.11

# Set the connection.
connection: duckdb-default

# Choose materialization (optional, but recommended).
# Bruin feature: Python materialization lets you return a DataFrame (or list[dict]) and Bruin loads it into your destination.
# This is usually the easiest way to build ingestion assets in Bruin.
# Alternative (advanced): you can skip Bruin Python materialization and write a "plain" Python asset that manually writes
# into DuckDB (or another destination) using your own client library and SQL. In that case:
# - you typically omit the `materialization:` block
# - you do NOT need a `materialize()` function; you just run Python code
# Docs: https://getbruin.com/docs/bruin/assets/python#materialization

materialization:
  # choose `table` or `view` (ingestion generally should be a table)
  type: table
  # pick a strategy.
  # suggested strategy: append
  strategy: append

# Define output columns (names + types) for metadata, lineage, and quality checks.
# Tip: mark stable identifiers as `primary_key: true` if you plan to use `merge` later.
# Docs: https://getbruin.com/docs/bruin/assets/columns
columns:
  - name: vendor_id
    type: INTEGER
  - name: pickup_datetime
    type: TIMESTAMP
  - name: dropoff_datetime
    type: TIMESTAMP
  - name: passenger_count
    type: INTEGER
  - name: trip_distance
    type: FLOAT
  - name: rate_code_id
    type: INTEGER
  - name: store_and_fwd_flag
    type: STRING
  - name: payment_type_id
    type: INTEGER
  - name: fare_amount
    type: FLOAT
    description: The total fare amount for the trip.

@bruin """

import os
import pandas as pd
import json

# Add imports needed for your ingestion (e.g., pandas, requests).
# - Put dependencies in the nearest `requirements.txt` (this template has one at the pipeline root).
# Docs: https://getbruin.com/docs/bruin/assets/python


# Only implement `materialize()` if you are using Bruin Python materialization.
# If you choose the manual-write approach (no `materialization:` block), remove this function and implement ingestion
# as a standard Python script instead.
def materialize():
    """
    Implement ingestion using Bruin runtime context.

    Required Bruin concepts to use here:
    - Built-in date window variables:
      - BRUIN_START_DATE / BRUIN_END_DATE (YYYY-MM-DD)
      - BRUIN_START_DATETIME / BRUIN_END_DATETIME (ISO datetime)
      Docs: https://getbruin.com/docs/bruin/assets/python#environment-variables
    - Pipeline variables:
      - Read JSON from BRUIN_VARS, e.g. `taxi_types`
      Docs: https://getbruin.com/docs/bruin/getting-started/pipeline-variables

    Design TODOs (keep logic minimal, focus on architecture):
    - Use start/end dates + `taxi_types` to generate a list of source endpoints for the run window.
    - Fetch data for each endpoint, parse into DataFrames, and concatenate.
    - Add a column like `extracted_at` for lineage/debugging (timestamp of extraction).
    - Prefer append-only in ingestion; handle duplicates in staging.
    """
    # Bruin provides these dates based on your pipeline.yml or CLI flags
    start_date = os.environ.get("BRUIN_START_DATE")

    # We'll use the year and month from the start_date to build the URL
    # Example start_date: "2022-01-01"
    year = start_date[:4]
    month = start_date[5:7]

    # Get variables (like taxi_type) from the environment
    vars = json.loads(os.environ.get("BRUIN_VARS", "{}"))
    taxi_type = vars.get("taxi_types", ["yellow"])[0]

    url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/{taxi_type}_tripdata_{year}-{month}.parquet"

    print(f"Downloading: {url}")
    df = pd.read_parquet(url)

    # Add a column for lineage tracking
    df['taxi_type'] = taxi_type

    # return final_dataframe
    return df


