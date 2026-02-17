import os
import pandas as pd
import urllib.request
from google.cloud import bigquery

# -----------------------------
# CONFIG — update for your project
# -----------------------------
PROJECT_ID = "de-zoomcamp-2026-486900"  # Your GCP project
DATASET_ID = "nytaxi"
TABLE_ID = "fhv_tripdata"

client = bigquery.Client(project=PROJECT_ID)

# Base URL for CSV gzip files in DataTalksClub GitHub releases
FHV_BASE_URL = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv/fhv_tripdata_"

YEARS = [2019]
MONTHS = [f"{i:02d}" for i in range(1, 13)]

DOWNLOAD_DIR = "./tmp_fhv"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# -----------------------------
# FUNCTION TO LOAD SINGLE FILE
# -----------------------------
def load_file(year, month):
    url = f"{FHV_BASE_URL}{year}-{month}.csv.gz"
    local_path = os.path.join(DOWNLOAD_DIR, f"{year}-{month}.csv.gz")

    print(f"Downloading {url} ...")
    urllib.request.urlretrieve(url, local_path)
    print(f"Downloaded {local_path}")

    # Read CSV with gzip
    df = pd.read_csv(local_path, compression='gzip', low_memory=False)

    # Load into BigQuery
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    job = client.load_table_from_dataframe(
        df,
        table_ref,
        job_config=bigquery.LoadJobConfig(
            write_disposition="WRITE_APPEND"
        )
    )
    job.result()  # Wait for job to finish
    print(f"Loaded {year}-{month} into BigQuery")

# -----------------------------
# MAIN LOOP
# -----------------------------
if __name__ == "__main__":
    for year in YEARS:
        for month in MONTHS:
            load_file(year, month)

    print("✅ All FHV tripdata data loaded into BigQuery!")
