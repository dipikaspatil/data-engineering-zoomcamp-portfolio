# Python script to ingest a CSV:

import os
import pandas as pd
from sqlalchemy import create_engine
from tqdm import tqdm

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
CSV_URL = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"

TABLE_NAME = "taxi_data"
CHUNKSIZE = 100_000

# -----------------------------
# Ingestion logic
# -----------------------------
print("Starting ingestion process...")

print(f"Downloading data from: {CSV_URL}")

for i, chunk in enumerate(
    tqdm(
        pd.read_csv(
        CSV_URL,
        compression="gzip",
        chunksize=CHUNKSIZE),
        desc="Ingesting CSV chunks"
    )
):
    # Explicit datatype parsing (important columns)
    chunk["tpep_pickup_datetime"] = pd.to_datetime(
        chunk["tpep_pickup_datetime"]
    )
    chunk["tpep_dropoff_datetime"] = pd.to_datetime(
        chunk["tpep_dropoff_datetime"]
    )

    # Replace table on first chunk, append afterwards
    if i == 0:
        chunk.to_sql(
            name=TABLE_NAME,
            con=engine,
            if_exists="replace",
            index=False
        )
        print(f"Table '{TABLE_NAME}' created (chunk {i+1})")
    else:
        chunk.to_sql(
            name=TABLE_NAME,
            con=engine,
            if_exists="append",
            index=False
        )

print("Ingestion completed successfully.")