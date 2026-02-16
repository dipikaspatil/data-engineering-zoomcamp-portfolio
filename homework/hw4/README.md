## Cloud Setup Guide

https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/04-analytics-engineering/setup/cloud_setup.md

### ✅ What this setup is doing (big picture)

-  You are connecting dbt Cloud to BigQuery, using the GCP project and service account you created in Module 3 of the DataTalksClub Data Engineering Zoomcamp.

### By the end:

- Raw taxi data lives in nytaxi
- dbt builds analytics tables into dbt_prod_*
- You develop safely in your own dbt_dipika schema

## 🧭 Step-by-step sanity checklist (HW4-ready)

### Step 1 — BigQuery (MOST IMPORTANT)

- You must have all of this true before touching dbt Cloud:
    - ✔ Service account JSON file
    - ✔ Permissions:
        - BigQuery Data Editor
        - BigQuery Job User
        - BigQuery User
- ✔ Dataset exists:
    - nytaxi
    - Location noted (US / EU / us-central1)
- ✔ Tables exist:
    - green_tripdata (2019 + 2020)
    - yellow_tripdata (2019 + 2020)
- ⚠️ Critical detail
    - The data must come from the DataTalksClub NYC TLC repo, not the official TLC site Otherwise your homework answers will not match.

Steps followed are as follows - 
```
We’ll break Step 1 into three concrete checks.

1.1 Confirm nytaxi dataset exists

Open BigQuery Console and check:
    - In the left Explorer panel
    - Your GCP project
    - Create Dataset named exactly:
        - nytaxi


1.2 Confirm required tables are loaded

Use scripts - load_yellow_tripdata.py and load_green_tripdata.py

Inside nytaxi, you should see at least these tables:

green_tripdata
yellow_tripdata

Data source - https://github.com/DataTalksClub/nyc-tlc-data/releases

These must contain 2019 and 2020 data.

Quick check (optional but recommended):
```sql
SELECT
  MIN(EXTRACT(YEAR FROM pickup_datetime)) AS min_year,
  MAX(EXTRACT(YEAR FROM pickup_datetime)) AS max_year,
  COUNT(*) AS rows
FROM `de-zoomcamp-2026-486900.nytaxi.yellow_tripdata`;

SELECT
  MIN(EXTRACT(YEAR FROM lpep_pickup_datetime)) AS min_year,
  MAX(EXTRACT(YEAR FROM lpep_pickup_datetime)) AS max_year,
  COUNT(*) AS rows
FROM `de-zoomcamp-2026-486900.nytaxi.green_tripdata`;
```

Output - 
```ini
min_year = 2019
max_year = 2020
```
Troublshoot errors - 

1. Error while running - load_yellow_tripdata.py, `ModuleNotFoundError: No module named 'pandas'`
    - In Google Cloud Console, confirm python is avaialble, run - 
        ```bash
        which python
        python --version
        ```
    - Install required Python packages (Cloud Shell)
        ```bash
        pip install pandas pyarrow google-cloud-bigquery
        ```
    - Verify Installation
        ```
        python -c "import pandas; import pyarrow; import google.cloud.bigquery; print('OK')"
        ```
        Expected output - `OK`
    - Rerun script

2. `TypeError: string indices must be integers, not 'str'`

- This happens because:

    - Cloud Shell sometimes doesn’t correctly detect the VM metadata
    - Or the BigQuery client library is confused by the default Compute Engine service account
    - This is not your Python code — it’s an environment quirk
    - It often happens with newer Python / client library versions, especially Python 3.12 in Cloud Shell.

- Even though your user is authenticated, the google-cloud-bigquery library sometimes tries to use the “Compute Engine / Cloud Shell service account” first.

- On Python 3.12 + recent BigQuery client versions, there is a metadata parsing bug that throws:
    - `TypeError: string indices must be integers, not 'str'`

3. google.api_core.exceptions.Forbidden: 403 ... Caller does not have required permission to use project de-zoomcamp-2026-486900
Grant the caller the roles/serviceusage.serviceUsageConsumer role, or a custom role with the serviceusage.services.use permission

    - Assing required permissions to service account.
        Permissions:
        - BigQuery Data Editor
        - BigQuery Job User
        - BigQuery User


This happens even though gcloud auth login is fine, because the library is trying to read service account info from VM metadata and fails.

- Use service account json
    ```bash
    export GOOGLE_APPLICATION_CREDENTIALS="/home/nipika73/your-service-account.json"
    ```
    Upload your-service-account.json from local to google cloud console.


1.3 Check dataset location (IMPORTANT)

Click on the nytaxi dataset → Details panel.

Look for:

Data location: ?


Common values:

US

EU

us-central1

👉 Action:
Tell me exactly what your dataset location is.
```

### Step 2 — dbt Platform signup

Free Developer plan is perfect — no upgrade needed.

### Step 3 — Create project
    Project name:
    ```nginx
    taxi_rides_ny
    ```
- ✔ This exact name matters later when following the course structure.

### Step 4 — BigQuery connection (where most people break things)

Use:
- Connection type: BigQuery
- Upload JSON key (service account)
- Set exactly:
    ```vbnet
    Dataset: dbt_prod
    Location: SAME as nytaxi (must match)
    Timeout: 300
    ```
- You should see: `✅ “Connection test succeeded”`

### Step 5 — Git repo

- Either option is fine for HW4:
    - dbt-managed repo ✅ easiest
    - GitHub repo ✅ fine if you already use GitHub

### Step 6 — Environment

dbt Cloud creates this automatically:

Development
- Schema: dbt_<your_name>
- Target: dev

Deployment
- Schema base: dbt_prod
- Produces:
    - dbt_prod_staging
    - dbt_prod_intermediate
    - dbt_prod_marts

You do not need to manually create schemas — dbt will.

### Step 7 — Start developing

Click:
```powershell
Develop → Start developing
```

Once the IDE opens, you are officially ready for:
- stg_green_tripdata
- stg_yellow_tripdata
- fact & dimension models
- HW4 questions