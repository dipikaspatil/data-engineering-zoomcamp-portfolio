# Python script to ingest a CSV:

import os
import pandas as pd
from sqlalchemy import create_engine

# -----------------------------
# Database connection settings
# -----------------------------
user = os.environ.get("POSTGRES_USER", "root")
password = os.environ.get("POSTGRES_PASSWORD", "root")
db = os.environ.get("POSTGRES_DB", "ny_taxi")
host = os.environ.get("POSTGRES_HOST", "postgres")

engine = create_engine(f"postgresql://{user}:{password}@{host}:5432/{db}")

# -----------------------------
# Dataset configuration
# -----------------------------
GREEN_TAXI_PARQUET_FILE = "/data/green_tripdata_2025-11.parquet"  # Path inside container
TAXI_ZONE_FILE = "/data/taxi_zone_lookup.csv"  # Path inside container

GREEN_NY_TAXI_TABLE = "green_ny_taxi_data"
TAXI_ZONES_TABLE = "zones"

CHUNKSIZE = 100_000

# -----------------------------
# Ingest Green Taxi data
# -----------------------------

print("Starting ingestion of Green Taxi data...")

# Read Green taxi Parquet in chunks
# pd.read_parquet doesn't have chunksize parameter, so we read whole file
# then split manually for large files

df = pd.read_parquet(GREEN_TAXI_PARQUET_FILE)
total_rows = len(df)
print(f"Total rows in Parquet: {total_rows}")

for i, start in enumerate(range(0, total_rows, CHUNKSIZE)):
    chunk = df.iloc[start:start+CHUNKSIZE].copy()
    
    # Explicitly parse datetime columns (green taxi)
    if 'lpep_pickup_datetime' in chunk.columns:
        chunk['lpep_pickup_datetime'] = pd.to_datetime(chunk['lpep_pickup_datetime'])
    if 'lpep_dropoff_datetime' in chunk.columns:
        chunk['lpep_dropoff_datetime'] = pd.to_datetime(chunk['lpep_dropoff_datetime'])
    
    # Write to Postgres. First chunk replaces table, rest append
    if i == 0:
        chunk.to_sql(
            name=GREEN_NY_TAXI_TABLE,
            con=engine,
            if_exists='replace',
            index=False
        )
        print(f"Table '{GREEN_NY_TAXI_TABLE}' created (chunk {i+1})")
    else:
        chunk.to_sql(
            name=GREEN_NY_TAXI_TABLE,
            con=engine,
            if_exists='append',
            index=False
        )

print(f"Ingestion for '{GREEN_NY_TAXI_TABLE}' completed successfully.")

# -----------------------------
# Ingest Taxi Zones data
# -----------------------------

print("Starting ingestion of Taxi Zones data...")

# Read taxi zones csv file
df_zone = pd.read_csv(TAXI_ZONE_FILE)

df_zone.to_sql(
    name=TAXI_ZONES_TABLE,
    con=engine,
    if_exists='replace',
    index=False
)

print(f"Ingestion for '{TAXI_ZONES_TABLE}' completed successfully.")