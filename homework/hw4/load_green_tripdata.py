import os
import pandas as pd
import urllib.request
from google.cloud import bigquery

# -----------------------------
# CONFIG
# -----------------------------
PROJECT_ID = "de-zoomcamp-2026-486900"
DATASET_ID = "nytaxi"
TABLE_ID = "green_tripdata"

client = bigquery.Client(project=PROJECT_ID)

GREEN_BASE_URL = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_"

YEARS = [2019, 2020]
MONTHS = [f"{i:02d}" for i in range(1, 13)]

DOWNLOAD_DIR = "./tmp_green"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# -----------------------------
# FUNCTION
# -----------------------------
def load_file(year, month):
    url = f"{GREEN_BASE_URL}{year}-{month}.csv.gz"
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
    job.result()
    print(f"Loaded {year}-{month} into BigQuery")

# -----------------------------
# MAIN LOOP
# -----------------------------
if __name__ == "__main__":
    for year in YEARS:
        for month in MONTHS:
            load_file(year, month)

    print("✅ All green taxi CSV data loaded into BigQuery!")
