## Homework: Build Your Own dlt Pipeline

https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/workshops/dlt/dlt_homework.md

For this homework, build a dlt pipeline that loads NYC taxi trip data from a custom API into DuckDB and then answer some questions using the loaded data.

Data Source
You'll be working with NYC Yellow Taxi trip data from a custom API (not available as a dlt scaffold). This dataset contains records of individual taxi trips in New York City.

| Property | Value |
|----------|-------|
| Base URL | https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api |
| Format | Paginated JSON |
| Page Size | 1,000 records per page |
| Pagination | Stop when an empty page is returned |

## Solution using Google Colab

Google Colab. It provides a free, temporary environment in the cloud with all the resources you need to run dlt and DuckDB.

Steps followed - 

### 1. Open Google Colab
Go to [colab.new](https://colab.research.google.com/?authuser=0#create=true) and create a new notebook.

### 2. Install Dependencies
In the first cell, run this to install dlt with DuckDB support:


```python
!pip install "dlt[duckdb]"
```

### 3. Create and Run the Pipeline
Copy below code into a new cell. This script uses dlt's RESTClient to handle the custom API and pagination requirements.

```python
import dlt
from dlt.sources.helpers.rest_client import RESTClient
from dlt.sources.helpers.rest_client.paginators import OffsetPaginator

# 1. Define the Resource
@dlt.resource(name="rides", write_disposition="replace")
def taxi_rides():
    client = RESTClient(
        base_url="https://us-central1-dlthub-analytics.cloudfunctions.net",
        # We add total_path=None so dlt doesn't look for a 'total' key
        paginator=OffsetPaginator(limit=1000, offset=0, total_path=None)
    )

    # The API returns an empty list when it's done, which OffsetPaginator handles
    for page in client.paginate("data_engineering_zoomcamp_api"):
        print(f"Fetched a page with {len(page)} records...")
        yield page

# 2. Define and Run the Pipeline
pipeline = dlt.pipeline(
    pipeline_name="taxi_pipeline",
    destination="duckdb",
    dataset_name="taxi_data"
)

load_info = pipeline.run(taxi_rides())
print(load_info)
```

#### Troubleshoot steps:

1. Got below error while executing python code

```
ValueError: Total `items` not found in the response in `OffsetPaginator` .Expected a response with a `total` key, got `[{'End_Lat': 40.742963, 'End_Lon': -73.980072, 'Fare_Amt': 45.0, 'Passenger_Count': 1, 'Payment_Type': 'Credit', 'Rate_Code': None, 'Start_Lat': 40.641525, 'Start_Lon': -73.787442, 'Tip_Amt': 9.0, 'Tolls_Amt': 4.15, 'Total_Amt': 58.15, 'Trip_Distance': 17.52, 'Trip_Dropoff_DateTime': '2009-06-14 23:48:00', 'Trip_Pickup_DateTime': '2009-06-14 23:23:00', 'mta_tax': None, 'store_and_forward': None, 'surcharge': 0.0, 'vendor_name': 'VTS'}, {'End_Lat': 40.740187, 'End_Lon': -74.005698, 'Fare_Amt': 6.5, 'Passenger_Count': 1, 'Payment_Type': 'Credit', 'Rate_Code': None, 'Start_Lat': 40.722065, 'Start_Lon': -74.009767, 'Tip_Amt': 1.0, 'Tolls_Amt': 0.0, 'Total_Amt': 8.5, 'Trip_Distance': 1.56, 'Trip_Dropoff_DateTime': '2009-06-18 17:43:00', 'Trip_Pickup_DateTime': '2009-06-18 17:35:00', 'mta_tax': None, 'store_and_forward': None, 'surcharge': 1.0, 'vendor_name': 'VTS'}, {'End_Lat': 40.718043, 'End_Lon': -74.004745, 'Fare_Amt': 12.5, 'Passenger_Count': 5, 'Payment_Type': 'Credit', 'Rate_Code': None, 'Start_Lat': 40.761945, 'Start_Lon': -73.983038, 'Tip_Amt': 2.0, 'Tolls_Amt': 0.0, 'Total_Amt': 15.5, 'Trip_Distance': 3.37, 'Trip_Dropoff_DateTime': '2009-06-10 18:27:00', 'Trip_Pickup_DateTime': '2009-06-10 18:08:00', 'mta_tax': None, 'store_and_forward': None, 'surcharge': 1.0, 'vendor_name': 'VTS'}, {'End_Lat': 40.739637, 'End_Lon': -73.985233, 'Fare_Amt':...

The above exception was the direct cause of the following exception:
```

Solution - 

- The error happens because the default OffsetPaginator in dlt is looking for a field in the API response that tells it the total number of records (e.g., {"total": 5000, "data": [...]}).

- However, this specific NYC Taxi API is "simple"—it just returns a raw list of objects [...]. When dlt doesn't see a total key, it panics and throws that ValueError.

- To fix this, we need to tell the Paginator not to look for a total count and instead just keep going until it hits an empty page. We do this by setting total_path=None.

- Update your taxi_rides function in Colab with this code:

old code - 
```python
 client = RESTClient(
        base_url="https://us-central1-dlthub-analytics.cloudfunctions.net",
        paginator=OffsetPaginator(limit=1000, offset=0)
    )

    # The API returns an empty list when it's done, which OffsetPaginator handles
    for page in client.paginate("data_engineering_zoomcamp_api"):
        yield page
```

Updated code - 
```python
@dlt.resource(name="rides", write_disposition="replace")
def taxi_rides():
    client = RESTClient(
        base_url="https://us-central1-dlthub-analytics.cloudfunctions.net",
        # We add total_path=None so dlt doesn't look for a 'total' key
        paginator=OffsetPaginator(limit=1000, offset=0, total_path=None)
    )

    for page in client.paginate("data_engineering_zoomcamp_api"):
        yield page
```

2. Got stuck into infinite loop while running python code

- Why this is happening:
Many simple APIs ignore extra parameters like ?offset=1000. If you send that request and the API just says "I don't know what offset is, here is page 1 again," dlt will see 1,000 records, think it's a new page, and ask for offset=2000. This creates an infinite loop.

- To prevent this, we need to implement Deduplication Logic inside the loop. We can store the "fingerprint" (a hash or just the string version) of the first record of each page. If we see a first record we’ve seen before, we know we're running in circles and we break.

```python
import dlt
from dlt.sources.helpers.rest_client import RESTClient
from dlt.sources.helpers.rest_client.paginators import OffsetPaginator

# We MUST use the decorator so dlt knows this is a data source
@dlt.resource(name="rides", write_disposition="replace")
def taxi_rides():
    client = RESTClient(base_url="https://us-central1-dlthub-analytics.cloudfunctions.net")
    
    offset = 0
    page_size = 1000
    last_first_record = None
    
    while True:
        params = {"offset": offset, "limit": page_size}
        response = client.get("data_engineering_zoomcamp_api", params=params)
        data = response.json()
        
        if not data:
            print("Stop: API returned an empty list.")
            break
            
        current_first_record = data[0]
        
        # This will prove the theory
        if last_first_record is not None:
            if current_first_record == last_first_record:
                print("\n⚠️ LOOP PROVED! ⚠️")
                print(f"Last Page's First Record:    {last_first_record}")
                print(f"Current Page's First Record: {current_first_record}")
                print(f"Stopping now because offset {offset} returned the same data as before.")
                break
            else:
                print(f"✅ Offset {offset} provided new data.")

        last_first_record = current_first_record
        yield data
        offset += page_size


# 2. Define and Run the Pipeline
pipeline = dlt.pipeline(
    pipeline_name="taxi_pipeline",
    destination="duckdb",
    dataset_name="taxi_data"
)

load_info = pipeline.run(taxi_rides())
print(load_info)
```

- By saving last_first_record, the code compares the first row of the new page to the first row of the previous page.

- Automatic Exit: If the API ignores your offset=1000 and sends the same first page again, the if current_first_record == last_first_record check will trigger immediately, and the script will finish gracefully.

- Output after execution - 
```logs
⚠️ LOOP PROVED! ⚠️
Last Page's First Record:    {'End_Lat': 40.742963, 'End_Lon': -73.980072, 'Fare_Amt': 45.0, 'Passenger_Count': 1, 'Payment_Type': 'Credit', 'Rate_Code': None, 'Start_Lat': 40.641525, 'Start_Lon': -73.787442, 'Tip_Amt': 9.0, 'Tolls_Amt': 4.15, 'Total_Amt': 58.15, 'Trip_Distance': 17.52, 'Trip_Dropoff_DateTime': '2009-06-14 23:48:00', 'Trip_Pickup_DateTime': '2009-06-14 23:23:00', 'mta_tax': None, 'store_and_forward': None, 'surcharge': 0.0, 'vendor_name': 'VTS'}

Current Page's First Record: {'End_Lat': 40.742963, 'End_Lon': -73.980072, 'Fare_Amt': 45.0, 'Passenger_Count': 1, 'Payment_Type': 'Credit', 'Rate_Code': None, 'Start_Lat': 40.641525, 'Start_Lon': -73.787442, 'Tip_Amt': 9.0, 'Tolls_Amt': 4.15, 'Total_Amt': 58.15, 'Trip_Distance': 17.52, 'Trip_Dropoff_DateTime': '2009-06-14 23:48:00', 'Trip_Pickup_DateTime': '2009-06-14 23:23:00', 'mta_tax': None, 'store_and_forward': None, 'surcharge': 0.0, 'vendor_name': 'VTS'}

Stopping now because offset 1000 returned the same data as before.

2026-02-28 00:16:37,964|[WARNING]|197|138693026349056|dlt|validate.py|verify_normalized_table:91|In schema `taxi`: The following columns in table 'taxi_rides' did not receive any data during this load and therefore could not have their types inferred:
  - rate_code
  - mta_tax

Unless type hints are provided, these columns will not be materialized in the destination.
One way to provide type hints is to use the 'columns' argument in the '@dlt.resource' decorator.  For example:

@dlt.resource(columns={'rate_code': {'data_type': 'text'}})

Pipeline taxi_pipeline load step completed in 0.41 seconds
1 load package(s) were loaded to destination duckdb and into dataset taxi_data
The duckdb destination used duckdb:////content/taxi_pipeline.duckdb location to store data
Load package 1772237794.573749 is LOADED and contains no failed jobs

```

`Theory confirmed! 🕵️‍♂️`

`The API is indeed ignoring the offset parameter and just giving you the same 1,000 records every time.`

- The warning about rate_code and mta_tax is normal; it just means those columns were empty (all None) in the 1,000 records you fetched, so dlt didn't know if they should be numbers or text.


### 4. Query the Data (The Answers)
Since you are in a notebook, you can use duckdb directly to query the file created by the pipeline. Run these in a new cell:

```python
import duckdb

# Connect to the DuckDB file created by dlt
conn = duckdb.connect("taxi_pipeline.duckdb")

# Question 1: Date Range
"""
Question 1. What is the start date and end date of the dataset? (1 point)

2009-01-01 to 2009-01-31

2009-06-01 to 2009-07-01

2024-01-01 to 2024-02-01

2024-06-01 to 2024-07-01

"""
print("--- Question 1: Date Range ---")
res1 = conn.execute("SELECT min(trip_pickup_date_time), max(trip_pickup_date_time) FROM taxi_data.taxi_rides").fetchone()
print(f"Start: {res1[0]} | End: {res1[1]}")

# Question 2: Credit Card Proportion (Payment Type 1 = Credit Card)
"""
Question 2. What proportion of trips are paid with credit card? (1 point)

16.66%

26.66%

36.66%

46.66%

"""
print("\n--- Question 2: Credit Card Proportion ---")
res2 = conn.execute("""
    SELECT 
        (COUNT(CASE WHEN payment_type = 'Credit' THEN 1 END) * 100.0 / COUNT(*)) 
    FROM taxi_data.taxi_rides
""").fetchone()
print(f"Percentage: {res2[0]:.2f}%")

# Question 3: Total Tips
"""
Question 3. What is the total amount of money generated in tips? (1 point)


$4,063.41

$6,063.41

$8,063.41

$10,063.41
"""
print("\n--- Question 3: Total Tips ---")
res3 = conn.execute("SELECT SUM(tip_amt) FROM taxi_data.taxi_rides").fetchone()
print(f"Total Tips: ${res3[0]:,.2f}")
```

## Troubleshoot errors

1. Received below error while executing queries on table created in duckdb

```error
--- Question 1: Date Range ---
---------------------------------------------------------------------------
CatalogException                          Traceback (most recent call last)
/tmp/ipython-input-399/3491495473.py in <cell line: 0>()
     18 """
     19 print("--- Question 1: Date Range ---")
---> 20 res1 = conn.execute("SELECT min(trip_pickup_date_time), max(trip_pickup_date_time) FROM taxi_data.rides").fetchone()
     21 print(f"Start: {res1[0]} | End: {res1[1]}")
     22 

CatalogException: Catalog Error: Table with name rides does not exist!
Did you mean "information_schema.views"?

LINE 1: ... min(trip_pickup_date_time), max(trip_pickup_date_time) FROM taxi_data.rides
                                                                        ^
```

- This is classic "Where is my table?" mystery. This usually happens because dlt creates table names based on the resource name defined in code.

- But if if you don't use the @dlt.resource decorator, the library defaults to using the function name as the table name.

- Since function was named taxi_rides, the table in DuckDB is likely named taxi_rides. However, when we ran the query, we were looking for rides.

```python
import duckdb
conn = duckdb.connect("taxi_pipeline.duckdb")
print(conn.execute("SHOW ALL TABLES").df())
```

output - 
```
Empty DataFrame
Columns: [database, schema, name, column_names, column_types, temporary]
Index: []
```

- If SHOW ALL TABLES is empty, it means that even though the dlt pipeline said it completed, no data was actually written to the disk in that specific .duckdb file.

### Why is the database empty?
There are two likely culprits here:

- The "Silent Yield" Issue: Because we removed the @dlt.resource decorator, dlt might not have recognized taxi_rides() as a valid data source when we passed it to pipeline.run(). It essentially ran an empty pipeline.

- File Path Confusion: In Google Colab, sometimes dlt creates the database in a hidden temporary folder if the path isn't explicitly clear, or it might have failed to commit the transaction because the generator (the loop) was interrupted by our "Loop Proved" break.

Solution - 

- Let's fix the code to be explicit. We will add the decorator back (to ensure dlt sees the data) and use a fresh database name to avoid any weird locking issues.

```python
import dlt
from dlt.sources.helpers.rest_client import RESTClient
from dlt.sources.helpers.rest_client.paginators import OffsetPaginator

# 1. Define the Resource
# We MUST use the decorator so dlt knows this is a data source
@dlt.resource(name="rides", write_disposition="replace")
def taxi_rides():
    client = RESTClient(base_url="https://us-central1-dlthub-analytics.cloudfunctions.net")
    
    offset = 0
    page_size = 1000
    last_first_record = None
    
    while True:
        params = {"offset": offset, "limit": page_size}
        response = client.get("data_engineering_zoomcamp_api", params=params)
        data = response.json()
        
        if not data:
            print("Stop: API returned an empty list.")
            break
            
        current_first_record = data[0]
        
        # This will prove the theory
        if last_first_record is not None:
            if current_first_record == last_first_record:
                print("\n⚠️ LOOP PROVED! ⚠️")
                print(f"Last Page's First Record:    {last_first_record}")
                print(f"Current Page's First Record: {current_first_record}")
                print(f"Stopping now because offset {offset} returned the same data as before.")
                break
            else:
                print(f"✅ Offset {offset} provided new data.")

        last_first_record = current_first_record
        yield data
        offset += page_size


# 2. Define and Run the Pipeline
# Run the pipeline with a FRESH database name
pipeline = dlt.pipeline(
    pipeline_name="taxi_fix",
    destination="duckdb",
    dataset_name="homework"
)

load_info = pipeline.run(taxi_rides())
print(load_info)

# 3. Query immediately in the same cell
import duckdb
conn = duckdb.connect("taxi_fix.duckdb")
# Let's check the table name dlt created
print("\nTable created:", conn.execute("SHOW TABLES").fetchall())

res = conn.execute("""
    SELECT 
        min(trip_pickup_date_time), 
        max(trip_pickup_date_time),
        (COUNT(CASE WHEN payment_type = 'Credit' THEN 1 END) * 100.0 / COUNT(*)),
        SUM(tip_amt)
    FROM homework.rides
""").fetchone()

print("\n--- 🚕 FINAL ANSWERS 🚕 ---")
print(f"Q1: {res[0]} to {res[1]}")
print(f"Q2: {res[2]:.2f}%")
print(f"Q3: ${res[3]:,.2f}")
```

Output - 
```
---------------------------------------------------------------------------
ModuleNotFoundError                       Traceback (most recent call last)
/tmp/ipython-input-399/1245539975.py in <cell line: 0>()
----> 1 import dlt
      2 from dlt.sources.helpers.rest_client import RESTClient
      3 from dlt.sources.helpers.rest_client.paginators import OffsetPaginator
      4 
      5 # 1. Define the Resource

ModuleNotFoundError: No module named 'dlt'

---------------------------------------------------------------------------
NOTE: If your import is failing due to a missing package, you can
manually install dependencies using either !pip or !apt.

To view examples of installing some common dependencies, click the
"Open Examples" button below.
---------------------------------------------------------------------------
```

- This error shows that, my session is expired. No other issue. So I ran all previous steps one by one. 

- Got the result but none of the answers are matching. Included debug messages which shows that only 1000 records are added. 

- Let's try with page number logic for pagination instead of offset.

```python
import dlt
from dlt.sources.helpers.rest_client import RESTClient

@dlt.resource(name="rides", write_disposition="replace")
def taxi_rides():
    client = RESTClient(base_url="https://us-central1-dlthub-analytics.cloudfunctions.net")
    
    page = 1
    prev_first_id = None
    
    while True:
        # Requesting by page instead of offset
        params = {
            "page": page,
            "limit": 1000
        }
        response = client.get("data_engineering_zoomcamp_api", params=params)
        data = response.json()
        
        # 1. Stop if empty
        if not data:
            print(f"Stopped: No data on page {page}")
            break
            
        # 2. Check for duplication (The "Loop Trap")
        current_first_id = data[0].get('Trip_Pickup_DateTime') # Using timestamp as a proxy ID
        if prev_first_id == current_first_id:
            print(f"\n⚠️ Page {page} returned the same data as Page {page-1}.")
            print("The API does not support page-based pagination.")
            break
            
        print(f"✅ Loaded Page {page} ({len(data)} records)")
        yield data
        
        prev_first_id = current_first_id
        page += 1

pipeline = dlt.pipeline(pipeline_name="taxi_page_test", destination="duckdb", dataset_name="taxi_data")
pipeline.run(taxi_rides())
```

Output - 
```
✅ Loaded Page 1 (1000 records)
✅ Loaded Page 2 (1000 records)
✅ Loaded Page 3 (1000 records)
✅ Loaded Page 4 (1000 records)
✅ Loaded Page 5 (1000 records)
✅ Loaded Page 6 (1000 records)
✅ Loaded Page 7 (1000 records)
✅ Loaded Page 8 (1000 records)
✅ Loaded Page 9 (1000 records)
✅ Loaded Page 10 (1000 records)
Stopped: No data on page 11
2026-02-28 07:59:26,219|[WARNING]|399|135000070295552|dlt|validate.py|verify_normalized_table:91|In schema `taxi_page_test`: The following columns in table 'rides' did not receive any data during this load and therefore could not have their types inferred:
  - rate_code
  - mta_tax

Unless type hints are provided, these columns will not be materialized in the destination.
One way to provide type hints is to use the 'columns' argument in the '@dlt.resource' decorator.  For example:

@dlt.resource(columns={'rate_code': {'data_type': 'text'}})

LoadInfo(pipeline=<dlt.pipeline(pipeline_name='taxi_page_test', destination='duckdb', dataset_name='taxi_data', default_schema_name='taxi_page_test', schema_names=['taxi_page_test'], first_run=False, dev_mode=False, is_active=True, pipelines_dir='/var/dlt/pipelines', working_dir='/var/dlt/pipelines/taxi_page_test')>, metrics={'1772265543.3443127': [{'started_at': DateTime(2026, 2, 28, 7, 59, 26, 263146, tzinfo=Timezone('UTC')), 'finished_at': DateTime(2026, 2, 28, 7, 59, 28, 355780, tzinfo=Timezone('UTC')), 'job_metrics': {'rides.e274a78e17.insert_values.gz': LoadJobMetrics(job_id='rides.e274a78e17.insert_values.gz', file_path='/var/dlt/pipelines/taxi_page_test/load/normalized/1772265543.3443127/started_jobs/rides.e274a78e17.0.insert_values.gz', table_name='rides', started_at=DateTime(2026, 2, 28, 7, 59, 26, 340217, tzinfo=Timezone('UTC')), finished_at=DateTime(2026, 2, 28, 7, 59, 28, 269652, tzinfo=Timezone('UTC')), state='completed', remote_url=None, retry_count=0), '_dlt_pipeline_state.d9c5de784c.insert_values.gz': LoadJobMetrics(job_id='_dlt_pipeline_state.d9c5de784c.insert_values.gz', file_path='/var/dlt/pipelines/taxi_page_test/load/normalized/1772265543.3443127/started_jobs/_dlt_pipeline_state.d9c5de784c.0.insert_values.gz', table_name='_dlt_pipeline_state', started_at=DateTime(2026, 2, 28, 7, 59, 26, 342077, tzinfo=Timezone('UTC')), finished_at=DateTime(2026, 2, 28, 7, 59, 26, 365868, tzinfo=Timezone('UTC')), state='completed', remote_url=None, retry_count=0)}}]}, destination_type='dlt.destinations.duckdb', destination_displayable_credentials='duckdb:////content/taxi_page_test.duckdb', destination_name='duckdb', environment=None, staging_type=None, staging_name=None, staging_displayable_credentials=None, destination_fingerprint='', dataset_name='taxi_data', loads_ids=['1772265543.3443127'], load_packages=[LoadPackageInfo(load_id='1772265543.3443127', package_path='/var/dlt/pipelines/taxi_page_test/load/loaded/1772265543.3443127', state='loaded', schema=<dlt.Schema(name='taxi_page_test', version=2, tables=['_dlt_version', '_dlt_loads', 'rides', '_dlt_pipeline_state'], version_hash='LVwRP+Qp8A8qvRI5S63ZoWRcqRQ1RaJAHsvrPaTUrfY=')>, schema_update={'_dlt_version': {'name': '_dlt_version', 'columns': {'version': {'name': 'version', 'data_type': 'bigint', 'nullable': False}, 'engine_version': {'name': 'engine_version', 'data_type': 'bigint', 'nullable': False}, 'inserted_at': {'name': 'inserted_at', 'data_type': 'timestamp', 'nullable': False}, 'schema_name': {'name': 'schema_name', 'data_type': 'text', 'nullable': False}, 'version_hash': {'name': 'version_hash', 'data_type': 'text', 'nullable': False}, 'schema': {'name': 'schema', 'data_type': 'text', 'nullable': False}}, 'write_disposition': 'skip', 'resource': '_dlt_version', 'description': 'Created by DLT. Tracks schema updates'}, '_dlt_loads': {'name': '_dlt_loads', 'columns': {'load_id': {'name': 'load_id', 'data_type': 'text', 'nullable': False, 'precision': 64}, 'schema_name': {'name': 'schema_name', 'data_type': 'text', 'nullable': True}, 'status': {'name': 'status', 'data_type': 'bigint', 'nullable': False}, 'inserted_at': {'name': 'inserted_at', 'data_type': 'timestamp', 'nullable': False}, 'schema_version_hash': {'name': 'schema_version_hash', 'data_type': 'text', 'nullable': True}}, 'write_disposition': 'skip', 'resource': '_dlt_loads', 'description': 'Created by DLT. Tracks completed loads'}, 'rides': {'columns': {'end_lat': {'name': 'end_lat', 'data_type': 'double', 'nullable': True}, 'end_lon': {'name': 'end_lon', 'data_type': 'double', 'nullable': True}, 'fare_amt': {'name': 'fare_amt', 'data_type': 'double', 'nullable': True}, 'passenger_count': {'name': 'passenger_count', 'data_type': 'bigint', 'nullable': True}, 'payment_type': {'name': 'payment_type', 'data_type': 'text', 'nullable': True}, 'start_lat': {'name': 'start_lat', 'data_type': 'double', 'nullable': True}, 'start_lon': {'name': 'start_lon', 'data_type': 'double', 'nullable': True}, 'tip_amt': {'name': 'tip_amt', 'data_type': 'double', 'nullable': True}, 'tolls_amt': {'name': 'tolls_amt', 'data_type': 'double', 'nullable': True}, 'total_amt': {'name': 'total_amt', 'data_type': 'double', 'nullable': True}, 'trip_distance': {'name': 'trip_distance', 'data_type': 'double', 'nullable': True}, 'trip_dropoff_date_time': {'name': 'trip_dropoff_date_time', 'data_type': 'timestamp', 'nullable': True}, 'trip_pickup_date_time': {'name': 'trip_pickup_date_time', 'data_type': 'timestamp', 'nullable': True}, 'surcharge': {'name': 'surcharge', 'data_type': 'double', 'nullable': True}, 'vendor_name': {'name': 'vendor_name', 'data_type': 'text', 'nullable': True}, '_dlt_load_id': {'name': '_dlt_load_id', 'data_type': 'text', 'nullable': False}, '_dlt_id': {'name': '_dlt_id', 'data_type': 'text', 'nullable': False, 'unique': True, 'row_key': True}, 'store_and_forward': {'name': 'store_and_forward', 'nullable': True, 'data_type': 'double'}}, 'write_disposition': 'replace', 'name': 'rides', 'resource': 'rides', 'x-normalizer': {'seen-data': True}, 'x-replace-strategy': 'truncate-and-insert'}, '_dlt_pipeline_state': {'columns': {'version': {'name': 'version', 'data_type': 'bigint', 'nullable': False}, 'engine_version': {'name': 'engine_version', 'data_type': 'bigint', 'nullable': False}, 'pipeline_name': {'name': 'pipeline_name', 'data_type': 'text', 'nullable': False}, 'state': {'name': 'state', 'data_type': 'text', 'nullable': False}, 'created_at': {'name': 'created_at', 'data_type': 'timestamp', 'nullable': False}, 'version_hash': {'name': 'version_hash', 'data_type': 'text', 'nullable': True}, '_dlt_load_id': {'name': '_dlt_load_id', 'data_type': 'text', 'nullable': False, 'precision': 64}, '_dlt_id': {'name': '_dlt_id', 'data_type': 'text', 'nullable': False, 'unique': True, 'row_key': True}}, 'write_disposition': 'append', 'file_format': 'preferred', 'name': '_dlt_pipeline_state', 'resource': '_dlt_pipeline_state', 'x-normalizer': {'seen-data': True}}}, completed_at=DateTime(2026, 2, 28, 7, 59, 28, 352464, tzinfo=Timezone('UTC')), jobs={'new_jobs': [], 'failed_jobs': [], 'started_jobs': [], 'completed_jobs': [LoadJobInfo(state='completed_jobs', file_path='/var/dlt/pipelines/taxi_page_test/load/loaded/1772265543.3443127/completed_jobs/rides.e274a78e17.0.insert_values.gz', file_size=455846, created_at=DateTime(2026, 2, 28, 7, 59, 26, 217232, tzinfo=Timezone('UTC')), elapsed=2.1352317333221436, job_file_info=ParsedLoadJobFileName(table_name='rides', file_id='e274a78e17', retry_count=0, file_format='insert_values', is_compressed=True), failed_message=None), LoadJobInfo(state='completed_jobs', file_path='/var/dlt/pipelines/taxi_page_test/load/loaded/1772265543.3443127/completed_jobs/_dlt_pipeline_state.d9c5de784c.0.insert_values.gz', file_size=530, created_at=DateTime(2026, 2, 28, 7, 59, 26, 217232, tzinfo=Timezone('UTC')), elapsed=2.1352317333221436, job_file_info=ParsedLoadJobFileName(table_name='_dlt_pipeline_state', file_id='d9c5de784c', retry_count=0, file_format='insert_values', is_compressed=True), failed_message=None)]})], first_run=True)
```

Check homework questions and answers - 

```python
import duckdb

# Connect to the database created in last run
conn = duckdb.connect("taxi_page_test.duckdb")

# Execute the final calculation
res = conn.execute("""
    SELECT 
        COUNT(*) AS total_records,
        MIN(trip_pickup_date_time) AS start_time, 
        MAX(trip_pickup_date_time) AS end_time,
        (COUNT(CASE WHEN payment_type = 'Credit' THEN 1 END) * 100.0 / COUNT(*)) AS credit_card_percentage,
        SUM(tip_amt) AS total_tips
    FROM taxi_data.rides
""").fetchone()

print("="*40)
print("🚕 FINAL HOMEWORK ANSWERS 🚕")
print("="*40)
print(f"Total Records: {res[0]}")
print(f"Q1 Date Range: {res[1]} to {res[2]}")
print(f"Q2 CC %:      {res[3]:.2f}%")
print(f"Q3 Total Tips: ${res[4]:,.2f}")
print("="*40)
```

Output - 
```
========================================
🚕 FINAL HOMEWORK ANSWERS 🚕
========================================
Total Records: 10000
Q1 Date Range: 2009-06-01 11:33:00+00:00 to 2009-06-30 23:58:00+00:00
Q2 CC %:      26.66%
Q3 Total Tips: $6,063.41
========================================
```

Note - for first question, let's verify if there is any data beyond June, 2009

```python
import duckdb

# Connect to the database created in last run
conn = duckdb.connect("taxi_page_test.duckdb")

print(conn.execute("SELECT * FROM taxi_data.rides WHERE trip_pickup_date_time >= '2009-07-01'").fetchall())
```

Output - empty list. This confirms data is for June 2009

```
[]
```

Note - final version of collab notebood is available in Git repo as dlt_taxi_pipeline.ipynb