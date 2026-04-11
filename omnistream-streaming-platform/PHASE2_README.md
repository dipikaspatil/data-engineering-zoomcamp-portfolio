# Phase 2 Implementation 

🟡 Phase 2: The "Happy Path" (Ingestion & Storage)
Get data moving from API to BigQuery Staging.

- Step 3: The Producers. Write the Python Aviation Producer to move data from API → Redpanda:raw_aviation_data

- Step 4: The BQ Sink. Set up a basic connector (or a simple Flink "Pass-through" job) that takes everything from the processed_events topic and dumps it into a BigQuery table.

Goal: Verify that I can see "Raw" data appearing in BigQuery console.

--------------------------------------------------------------------------------------------------------------------------



## 🐍 Step 3: The Producers. Write the Python Aviation Producer to move data from API → Redpanda:raw_aviation_data

### Objects created/modified - 
- The Aviation Producer (producers/aviation_producer.py) - Script to start producing aviation data to the Kafka topic

### The Aviation Producer (producers/aviation_producer.py) 
First, I have to check that I have the Kafka client installed on my Mac:
```bash
# 1. Create the virtual environment folder (named 'venv')
python3 -m venv venv

# 2. Activate it 
# (Terminal prompt will usually change to show (venv) at the start)
source venv/bin/activate

# 3. Now install requirements inside the 'bubble'
pip install confluent-kafka requests
```

- Create aviation.producer.py

### 🧪 Testing Step 3 - 
Run the script: `python producers/aviation_producer.py`

Check Redpanda Console: Go to `http://localhost:8082/topics`.

I should see a new topic named aviation_events with 3 partitions.

Click it and go to the Messages tab. I should see JSON objects appearing in real-time.

Logs

```bash
(venv) niteshmishra@Mac 08-capstone % python producers/aviation_producer.py
✨ Topic 'aviation_events' not found. Creating...
✅ Topic 'aviation_events' created successfully.
📡 Fetching data from OpenSky...
✅ Message -> aviation_events [Partition: 2]
✅ Message -> aviation_events [Partition: 2]
✅ Message -> aviation_events [Partition: 2]
✅ Message -> aviation_events [Partition: 2]
✅ Message -> aviation_events [Partition: 2]
✅ Message -> aviation_events [Partition: 2]
✅ Message -> aviation_events [Partition: 2]
✅ Message -> aviation_events [Partition: 2]
✅ Message -> aviation_events [Partition: 0]
✅ Message -> aviation_events [Partition: 0]
✅ Message -> aviation_events [Partition: 0]
✅ Message -> aviation_events [Partition: 0]
✅ Message -> aviation_events [Partition: 0]
✅ Message -> aviation_events [Partition: 0]
✅ Message -> aviation_events [Partition: 1]
✅ Message -> aviation_events [Partition: 1]
✅ Message -> aviation_events [Partition: 1]
✅ Message -> aviation_events [Partition: 1]
✅ Message -> aviation_events [Partition: 1]
✅ Message -> aviation_events [Partition: 1]
😴 Waiting 30s for next poll...
```

![aviation_producer_testing](../08-capstone/images/aviation_producer_testing_1.png)

![aviation_producer_testing](../08-capstone/images/aviation_producer_testing_2.png)


## Step 4: Redpanda (raw_aviation_data) → Redpanda (processed_aviation_data)

To move from Step 4 (Raw to Processed) to Step 5 (Processed to BigQuery), Flink needs to stop treating data as a "Blob of Text" and start treating it as a Java Object. This allows to validate, filter, and map fields to BigQuery columns.

- The Model: FlightRecord.java
    - This class is the internal representation of flight data. It must match the keys in your Python Producer's JSON.
    - File: src/main/java/com/omnistream/model/FlightRecord.java

- The Translator: JSONSchema.java
    - Flink needs to know how to "De-serialize" (JSON string → Java Object) and "Serialize" (Java Object → JSON string). We'll use the Jackson library for this.
    - File: src/main/java/com/omnistream/serialization/JSONSchema.java

- The Logic: StreamingJob.java (Part 1)
    - This Flink job reads from raw_aviation_data and writes to processed_aviation_data.
    - File: src/main/java/com/omnistream/StreamingJob.java

## 🛠️ Step 5: Redpanda:processed_events → BigQuery staging

Before we add the BigQuery Sink code to StreamingJob.java, we need to define the BigQuery Row Serializer. BigQuery doesn't understand Java Objects directly; it needs them converted into TableRow or GenericRecord format.

We need to tell Flink how to turn Java FlightRecord into a format that Google BigQuery understands. Since BigQuery expects a "Row" format, we use a BigQuerySerializationSchema

- The BigQuery Serializer
    - This class acts as the bridge between your Java object and the BigQuery table columns.
    - File: src/main/java/com/omnistream/serialization/BigQueryRowSerializer.java
- The Final "Pass-Through" StreamingJob.java
    - Now integrate everything. This single Flink job now handles the entire Phase 2 movement: Raw Topic → Processed Topic → BigQuery.
    - File: src/main/java/com/omnistream/StreamingJob.java


### ☁️ Step 5.1: Pre-flight for BigQuery - Move data from the Redpanda topic into Google BigQuery.

### Objects created/modified - 

- terraform/main.tf - To create table in staging dataset as `raw_aviation_data`


Before we write the Flink job to move data to BigQuery, we need the "Landing Pad" ready in GCP.

- Create a Dataset: Name it omnistream_dataset. - Already created using terraform in phase 1

- Create a Table: Name it `raw_aviation_data` using terraform.

### Apply terraform changes - 
Since you already have a state file, Terraform will recognize that the datasets exist and will only create the new table.

#### Run:

- Initialize (just in case): `terraform init`
- Plan: `terraform plan -var-file="dev.tfvars"` (Verify it says "1 to add, 0 to change, 0 to destroy")
- Apply: `terraform apply -var-file="dev.tfvars"`

Logs

```bash
...
Apply complete! Resources: 1 added, 0 changed, 0 destroyed.

Outputs:

cold_archive_bucket = "de-zoomcamp-2026-486900-raw-archive"
error_lake_bucket = "de-zoomcamp-2026-486900-error-lake"
gold_dataset_id = "omnistream_gold"
service_account_email = "omnistream-runner@de-zoomcamp-2026-486900.iam.gserviceaccount.com"
staging_dataset_id = "omnistream_staging"
```

- Verify
```bash
# List all resources and grep for bigquery tables
terraform state list | grep google_bigquery_table

# Output
google_bigquery_table.raw_aviation_data
```

```bash
terraform state show google_bigquery_table.raw_aviation_data

# Output
# google_bigquery_table.raw_aviation_data:
resource "google_bigquery_table" "raw_aviation_data" {
    creation_time                = 1774308379625
    dataset_id                   = "omnistream_staging"
    deletion_protection          = false
    description                  = null
    effective_labels             = {
        "goog-terraform-provisioned" = "true"
    }
    etag                         = "qQ5RlFHs5RiIjvDCazWihw=="
    expiration_time              = 0
    friendly_name                = null
    generated_schema_columns     = null
    id                           = "projects/de-zoomcamp-2026-486900/datasets/omnistream_staging/tables/raw_aviation_data"
    ignore_auto_generated_schema = false
    last_modified_time           = 1774308379700
    location                     = "us-central1"
    max_staleness                = null
    num_bytes                    = 0
    num_long_term_bytes          = 0
    num_rows                     = 0
    project                      = "de-zoomcamp-2026-486900"
    require_partition_filter     = false
    schema                       = jsonencode(
        [
            {
                mode = "NULLABLE"
                name = "icao24"
                type = "STRING"
            },
            {
                mode = "NULLABLE"
                name = "callsign"
                type = "STRING"
            },
            {
                mode = "NULLABLE"
                name = "origin_country"
                type = "STRING"
            },
            {
                mode = "NULLABLE"
                name = "timestamp"
                type = "INTEGER"
            },
            {
                mode = "NULLABLE"
                name = "latitude"
                type = "FLOAT"
            },
            {
                mode = "NULLABLE"
                name = "longitude"
                type = "FLOAT"
            },
            {
                mode = "NULLABLE"
                name = "velocity"
                type = "FLOAT"
            },
        ]
    )
    self_link                    = "https://bigquery.googleapis.com/bigquery/v2/projects/de-zoomcamp-2026-486900/datasets/omnistream_staging/tables/raw_aviation_data"
    table_id                     = "raw_aviation_data"
    terraform_labels             = {
        "goog-terraform-provisioned" = "true"
    }
    type                         = "TABLE"

    time_partitioning {
        expiration_ms            = 7776000000
        field                    = null
        require_partition_filter = false
        type                     = "DAY"
    }
}
```

### Step 5.2 - Preflight - "Next Action" Checklist
To make this happen, I need to configure my Maven Project so it knows how to talk to both Redpanda and Google Cloud.

- Update pom.xml: Add the Kafka and BigQuery connectors.
    - three main categories of dependencies:
        - Flink Core: The engine itself.
        - Connectors: Kafka (for Redpanda) and Google Cloud (for BigQuery).
        - Serialization: Jackson (to turn your Producer's JSON into Java Objects).

### Step 5.3 - PostFlight - Logging

- Configure log4j.properties
    - This file tells Flink how much detail to show in the TaskManager logs. We want to see INFO for the general flow and WARN/ERROR for the connectors.
    - File: src/main/resources/log4j.properties

## 🚀 Implementation Steps

1. Build the Project: On Mac, inside flink-processor, run:

```bash
mvn clean package

OR 

mvn clean package -U # to ignore "cached failure"

# OUTPUT 

[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  12.338 s
[INFO] Finished at: 2026-03-26T15:23:24-07:00
[INFO] ------------------------------------------------------------------------
```
This creates a file like target/flink-processor-1.0-SNAPSHOT.jar.

2. Submit to Flink: Since Flink is running in Docker, you'll upload this JAR to the Flink JobManager. You can do this via the Flink UI at localhost:8081.
    - Open http://localhost:8081.
    - Click Submit New Job > Add New.
    - Upload your JAR and click Submit.

Note - This is only for phase 2. Later I will automate it Airflow BashOperator - Airflow runs a docker exec command to tell the Flink container to run the JAR.

3. Start the Producer: Run your aviation_producer.py.

4. Verify: 

    1. Check the Flink UI: Once you run the job, look at the DAG (Directed Acyclic Graph). You should see your rawSource branching out into two separate sinks from a single transformation point.

    2. Verify Redpanda (Silver Layer):
    Open your terminal and check if the sanitized data is landing in the processed topic:

    ```bash
    rpk topic consume processed_aviation_data
    ```
    3. Verify BigQuery (Gold Layer):
    Run a quick SQL query to see the streaming inserts. Remember, it might take ~60 seconds for the first batch to appear because of the checkpointing interval we set:

    ```sql
    SELECT icao24, callsign, velocity, timestamp 
    FROM `de-zoomcamp-2026-486900.omnistream.aviation_events` 
    ORDER BY timestamp DESC LIMIT 5;
    ```

    

## 🏁 Phase 2 Implementation Summary

By combining the MultiTypeParser and the Generic Serializer, your pipeline architecture now looks like this:

1. Ingestion: 3 Python Producers -> 3 Redpanda Topics.
2. Routing: Flink reads all 3 -> MultiTypeParser splits them into 3 Side Outputs.
3. Silver Layer: Each Side Output sinks back to a processed_ Redpanda topic (Step 4).
4. Gold Layer: Each Side Output sinks to its own BigQuery table (Step 5) using the GenericSerializer.

## 🏁 Final Phase 2 Architecture Check

At this point, you have:

1. 3 Producers: Aviation (OpenSky/Mock), Geo (USGS), and Finance (Alpha Vantage).
2. Redpanda: Topics for raw_ and processed_ (Silver layer).
3. Flink: A unified job using MultiTypeParser to route data.
4. BigQuery: 3 Sinks using a GenericSerializer to land data in Staging.


## You have successfully built a production-grade Medallion Pipeline.

1. Bronze: Raw JSON in Kafka.
2. Silver: Type-safe POJOs in Flink.
3. Gold: Structured, partitioned tables in BigQuery.