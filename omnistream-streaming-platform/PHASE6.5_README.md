# Phase 6.5 - hardening phase

- Task 1 — archive processed records `Flink → GCS`


- Task 2 — document retention
    - staging = 90 days
    - gold = persistent analytics
    - GCS cold archive = long-term history

- Task 3 — add DLQ retry DAG
    - Airflow periodically retries eligible DLQ records


## Task 1 — archive processed records `Flink → GCS`

### Add a second sink for each processed stream:

- processedGeoStream -> GCS
- processedAviationStream -> GCS
- processedFinanceStream -> GCS


 ### GCS path layout:

 ```
 gs://<project-id>-raw-archive/source_type=geo/year=2026/month=03/day=30/hour=09/part-....
gs://<project-id>-raw-archive/source_type=aviation/year=2026/month=03/day=30/hour=00/part-....
gs://<project-id>-raw-archive/source_type=finance/year=2026/month=03/day=30/hour=00/part-....
```

### How to implement in Flink

The common pattern is:

- map each processed record to a JSON string
- use a FileSink
- configure rolling policy
- point it to GCS bucket path

### Example shape

For each stream:

```java
FileSink<String> geoArchiveSink = FileSink
    .forRowFormat(
        new Path("gs://de-zoomcamp-2026-486900-raw-archive/source_type=geo"),
        new SimpleStringEncoder<String>("UTF-8")
    )
    .withRollingPolicy(
        DefaultRollingPolicy.builder()
            .withRolloverInterval(Duration.ofMinutes(15))
            .withInactivityInterval(Duration.ofMinutes(5))
            .withMaxPartSize(MemorySize.ofMebiBytes(128))
            .build()
    )
    .build();

processedGeoStream
    .map(record -> objectMapper.writeValueAsString(record))
    .sinkTo(geoArchiveSink);
```

And similarly for aviation and finance.

### Clean code structure

- Existing
    - BigQueryGeoSink
    - BigQueryAviationSink
    - BigQueryFinanceSink
- Add
    - GeoArchiveSink
    - AviationArchiveSink
    - FinanceArchiveSink

Or one reusable helper:
- ArchiveSinkFactory.createJsonSink(basePath, sourceType)

### Final story becomes:

- processed records go to BigQuery staging for analytics
- the same processed records go to GCS cold archive for long-term retention
- BigQuery staging expires after 90 days
- archive remains durable and cheap


## Verify
```bash
08-capstone % gcloud storage ls
# Output
gs://de-zoomcamp-2026-486900-error-lake/
gs://de-zoomcamp-2026-486900-raw-archive/

gcloud storage ls --recursive gs://de-zoomcamp-2026-486900-raw-archive/
# Output
------------------------------------------------------------------------------------------------------------------
gs://de-zoomcamp-2026-486900-raw-archive/:

gs://de-zoomcamp-2026-486900-raw-archive/.inprogress/:

gs://de-zoomcamp-2026-486900-raw-archive/.inprogress/de-zoomcamp-2026-486900-raw-archive/:

gs://de-zoomcamp-2026-486900-raw-archive/.inprogress/de-zoomcamp-2026-486900-raw-archive/source_type=aviation/:

gs://de-zoomcamp-2026-486900-raw-archive/.inprogress/de-zoomcamp-2026-486900-raw-archive/source_type=aviation/2026-03-31--19/:

gs://de-zoomcamp-2026-486900-raw-archive/.inprogress/de-zoomcamp-2026-486900-raw-archive/source_type=aviation/2026-03-31--19/part-92d61873-07ee-46a2-9989-2b1db8f3ec6d-0/:
gs://de-zoomcamp-2026-486900-raw-archive/.inprogress/de-zoomcamp-2026-486900-raw-archive/source_type=aviation/2026-03-31--19/part-92d61873-07ee-46a2-9989-2b1db8f3ec6d-0/273a0dcd-6b88-4e37-957d-6bff91ec7e48
gs://de-zoomcamp-2026-486900-raw-archive/.inprogress/de-zoomcamp-2026-486900-raw-archive/source_type=aviation/2026-03-31--19/part-92d61873-07ee-46a2-9989-2b1db8f3ec6d-0/2ccc9532-f6dc-4e2e-a58f-0c3133fc116f
gs://de-zoomcamp-2026-486900-raw-archive/.inprogress/de-zoomcamp-2026-486900-raw-archive/source_type=aviation/2026-03-31--19/part-92d61873-07ee-46a2-9989-2b1db8f3ec6d-0/36896595-f344-43aa-980a-dd2576b611de
gs://de-zoomcamp-2026-486900-raw-archive/.inprogress/de-zoomcamp-2026-486900-raw-archive/source_type=aviation/2026-03-31--19/part-92d61873-07ee-46a2-9989-2b1db8f3ec6d-0/5269df78-053c-4e08-8613-ee0a4e49b71c
gs://de-zoomcamp-2026-486900-raw-archive/.inprogress/de-zoomcamp-2026-486900-raw-archive/source_type=aviation/2026-03-31--19/part-92d61873-07ee-46a2-9989-2b1db8f3ec6d-0/5661df8c-46f2-495d-a5bd-693c08659b13

gs://de-zoomcamp-2026-486900-raw-archive/source_type=aviation/:

gs://de-zoomcamp-2026-486900-raw-archive/source_type=aviation/2026-03-31--18/:
gs://de-zoomcamp-2026-486900-raw-archive/source_type=aviation/2026-03-31--18/part-44cad620-77b5-4314-8392-6cb4183177f9-0

gs://de-zoomcamp-2026-486900-raw-archive/source_type=finance/:

gs://de-zoomcamp-2026-486900-raw-archive/source_type=finance/2026-03-31--18/:
gs://de-zoomcamp-2026-486900-raw-archive/source_type=finance/2026-03-31--18/part-0eed1c6d-bde4-497a-adb2-7492fcb6a9e9-0

gs://de-zoomcamp-2026-486900-raw-archive/source_type=geo/:

gs://de-zoomcamp-2026-486900-raw-archive/source_type=geo/2026-03-31--18/:
gs://de-zoomcamp-2026-486900-raw-archive/source_type=geo/2026-03-31--18/part-225d3081-2980-4924-8e14-be70ccf67845-0

--------------------------------------------------------------------------------------------------------------------

gcloud storage ls gs://de-zoomcamp-2026-486900-raw-archive/source_type=geo/
# Output
gs://de-zoomcamp-2026-486900-raw-archive/source_type=geo/2026-03-31--18/

gcloud storage ls gs://de-zoomcamp-2026-486900-raw-archive/source_type=finance/
# Output
gs://de-zoomcamp-2026-486900-raw-archive/source_type=finance/2026-03-31--18/

gcloud storage ls gs://de-zoomcamp-2026-486900-raw-archive/source_type=aviation/
# Output
gs://de-zoomcamp-2026-486900-raw-archive/source_type=aviation/2026-03-31--18/
gs://de-zoomcamp-2026-486900-raw-archive/source_type=aviation/2026-03-31--19/


```

## Screenshots

![GCS raw buckets](../08-capstone/images/GCS_raw_data_buckets.png)

## Task 2 — document retention
    - staging = 90 days
    - gold = persistent analytics
    - GCS cold archive = long-term history

A clean deliverable here is a short retention table in your project docs.

### Already implemented

1. Staging → 90-day purge (BigQuery)
```hcl
default_partition_expiration_ms = 7776000000
```

This means:
```
partitions automatically deleted after 90 days
no manual cleanup needed
```

2. GCS Archive → lifecycle + cost optimization

```hcl
lifecycle_rule {
  condition {
    age = 365
  }
  action {
    type          = "SetStorageClass"
    storage_class = "ARCHIVE"
  }
}
```

Archive behavior is:

- starts as COLDLINE
- after 365 days → moves to ARCHIVE (cheapest storage)
- retained indefinitely (no delete rule)

✔ This is a proper long-term historical archive strategy

3. Gold → persistent

```hcl
google_bigquery_dataset "gold_ds"
```

No expiration = correct for analytics layer

### Summary - Data Retention Strategy

| Layer   | Storage                         | Retention Policy | Enforcement                                              |
| ------- | ------------------------------- | ---------------- | -------------------------------------------------------- |
| Staging | BigQuery (`omnistream_staging`) | 90 days          | Partition expiration (`default_partition_expiration_ms`) |
| Gold    | BigQuery (`omnistream_gold`)    | Persistent       | No expiration                                            |
| Archive | GCS (`raw-archive`)             | Long-term        | Lifecycle rules (Coldline → Archive after 365 days)      |

- Staging Layer
    - Partitioned tables with automatic expiration after 90 days
    - Ensures bounded storage and supports replay window
- Gold Layer
    - Persistent curated datasets for analytics and BI
    - No automatic deletion
- GCS Cold Archive
    - Stores processed records from Flink
    - Data is transitioned to cheaper storage (ARCHIVE) after 365 days
    - Used for audit, reprocessing, and historical recovery

## Task 3 — add DLQ retry DAG

The DAG should:

- run on a schedule
- read eligible DLQ records
- apply retry policy
- republish retryable records to the appropriate source topic
- mark retry attempt metadata
- stop retrying after max attempts
- optionally move permanently failed records to a terminal DLQ table/bucket

A good retry filter usually includes:

- status = RETRYABLE
- retry_count < max_retries
- next_retry_at <= now()


### 🔴 DLQ flow

```
Flink failure
    ↓
Redpanda DLQ topic
    ↓
Dual write:
    → GCS Error Lake (full payload)
    → BigQuery DLQ table (metadata only)
```

### 🔵 Retry flow

```
Airflow DAG
    ↓
Query BigQuery DLQ table (cheap, small)
    ↓
Fetch payload from GCS (via gcs_path)
    ↓
Republish to retry topic
```

### How Airflow should decide what to retry

- Airflow should not read the raw Kafka DLQ topic directly for retry decisions. It should read a small control table.

Retryable records should look like:

- status = RETRYABLE
- errorClassification = TRANSIENT
- retryCount < maxRetries
- nextRetryAt <= now

Do not auto-retry:

- VALIDATION_ERROR caused by permanently bad data
- UNKNOWN_TYPE
- repeated parse failures
- records missing required business keys

### Write path

When Flink sends a DLQ record:

1. emit to dead_letter_queue
2. write full JSON record to GCS Error Lake
3. write a small metadata row to BigQuery DLQ control table

### Retry path

Airflow:

1. queries BigQuery for eligible retry rows
2. reads the payload from payload_gcs_path
3. republishes to a retry topic
4. increments retry_count
5. updates next_retry_at and status

### GCS error lake sink for DLQ

```java
dlqStream
    .map(record -> OBJECT_MAPPER.writeValueAsString(record))
    .sinkTo(buildGcsArchiveSink("gs://" + errorLakeBucket + "/error_stage=parser"))
    .name("DlqGcsErrorLakeSink");
```

### BigQuery DLQ metadata sink

Not the full raw payload. A metadata projection.

For example, create a second stream:

```java
DataStream<DlqMetadataRecord> dlqMetadataStream = dlqStream.map(record ->
    new DlqMetadataRecord(
        record.getDlqId(),
        record.getSourceTopic(),
        record.getRecordType(),
        record.getErrorType(),
        record.getErrorClassification(),
        record.getRetryCount(),
        record.getMaxRetries(),
        record.getNextRetryAt(),
        record.getStatus(),
        record.getPayloadGcsPath(),
        record.getFailedAt()
    )
);
```

### BigQuery DLQ metadata schema

```java
dlq_id STRING
source_topic STRING
record_type STRING
error_stage STRING
error_type STRING
error_classification STRING
status STRING
retry_count INT64
max_retries INT64
next_retry_at TIMESTAMP
payload_gcs_path STRING
failed_at TIMESTAMP
last_retried_at TIMESTAMP
idempotency_key STRING
```

### retry statuses
```
NEW
RETRYABLE
MANUAL_REVIEW
RETRIED
FAILED_PERMANENT
RESOLVED
```

### retry topic strategy

Do not replay directly into the raw source topics first. Use:
```
retry_geo_data
retry_finance_data
retry_aviation_data
```
That makes the system safer and easier to observe.

### Testing plan
Test 1

Send a malformed record.
Expect:
```
DLQ Kafka message
GCS Error Lake object
BigQuery DLQ metadata row
status likely PERMANENT or MANUAL_REVIEW
```

Test 2

Simulate a transient sink failure.
Expect:
```
DLQ metadata classified TRANSIENT
Airflow later picks it up
record replayed to retry topic
retry count increments
```

Test 3

Replay same record twice.
Expect:
```
downstream dedup prevents duplicates
```

### Implementation order

1. Expand DlqRecord
2. Add GCS Error Lake sink for DLQ
3. Add a separate lean BigQuery DLQ metadata model
4. Build Airflow DAG against the metadata table
5. Replay from GCS payload path to retry topic

## Task 4 — optionally add archive validation DAG

This is a very good operational hardening task.

The DAG can:

- check expected partitions by date/hour/source type
- verify at least one object exists for active partitions
- optionally compare archive counts vs downstream counts
- alert if a partition is missing

A lightweight first version is enough:

- for each source_type
- for the last N hours
- verify expected GCS prefix exists and contains at least one finalized object

## Testing

Valid cases
    - valid geo JSON → GEO_TAG
    - valid finance JSON → FINANCE_TAG
    - valid aviation JSON → AVIATION_TAG
Invalid cases
    - malformed JSON → DLQ_TAG, PARSE_ERROR
    - unknown schema JSON → DLQ_TAG, UNKNOWN_TYPE
    - bad geo latitude → DLQ_TAG, VALIDATION_ERROR
    - finance with negative price → DLQ_TAG, VALIDATION_ERROR
    - aviation with invalid longitude → DLQ_TAG, VALIDATION_ERROR

### Test dataset

Produce:

- 1 valid geo
- 1 valid finance
- 1 valid aviation
- 1 malformed JSON
- 1 unknown-type JSON
- 1 invalid geo JSON

Expected results
- processed topics receive 3 valid messages
- dead_letter_queue receives 3 invalid messages
- GCS cold archive gets 3 valid archived records
- BigQuery staging gets 3 valid rows
- no valid record ends up in DLQ
- no invalid record ends up in BigQuery

That proves the current core flow.

## Test the new DLQ expansion

After adding:

- richer DlqRecord
- GCS Error Lake sink
- BigQuery dlq_control metadata sink

Test

Permanent failure test

Send:

- malformed JSON
- invalid finance price
- unknown object shape

Expected:

- message lands in dead_letter_queue
- full DLQ JSON lands in GCS Error Lake
- metadata lands in BigQuery dlq_control
- status/classification are correct:
    - parse/validation → likely FAILED_PERMANENT
    - unknown type → likely MANUAL_REVIEW

### Transient retry test

Since current parser mostly creates permanent failures, create one test DLQ metadata row manually with:

- status = RETRYABLE
- errorClassification = TRANSIENT
- payloadGcsPath pointing to a real GCS object
- nextRetryAt in the past

Then let Airflow retry it.

That’s the easiest way to validate the retry DAG before adding true transient failures in Flink.

### Test the Airflow DAG

Use the DAG only after the DLQ control table is populated.

Airflow test expectations

When DAG runs:

- it queries eligible retryable rows
- fetches payload from GCS
- republishes to retry topic
- increments retry count / updates status

Expected outcome:

- message appears in retry topic
- metadata row updates
- replayed message can be consumed by Flink

### test order

#### Phase A — current code smoke test

1. start Redpanda, Flink, Airflow
2. submit Flink job
3. produce 6 controlled test messages
4. verify:
    - processed Kafka topics
    - dead_letter_queue
    - GCS archive
    - BigQuery staging

Result - Started producer. Data loaded into processed kafka topics, 3 staging, GCS cold archive

#### Phase B — DLQ enhancement test

After code changes:

1. redeploy Flink
2. send invalid records


```bash
# Malformed JSON 
echo '{"symbol":"AAPL","price":' | docker exec -i redpanda rpk topic produce raw_finance_data
# Output
Produced to partition 0 at offset 0 with timestamp 1775002616839.



# Unknown type
echo '{"foo":"bar","hello":"world"}' | docker exec -i redpanda rpk topic produce raw_geo_data
# Output
Produced to partition 2 at offset 5 with timestamp 1775002641788.



# Invalid geo
echo '{"id":"geo-bad","mag":4.2,"place":"CA","timestamp":1774983000000,"lon":-121.9,"lat":137.3,"depth":10.5}' | docker exec -i redpanda rpk topic produce raw_geo_data
#Output
Produced to partition 1 at offset 3 with timestamp 1775002664315.
```

Expected result

Based on current parser:

- all 3 should go to dead_letter_queue
- none should go to processed Kafka topics
- all should go to BigQuery staging - dlq_control
- none should go to GCS cold archive
- all should go to GCS Error lake

all should go to BigQuery staging - dlq_control
![BQ dlq control stg](../08-capstone/images/BQ_staging_dlq_control.png)

all should go to GCS Error lake
![GCS Error lake](../08-capstone/images/GCS_error_lake.png)

```bash
# Records added to dead_letter_queue
(venv) niteshmishra@Mac flink-processor % docker exec -it redpanda rpk topic consume dead_letter_queue --num -3
{
  "topic": "dead_letter_queue",
  "value": "{\"dlqId\":\"330c1cc6-02d4-4b5b-97d6-f4f20618e101\",\"sourceTopic\":\"unknown\",\"recordType\":\"unknown\",\"errorStage\":\"PARSE\",\"errorType\":\"PARSE_ERROR\",\"errorReason\":\"Unexpected end-of-input within/between Object entries\\n at [Source: (String)\\\"{\\\"symbol\\\":\\\"AAPL\\\",\\\"price\\\":\\\"; line: 1, column: 26]\",\"errorClassification\":\"PERMANENT\",\"rawPayload\":\"{\\\"symbol\\\":\\\"AAPL\\\",\\\"price\\\":\",\"payloadGcsPath\":null,\"idempotencyKey\":\"df1b825c36e84bff5619752b59c587ec499f181e204c278d8a71782146f8a9fe\",\"retryCount\":0,\"maxRetries\":2,\"nextRetryAt\":null,\"status\":\"FAILED_PERMANENT\",\"failedAt\":1775002616974,\"lastRetriedAt\":null}",
  "timestamp": 1775002616839,
  "partition": 0,
  "offset": 0
}
{
  "topic": "dead_letter_queue",
  "value": "{\"dlqId\":\"d03ee3b8-9603-4838-bc36-736204cd1076\",\"sourceTopic\":\"unknown\",\"recordType\":\"unknown\",\"errorStage\":\"CLASSIFY\",\"errorType\":\"UNKNOWN_TYPE\",\"errorReason\":\"Unable to classify message\",\"errorClassification\":\"MANUAL_REVIEW\",\"rawPayload\":\"{\\\"foo\\\":\\\"bar\\\",\\\"hello\\\":\\\"world\\\"}\",\"payloadGcsPath\":null,\"idempotencyKey\":\"0c4872cf813596d1f01e721559962641731b6ad0da3725e9a1629dde95131719\",\"retryCount\":0,\"maxRetries\":2,\"nextRetryAt\":null,\"status\":\"MANUAL_REVIEW\",\"failedAt\":1775002641812,\"lastRetriedAt\":null}",
  "timestamp": 1775002641788,
  "partition": 0,
  "offset": 1
}
{
  "topic": "dead_letter_queue",
  "value": "{\"dlqId\":\"4d3d5dbd-e55c-49a4-8c14-7098b048ea8e\",\"sourceTopic\":\"raw_geo_data\",\"recordType\":\"geo\",\"errorStage\":\"VALIDATE\",\"errorType\":\"VALIDATION_ERROR\",\"errorReason\":\"Latitude out of range\",\"errorClassification\":\"PERMANENT\",\"rawPayload\":\"{\\\"id\\\":\\\"geo-bad\\\",\\\"mag\\\":4.2,\\\"place\\\":\\\"CA\\\",\\\"timestamp\\\":1774983000000,\\\"lon\\\":-121.9,\\\"lat\\\":137.3,\\\"depth\\\":10.5}\",\"payloadGcsPath\":null,\"idempotencyKey\":\"be6df8552326b3403e4a472544a7403b4b9fcf9bd738682a70486370479ebd73\",\"retryCount\":0,\"maxRetries\":2,\"nextRetryAt\":null,\"status\":\"FAILED_PERMANENT\",\"failedAt\":1775002664338,\"lastRetriedAt\":null}",
  "timestamp": 1775002664315,
  "partition": 0,
  "offset": 2
}
```


```bash
# Records NOT added to processed data kafka topic - all are valid records
docker exec -it redpanda rpk topic consume processed_geo_data --offset -1
{
  "topic": "processed_geo_data",
  "value": "{\"id\":\"nc75336662\",\"mag\":1.11,\"place\":\"2 km NW of The Geysers, CA\",\"timestamp\":1775001630,\"lon\":-122.768501281738,\"lat\":38.7881660461426,\"depth\":1.13999998569489}",
  "timestamp": 1775001847969,
  "partition": 2,
  "offset": 11
}

(venv) niteshmishra@Mac flink-processor % docker exec -it redpanda rpk topic consume processed_aviation_data --offset -1
{
  "topic": "processed_aviation_data",
  "value": "{\"icao24\":\"a52bd9\",\"callsign\":\"N432PH\",\"origin_country\":\"United States\",\"timestamp\":1775002006,\"latitude\":32.3576,\"longitude\":-97.434,\"velocity\":20.06}",
  "timestamp": 1775002006205,
  "partition": 2,
  "offset": 91
}
{
  "topic": "processed_aviation_data",
  "value": "{\"icao24\":\"a1befc\",\"callsign\":\"UAL1509\",\"origin_country\":\"United States\",\"timestamp\":1775001844,\"latitude\":37.618,\"longitude\":-122.3777,\"velocity\":10.29}",
  "timestamp": 1775001844007,
  "partition": 0,
  "offset": 97
}
{
  "topic": "processed_aviation_data",
  "value": "{\"icao24\":\"a2cbb4\",\"callsign\":\"LJY296\",\"origin_country\":\"United States\",\"timestamp\":1775002137,\"latitude\":37.2024,\"longitude\":-79.7637,\"velocity\":252.34}",
  "timestamp": 1775002137580,
  "partition": 1,
  "offset": 189
}

(venv) niteshmishra@Mac flink-processor % docker exec -it redpanda rpk topic consume processed_finance_data --offset -1
{
  "topic": "processed_finance_data",
  "value": "{\"symbol\":\"IBM\",\"price\":242.39,\"volume\":4705485,\"timestamp\":1775001542,\"change_percent\":\"2.1665%\"}",
  "timestamp": 1775001542612,
  "partition": 2,
  "offset": 0
}
```




Because your parser sends invalid cases to DLQ_TAG with:

- PARSE_ERROR
- UNKNOWN_TYPE
- VALIDATION_ERROR

Check:

- dead_letter_queue contains 3 records
- processed topics do not get these bad records
- staging row counts do not increase because of them
- archive counts do not increase because of them


verify:
- DLQ Kafka
- GCS Error Lake
- BigQuery dlq_control

#### Phase C — retry DAG test
1. insert one retryable metadata row
2. run omnistream_dlq_retry
3. verify retry topic got message
4. verify metadata updated


1. Send 2 bad raw records

These should create 2 DLQ records, 2 GCS files, and 2 dlq_control rows.

Unknown type:

```bash
echo '{"foo":"bar"}' | docker exec -i redpanda rpk topic produce raw_geo_data

# Output
Produced to partition 0 at offset 0 with timestamp 1775087728181.
```

Parse error:

```bash
echo '{"symbol":"AAPL","price":}' | docker exec -i redpanda rpk topic produce raw_finance_data

# Output
Produced to partition 0 at offset 0 with timestamp 1775087736145.
```

2. Verify 2 separate files in GCS Error Lake

```bash
gcloud storage ls --recursive gs://de-zoomcamp-2026-486900-error-lake/

# Output
gs://de-zoomcamp-2026-486900-error-lake/:

gs://de-zoomcamp-2026-486900-error-lake/error_stage=classify/:

gs://de-zoomcamp-2026-486900-error-lake/error_stage=classify/2026-04-01--23/:

gs://de-zoomcamp-2026-486900-error-lake/error_stage=classify/2026-04-01--23/dlq_id=25bcdbb1-365b-4f0c-a089-932ca5a84831/:
gs://de-zoomcamp-2026-486900-error-lake/error_stage=classify/2026-04-01--23/dlq_id=25bcdbb1-365b-4f0c-a089-932ca5a84831/part-048ede20-c849-472a-acc1-4d1905f44239-0

gs://de-zoomcamp-2026-486900-error-lake/error_stage=parse/:

gs://de-zoomcamp-2026-486900-error-lake/error_stage=parse/2026-04-01--23/:

gs://de-zoomcamp-2026-486900-error-lake/error_stage=parse/2026-04-01--23/dlq_id=4f286a2e-5120-4d22-9d99-eb45d4437d69/:
gs://de-zoomcamp-2026-486900-error-lake/error_stage=parse/2026-04-01--23/dlq_id=4f286a2e-5120-4d22-9d99-eb45d4437d69/part-7ba4aa04-ef4f-401c-abe9-961cdf29d8de-0
```

![GCS error lake](../08-capstone/images/GCS_error_lake_2.png)

3. Verify rows in dlq_control

Query the latest two rows:

```sql
(venv) niteshmishra@Mac flink-processor % bq query --use_legacy_sql=false '
SELECT
  dlqId,
  sourceTopic,
  recordType,
  errorStage,
  errorType,
  errorClassification,
  status,
  failedAt,
  payloadGcsPath
FROM `de-zoomcamp-2026-486900.omnistream_staging.dlq_control`
ORDER BY failedAt DESC
LIMIT 5
'

+--------------------------------------+-------------+------------+------------+--------------+---------------------+------------------+---------------+----------------------------------------------------------------------------------------------------------------------------------+
|                dlqId                 | sourceTopic | recordType | errorStage |  errorType   | errorClassification |      status      |   failedAt    |                                                          payloadGcsPath                                                          |
+--------------------------------------+-------------+------------+------------+--------------+---------------------+------------------+---------------+----------------------------------------------------------------------------------------------------------------------------------+
| bbde3c85-cf39-4809-83a3-e669777aac49 | unknown     | unknown    | PARSE      | PARSE_ERROR  | PERMANENT           | FAILED_PERMANENT | 1775087736180 | gs://de-zoomcamp-2026-486900-error-lake/error_stage=parse/2026-04-01--23/dlq_id=bbde3c85-cf39-4809-83a3-e669777aac49/part-0-0    |
| 64d7106e-e026-4d93-96be-9aaf1f60dfde | unknown     | unknown    | CLASSIFY   | UNKNOWN_TYPE | MANUAL_REVIEW       | MANUAL_REVIEW    | 1775087728329 | gs://de-zoomcamp-2026-486900-error-lake/error_stage=classify/2026-04-01--23/dlq_id=64d7106e-e026-4d93-96be-9aaf1f60dfde/part-0-0 |
+--------------------------------------+-------------+------------+------------+--------------+---------------------+------------------+---------------+----------------------------------------------------------------------------------------------------------------------------------+
```

![BQ dlq_control retryable 2](../08-capstone/images/BQ_staging_dlq_control_retryable_2.png)

Expected:

one MANUAL_REVIEW
one FAILED_PERMANENT

4. Create one retryable row from one of those files

Pick one of the GCS object paths from step 2 and insert one synthetic retryable row pointing to that exact file:

```sql
bq query --use_legacy_sql=false '
INSERT INTO `de-zoomcamp-2026-486900.omnistream_staging.dlq_control`
(
  dlqId,
  sourceTopic,
  recordType,
  errorStage,
  errorType,
  errorClassification,
  status,
  retryCount,
  maxRetries,
  nextRetryAt,
  failedAt,
  lastRetriedAt,
  payloadGcsPath,
  idempotencyKey
)
VALUES
(
  "retry-dlq-001",
  "raw_geo_data",
  "geo",
  "ENRICH",
  "NETWORK_ERROR",
  "TRANSIENT",
  "RETRYABLE",
  0,
  2,
  UNIX_MILLIS(TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 MINUTE)),
  UNIX_MILLIS(CURRENT_TIMESTAMP()),
  NULL,
  "gs://de-zoomcamp-2026-486900-error-lake/error_stage=parse/2026-04-01--23/dlq_id=bbde3c85-cf39-4809-83a3-e669777aac49/part-0-0",
  "retry-test-001"
)'

-- Output
Waiting on bqjob_r2d5b10101828a1fe_0000019d4b802952_1 ... (1s) Current status: DONE
Number of affected rows: 1
```

This is okay for DAG testing even though the file content is from a permanent parse error. It will validate:

- Airflow can find the row
- Airflow can read GCS
- Airflow can publish to Kafka
- Airflow can update metadata

5. Trigger the DAG

```bash
docker exec -it omnistream-airflow airflow dags trigger omnistream_dlq_retry

# Output
[2026-04-02T11:25:42.754+0000] {__init__.py:42} INFO - Loaded API auth backend: airflow.api.auth.backend.session
     |                      |                       |                      |                       |          |                  | last_scheduling_deci |                       |          |            |
conf | dag_id               | dag_run_id            | data_interval_start  | data_interval_end     | end_date | external_trigger | sion                 | logical_date          | run_type | start_date | state
=====+======================+=======================+======================+=======================+==========+==================+======================+=======================+==========+============+=======
{}   | omnistream_dlq_retry | manual__2026-04-02T11 | 2026-04-02           | 2026-04-02            | None     | True             | None                 | 2026-04-02            | manual   | None       | queued
     |                      | :25:43+00:00          | 10:30:00+00:00       | 11:00:00+00:00        |          |                  |                      | 11:25:43+00:00        |          |            |


docker exec -it omnistream-airflow airflow dags list-runs -d omnistream_dlq_retry

dag_id               | run_id                            | state  | execution_date            | start_date | end_date
=====================+===================================+========+===========================+============+=========
omnistream_dlq_retry | manual__2026-04-02T11:25:43+00:00 | queued | 2026-04-02T11:25:43+00:00 |            |

(venv) niteshmishra@Mac flink-processor % docker exec -it omnistream-airflow airflow dags unpause omnistream_dlq_retry
Dag: omnistream_dlq_retry, paused: False

```

6. Start retry topic consumer

```bash
(venv) niteshmishra@Mac docker % docker exec -it redpanda rpk topic consume retry_geo_data --num -5

{
  "topic": "retry_geo_data",
  "value": "{\"symbol\":\"AAPL\",\"price\":}",
  "timestamp": 1775131830396,
  "partition": 0,
  "offset": 0
}

```

7. Check DAG run
```bash
docker exec -it omnistream-airflow airflow dags list-runs -d omnistream_dlq_retry

# Output

(venv) niteshmishra@Mac docker % docker exec -it omnistream-airflow airflow dags list-runs -d omnistream_dlq_retry
dag_id               | run_id                               | state   | execution_date            | start_date                       | end_date
=====================+======================================+=========+===========================+==================================+=================================
omnistream_dlq_retry | scheduled__2026-04-02T14:00:00+00:00 | success | 2026-04-02T14:00:00+00:00 | 2026-04-02T14:30:00.214917+00:00 | 2026-04-02T14:30:08.649588+00:00
omnistream_dlq_retry | scheduled__2026-04-02T13:30:00+00:00 | success | 2026-04-02T13:30:00+00:00 | 2026-04-02T14:06:10.579481+00:00 | 2026-04-02T14:06:19.798460+00:00
omnistream_dlq_retry | scheduled__2026-04-02T13:00:00+00:00 | success | 2026-04-02T13:00:00+00:00 | 2026-04-02T13:33:00.389666+00:00 | 2026-04-02T13:33:13.435809+00:00
omnistream_dlq_retry | scheduled__2026-04-02T12:30:00+00:00 | success | 2026-04-02T12:30:00+00:00 | 2026-04-02T13:03:29.313750+00:00 | 2026-04-02T13:03:40.391801+00:00
omnistream_dlq_retry | manual__2026-04-02T12:10:19+00:00    | success | 2026-04-02T12:10:19+00:00 | 2026-04-02T12:10:20.180192+00:00 | 2026-04-02T12:10:42.306022+00:00
omnistream_dlq_retry | scheduled__2026-04-02T12:00:00+00:00 | success | 2026-04-02T12:00:00+00:00 | 2026-04-02T12:44:50.451450+00:00 | 2026-04-02T12:45:02.858860+00:00
```

![Airflow DAG successful](../08-capstone/images/DAG_retry_geo_record_successful.png)

8. Verify outcome

Check the retry topic terminal from step 5.

Then verify metadata updated:

```bash
bq query --use_legacy_sql=false '
SELECT
  dlqId,
  status,
  retryCount,
  lastRetriedAt,
  nextRetryAt,
  payloadGcsPath
FROM `de-zoomcamp-2026-486900.omnistream_staging.dlq_control`
WHERE idempotencyKey = "retry-test-001"
LIMIT 1
'

+---------------+---------+------------+---------------+---------------+-----------------------------------------------------------------------------------------------------------------------+
|     dlqId     | status  | retryCount | lastRetriedAt |  nextRetryAt  |                                                    payloadGcsPath                                                     |
+---------------+---------+------------+---------------+---------------+-----------------------------------------------------------------------------------------------------------------------+
| retry-dlq-001 | RETRIED |          1 | 1775131835766 | 1775135435766 | gs://de-zoomcamp-2026-486900-error-lake/error_stage=parse/2026-04-01--23/dlq_id=bbde3c85-cf39-4809-83a3-e669777aac49/ |
+---------------+---------+------------+---------------+---------------+-----------------------------------------------------------------------------------------------------------------------+
```

What counts as success
- 2 bad raw records create 2 separate GCS files
- 2 rows appear in dlq_control
- the synthetic retryable row is picked by Airflow
- one message lands in retry_geo_data
- retryCount increments
- lastRetriedAt is populated

## Task 4 

- Automate Flink jar upload

1. Mount that built JAR into the JobManager

Instead of relying on the UI upload, mount the target directory directly into Flink.

In both jobmanager and taskmanager, add in docker-compose.yaml

```yaml
      - ../flink-processor/target:/opt/flink/usrlib
```

2. Build the JAR before starting containers

From flink-processor project:

```bash
mvn clean package -DskipTests

# this should generate
target/omnistream-processor-1.0-SNAPSHOT.jar
```

3. Submit the JAR automatically with a deploy script

Create a small script, for example deploy-flink-job.sh:

```bash
#!/usr/bin/env bash
set -euo pipefail

JAR_PATH="/opt/flink/usrlib/omnistream-processor-1.0-SNAPSHOT.jar"
MAIN_CLASS="com.omnistream.pipeline.Main"

echo "Waiting for Flink JobManager..."
until curl -s http://localhost:8081/overview >/dev/null; do
  sleep 3
done

echo "Submitting Flink job..."
docker exec omnistream-jobmanager /opt/flink/bin/flink run \
  -d \
  -c ${MAIN_CLASS} \
  ${JAR_PATH}

echo "Job submitted."
```

Make it executable:
```bash
chmod +x deploy-flink-job.sh
```

Then run:

```bash
docker compose up -d
./deploy-flink-job.sh
```

Cokmand to get number of records in all topics 

```bash
docker exec redpanda rpk topic list | awk 'NR>1 {print $1}' | while read t; do echo -n "$t: "; docker exec redpanda rpk topic describe "$t" -p | awk 'NR>1 {sum += ($6 - $5)} END {print sum}'; done

# Output
dead_letter_queue: 0
processed_aviation_data: 0
processed_finance_data: 0
processed_geo_data: 0
raw_aviation_data: 0
raw_finance_data: 0
raw_geo_data: 0
retry_aviation_data: 0
retry_finance_data: 0
retry_geo_data: 0
```

Delete all topics

```bash
docker exec redpanda rpk topic list | tail -n +2 | awk '{print $1}' | xargs -I {} docker exec redpanda rpk topic delete {}

TOPIC              STATUS
dead_letter_queue  OK
TOPIC                    STATUS
processed_aviation_data  OK
TOPIC                   STATUS
processed_finance_data  OK
TOPIC               STATUS
processed_geo_data  OK
TOPIC              STATUS
raw_aviation_data  OK
TOPIC             STATUS
raw_finance_data  OK
TOPIC         STATUS
raw_geo_data  OK
TOPIC                STATUS
retry_aviation_data  OK
TOPIC               STATUS
retry_finance_data  OK
TOPIC           STATUS
retry_geo_data  OK
```

Create all topics

```bash
for t in raw_aviation_data raw_finance_data raw_geo_data \
         retry_aviation_data retry_finance_data retry_geo_data \
         processed_aviation_data processed_finance_data processed_geo_data \
         dead_letter_queue; do
  docker exec redpanda rpk topic create $t
done
```


for t in raw_aviation_data raw_finance_data raw_geo_data; do
  docker exec redpanda rpk topic create $t
done