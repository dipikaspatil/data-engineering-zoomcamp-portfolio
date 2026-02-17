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

#### Troublshoot errors - 

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

This happens even though gcloud auth login is fine, because the library is trying to read service account info from VM metadata and fails.

- Use service account json
    ```bash
    export GOOGLE_APPLICATION_CREDENTIALS="/home/nipika73/your-service-account.json"
    ```
    Upload your-service-account.json from local to google cloud console.

3. google.api_core.exceptions.Forbidden: 403 ... Caller does not have required permission to use project de-zoomcamp-2026-486900
Grant the caller the roles/serviceusage.serviceUsageConsumer role, or a custom role with the serviceusage.services.use permission

    - Assing required permissions to service account.
        Permissions:
        - BigQuery Data Editor
        - BigQuery Job User
        - BigQuery User

4. 403 ... Caller does not have required permission to use project de-zoomcamp-2026-486900
Grant the caller the roles/serviceusage.serviceUsageConsumer role

    - Your Python script is trying to load data into BigQuery.
    - The user credentials from gcloud auth login in Cloud Shell do not have enough permissions on the project.
    - Specifically, the user cannot even “use” the project services, which is required before BigQuery operations.

- Assign permission `serviceusage.serviceUsageConsumer` to service account

#### Script logs - 

```logs
 python load_green_tripdata.py 
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-01.csv.gz ...
Downloaded ./tmp_green/2019-01.csv.gz
Loaded 2019-01 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-02.csv.gz ...
Downloaded ./tmp_green/2019-02.csv.gz
Loaded 2019-02 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-03.csv.gz ...
Downloaded ./tmp_green/2019-03.csv.gz
Loaded 2019-03 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-04.csv.gz ...
Downloaded ./tmp_green/2019-04.csv.gz
Loaded 2019-04 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-05.csv.gz ...
Downloaded ./tmp_green/2019-05.csv.gz
Loaded 2019-05 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-06.csv.gz ...
Downloaded ./tmp_green/2019-06.csv.gz
Loaded 2019-06 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-07.csv.gz ...
Downloaded ./tmp_green/2019-07.csv.gz
Loaded 2019-07 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-08.csv.gz ...
Downloaded ./tmp_green/2019-08.csv.gz
Loaded 2019-08 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-09.csv.gz ...
Downloaded ./tmp_green/2019-09.csv.gz
Loaded 2019-09 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-10.csv.gz ...
Downloaded ./tmp_green/2019-10.csv.gz
Loaded 2019-10 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-11.csv.gz ...
Downloaded ./tmp_green/2019-11.csv.gz
Loaded 2019-11 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-12.csv.gz ...
Downloaded ./tmp_green/2019-12.csv.gz
Loaded 2019-12 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2020-01.csv.gz ...
Downloaded ./tmp_green/2020-01.csv.gz
Loaded 2020-01 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2020-02.csv.gz ...
Downloaded ./tmp_green/2020-02.csv.gz
Loaded 2020-02 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2020-03.csv.gz ...
Downloaded ./tmp_green/2020-03.csv.gz
Loaded 2020-03 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2020-04.csv.gz ...
Downloaded ./tmp_green/2020-04.csv.gz
Loaded 2020-04 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2020-05.csv.gz ...
Downloaded ./tmp_green/2020-05.csv.gz
Loaded 2020-05 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2020-06.csv.gz ...
Downloaded ./tmp_green/2020-06.csv.gz
Loaded 2020-06 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2020-07.csv.gz ...
Downloaded ./tmp_green/2020-07.csv.gz
Loaded 2020-07 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2020-08.csv.gz ...
Downloaded ./tmp_green/2020-08.csv.gz
Loaded 2020-08 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2020-09.csv.gz ...
Downloaded ./tmp_green/2020-09.csv.gz
Loaded 2020-09 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2020-10.csv.gz ...
Downloaded ./tmp_green/2020-10.csv.gz
Loaded 2020-10 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2020-11.csv.gz ...
Downloaded ./tmp_green/2020-11.csv.gz
Loaded 2020-11 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2020-12.csv.gz ...
Downloaded ./tmp_green/2020-12.csv.gz
Loaded 2020-12 into BigQuery
✅ All green taxi CSV data loaded into BigQuery!
```

```logs
python load_yellow_tripdata.py 
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2019-01.csv.gz ...
Downloaded ./tmp_yellow/2019-01.csv.gz
Loaded 2019-01 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2019-02.csv.gz ...
Downloaded ./tmp_yellow/2019-02.csv.gz
Loaded 2019-02 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2019-03.csv.gz ...
Downloaded ./tmp_yellow/2019-03.csv.gz
Loaded 2019-03 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2019-04.csv.gz ...
Downloaded ./tmp_yellow/2019-04.csv.gz
Loaded 2019-04 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2019-05.csv.gz ...
Downloaded ./tmp_yellow/2019-05.csv.gz
Loaded 2019-05 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2019-06.csv.gz ...
Downloaded ./tmp_yellow/2019-06.csv.gz
Loaded 2019-06 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2019-07.csv.gz ...
Downloaded ./tmp_yellow/2019-07.csv.gz
Loaded 2019-07 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2019-08.csv.gz ...
Downloaded ./tmp_yellow/2019-08.csv.gz
Loaded 2019-08 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2019-09.csv.gz ...
Downloaded ./tmp_yellow/2019-09.csv.gz
Loaded 2019-09 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2019-10.csv.gz ...
Downloaded ./tmp_yellow/2019-10.csv.gz
Loaded 2019-10 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2019-11.csv.gz ...
Downloaded ./tmp_yellow/2019-11.csv.gz
Loaded 2019-11 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2019-12.csv.gz ...
Downloaded ./tmp_yellow/2019-12.csv.gz
Loaded 2019-12 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2020-01.csv.gz ...
Downloaded ./tmp_yellow/2020-01.csv.gz
Loaded 2020-01 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2020-02.csv.gz ...
Downloaded ./tmp_yellow/2020-02.csv.gz
Loaded 2020-02 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2020-03.csv.gz ...
Downloaded ./tmp_yellow/2020-03.csv.gz
Loaded 2020-03 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2020-04.csv.gz ...
Downloaded ./tmp_yellow/2020-04.csv.gz
Loaded 2020-04 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2020-05.csv.gz ...
Downloaded ./tmp_yellow/2020-05.csv.gz
Loaded 2020-05 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2020-06.csv.gz ...
Downloaded ./tmp_yellow/2020-06.csv.gz
Loaded 2020-06 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2020-07.csv.gz ...
Downloaded ./tmp_yellow/2020-07.csv.gz
Loaded 2020-07 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2020-08.csv.gz ...
Downloaded ./tmp_yellow/2020-08.csv.gz
Loaded 2020-08 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2020-09.csv.gz ...
Downloaded ./tmp_yellow/2020-09.csv.gz
Loaded 2020-09 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2020-10.csv.gz ...
Downloaded ./tmp_yellow/2020-10.csv.gz
Loaded 2020-10 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2020-11.csv.gz ...
Downloaded ./tmp_yellow/2020-11.csv.gz
Loaded 2020-11 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2020-12.csv.gz ...
Downloaded ./tmp_yellow/2020-12.csv.gz
Loaded 2020-12 into BigQuery
✅ All yellow taxi CSV data loaded into BigQuery!

```
```sql
select count(*) from 
`de-zoomcamp-2026-486900.nytaxi.yellow_tripdata` --109047518

select count(*) from 
`de-zoomcamp-2026-486900.nytaxi.green_tripdata` --8409019
```

1.3 Check dataset location (IMPORTANT)

Click on the nytaxi dataset → Details panel.

Look for:

Data location: US


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


## HW4 steps followed - 
https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/04-analytics-engineering/homework.md

### Step 1: Create a Deployment Environment (prod)

- Click Create Environment
- Name it something like: prod
- Engine: Latest Fusion (or default dbt Cloud engine)
- Schema: dbt_prod
- save

### Step 2: Set it as the project’s production environment

- Once created, you should see an option like:
- Set as production environment
- Select your newly created prod environment

### Step 3: Verify

- Go back to your Studio / IDE

- Run:
```nginx
dbt build --target prod
```
- This will build all models in your production schema (dbt_prod)
- All your HW4 queries (fct_trips, fct_monthly_zone_revenue, etc.) will now query the production tables

✅ Once this is done, your deployment environment is fully configured, and you can safely build and test your HW4 models.

## Homework 4 Questions ans answers - 

### Question 1. Q1: dbt run --select int_trips_unioned builds which models? (1 point)


- stg_green_tripdata, stg_yellow_tripdata, and int_trips_unioned

- Any model with upstream and downstream dependencies

- int_trips_unioned only

- int_trips_unioned, int_trips, and fct_trips

Given a dbt project with the following structure:

models/
├── staging/
│   ├── stg_green_tripdata.sql
│   └── stg_yellow_tripdata.sql
└── intermediate/


```bash
dbt run --select int_trips_unioned
```

int_trips_unioned depends on:

- stg_green_tripdata

- stg_yellow_tripdata

dbt will automatically build all upstream dependencies to make int_trips_unioned materialize correctly.

dbt does not automatically build downstream models unless you explicitly select them.

✅ So the correct answer is:

stg_green_tripdata, stg_yellow_tripdata, and int_trips_unioned

### Question 2. Q2: New value 6 appears in payment_type. What happens on dbt test? (1 point)

You've configured a generic test like this in your schema.yml:

columns:
  - name: payment_type
    data_tests:
      - accepted_values:
          arguments:
            values: [1, 2, 3, 4, 5]
            quote: false
Your model fct_trips has been running successfully for months. A new value 6 now appears in the source data.

What happens when you run dbt test --select fct_trips?


- dbt skips the test

- dbt fails the test with non-zero exit code

- dbt passes with warning

- dbt updates the configuration

Answer - dbt fails the test with non-zero exit code ✅

### Question 3. Q3: Count of records in fct_monthly_zone_revenue? (1 point)


12,998

14,120

12,184

15,421

```sql
select count(*) from dbt_prod.fct_monthly_zone_revenue;
```

Answer - 12184

### Question 4. Q4: Zone with highest revenue for Green taxis in 2020? (1 point)


- East Harlem North

- Morningside Heights

- East Harlem South

- Washington Heights South

Using the fct_monthly_zone_revenue table, find the pickup zone with the highest total revenue (revenue_monthly_total_amount) for Green taxi trips in 2020.

Which zone had the highest revenue?
```sql
SELECT 
    pickup_zone,
    SUM(revenue_monthly_total_amount) AS revenue_2020
FROM dbt_prod.fct_monthly_zone_revenue
WHERE service_type = 'Green'
  AND EXTRACT(YEAR FROM revenue_month) = 2020
GROUP BY pickup_zone
ORDER BY revenue_2020 DESC
LIMIT 1;
```

Output - 
East Harlem North	1815309.55

Answer - East Harlem North

### Question 5. Q5: Total trips for Green taxis in October 2019? (1 point)


- 500,234

- 350,891

- 384,624

- 421,509

Using the fct_monthly_zone_revenue table, what is the total number of trips (total_monthly_trips) for Green taxis in October 2019?

```sql
SELECT SUM(total_monthly_trips)
FROM dbt_prod.fct_monthly_zone_revenue
WHERE service_type = 'Green'
AND EXTRACT(YEAR FROM revenue_month) = 2019
AND EXTRACT(MONTH FROM revenue_month) = 10;
```

Output - 384,624

### Question 6. Q6: Count of records in stg_fhv_tripdata (filter dispatching_base_num IS NULL)? (1 point)


- 42,084,899

43,244,693

22,998,722

44,112,187

Build a Staging Model for FHV Data
Create a staging model for the For-Hire Vehicle (FHV) trip data for 2019.

Load the FHV trip data for 2019 into your data warehouse
Create a staging model stg_fhv_tripdata with these requirements:
Filter out records where dispatching_base_num IS NULL
Rename fields to match your project's naming conventions (e.g., PUlocationID → pickup_location_id)
What is the count of records in stg_fhv_tripdata?

Steps followed are as follows - 

1. Loaded data using `load_fhv_tripdata.py` in Big-Query.

Logs - 
```logs
python load_fhv_tripdata.py 
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv/fhv_tripdata_2019-01.csv.gz ...
Downloaded ./tmp_fhv/2019-01.csv.gz
Loaded 2019-01 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv/fhv_tripdata_2019-02.csv.gz ...
Downloaded ./tmp_fhv/2019-02.csv.gz
Loaded 2019-02 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv/fhv_tripdata_2019-03.csv.gz ...
Downloaded ./tmp_fhv/2019-03.csv.gz
Loaded 2019-03 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv/fhv_tripdata_2019-04.csv.gz ...
Downloaded ./tmp_fhv/2019-04.csv.gz
Loaded 2019-04 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv/fhv_tripdata_2019-05.csv.gz ...
Downloaded ./tmp_fhv/2019-05.csv.gz
Loaded 2019-05 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv/fhv_tripdata_2019-06.csv.gz ...
Downloaded ./tmp_fhv/2019-06.csv.gz
Loaded 2019-06 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv/fhv_tripdata_2019-07.csv.gz ...
Downloaded ./tmp_fhv/2019-07.csv.gz
Loaded 2019-07 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv/fhv_tripdata_2019-08.csv.gz ...
Downloaded ./tmp_fhv/2019-08.csv.gz
Loaded 2019-08 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv/fhv_tripdata_2019-09.csv.gz ...
Downloaded ./tmp_fhv/2019-09.csv.gz
Loaded 2019-09 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv/fhv_tripdata_2019-10.csv.gz ...
Downloaded ./tmp_fhv/2019-10.csv.gz
Loaded 2019-10 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv/fhv_tripdata_2019-11.csv.gz ...
Downloaded ./tmp_fhv/2019-11.csv.gz
Loaded 2019-11 into BigQuery
Downloading https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv/fhv_tripdata_2019-12.csv.gz ...
Downloaded ./tmp_fhv/2019-12.csv.gz
Loaded 2019-12 into BigQuery
✅ All FHV tripdata data loaded into BigQuery!
```

Verify - 
```sql
SELECT COUNT(*) FROM nytaxi.fhv_tripdata
WHERE EXTRACT(YEAR FROM SAFE_CAST(pickup_datetime AS TIMESTAMP)) = 2019; -- 43244696
```

Output - `43244696`

Table columns
```
dispatching_base_num STRING	
pickup_datetime STRING	
dropOff_datetime STRING	
PUlocationID FLOAT	
DOlocationID FLOAT	
SR_Flag FLOAT	
Affiliated_base_number STRING
```

2. Create new file in dbt project
Note - use macro safe_cast wherever needed
```
models/staging/stg_fhv_tripdata.sql
```

3. Update existing file in dbt project for fhv tripdata
```
models/staging/schema.yml
models/staging/sources.yml
```

4. Run dbt
```bash
dbt run --select stg_fhv_tripdata
```

Table created in BigQuery - 
```sql
SELECT COUNT(*) AS total_records
FROM `de-zoomcamp-2026-486900.dbt_prod.stg_fhv_tripdata`
WHERE dispatching_base_num IS NOT NULL
  AND EXTRACT(YEAR FROM SAFE_CAST(pickup_datetime AS TIMESTAMP)) = 2019
```

Answer - 
43244693

