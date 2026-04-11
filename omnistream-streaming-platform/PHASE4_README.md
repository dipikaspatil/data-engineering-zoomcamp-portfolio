# Phase 4

## 👉 Define Phase 4: processed_* topics -> BigQuery stg tables

## Phase 4 flow

```
Keep the pipeline as:

raw_* topics
   ↓
MultiTypeParser
   ↓
processed_* topics
   ↓
BigQuery tables
```

And in the Flink job, sink the validated streams directly to those three BigQuery tables.

## What to wire

We already have these streams in StreamingJob from PHASE3:

```
processedAviationStream
processedFinanceStream
processedGeoStream
```
Now attach BigQuery sinks to each stream

Example

```java
processedAviationStream
        .map(StreamingJob::toAviationGenericRecord)
        .returns(new GenericRecordAvroTypeInfo(AVIATION_AVRO_SCHEMA))
        .sinkTo(buildBqSink(env, projectId, dataset, "raw_aviation_data"))
        .name("AviationBigQuerySink");
```

## 🧠 Architecture checkpoint

```
            ┌──────────────┐
            │ raw_* topics │
            └──────┬───────┘
                   ↓
          MultiTypeParser
                   ↓
   ┌───────────────┼───────────────┐
   ↓               ↓               ↓
processed_geo  processed_fin  processed_aviation
   ↓               ↓               ↓
Kafka (Silver)   Kafka           Kafka
   ↓               ↓               ↓
    BigQuery (Gold staging tables)
```

## Data loaded from processed stream to Big Query staging tables

![Big Query Aviation staging table ss](../08-capstone/images/BQ_staging_aviation_data.png)

![Big Query Geo staging table ss](../08-capstone/images/BQ_staging_geo_data.png)

![Big Query Finance staging table ss](../08-capstone/images/BQ_staging_finance_data.png)


## Include fix to avoid any duplicates in Big Query staging tables

processed Kafka = validated operational stream

BigQuery staging = validated + deduplicated analytical stream

### Why should we avoid duplicates:

- Kafka processed topics unchanged
- BigQuery staging clean
- dbt simpler
- warehouse stays clean
- staging really means validated + unique

### Design

```
processed_* topics
   ↓
Flink dedup for BQ path only
   ↓
BigQuery staging tables
```

So:

Kafka silver topics can still contain retries if needed
BigQuery staging gets unique rows only

### Dedup key by domain

Use stable business keys.

- For geo: `id`
- For finance: `symbol + timestamp`
- For aviation: `icao24 + timestamp` 
    - If icao24 + timestamp is too weak later, we can add latitude/longitude or callsign, but start simple.

### Flink approach

Use keyBy(...).process(...) with state to remember seen keys.

Example

```java
processedGeoStream
    .keyBy(GeoRecord::getId)
    .process(new DeduplicateGeoRecords())
```

### use TTL

Do not keep keys forever.

Use state TTL, for example:

- geo: 24 hours
- finance: 24 hours
- aviation: 24 hours

That prevents unbounded state growth.

### Clean pattern

For each keyed record:

if key not seen before → emit to BigQuery stream

if already seen → drop

### Example flow for Geo

```
raw_geo_data
   ↓
MultiTypeParser
   ↓
processedGeoStream
   ├─→ processed_geo_data
   └─→ DeduplicateGeoRecords
         └─→ BigQuery raw_geo_data
```

### Testing

```sql
select count(id) cnt, id from de-zoomcamp-2026-486900.omnistream_staging.raw_geo_data group by id having cnt > 1; - no data select count(id) cnt, id from de-zoomcamp-2026-486900.omnistream_staging.raw_geo_data group by id having cnt > 1; - 23 records
```

### Phase4 Final architecture

```
raw_* topics
   ↓
MultiTypeParser
   ↓
processed_* streams ───────────────→ Kafka (Silver)
   ↓
Deduplicate*Records
   ↓
unique_* streams ─────────────────→ BigQuery (Gold)
   ↓
invalid → DLQ
```

### 🚀 What is achieved so far

- Multi-source ingestion
- Schema detection
- Validation firewall
- DLQ isolation
- Kafka silver layer
- Stateful deduplication
- Clean BigQuery gold ingestion

### 1. Staging layer

For each stream:
- rename columns
- cast data types
- parse timestamps
- remove bad/null rows where needed

### 2. Core analytics layer

Create a unified event model:

- fct_events_unified
- event_id
- source_type
- event_timestamp
- event_date
- event_hour
- metric_value or domain-specific attributes

### 3. Mart layer

Build dashboard-ready aggregates:

- hourly counts by source
- daily counts by source
- top categories/types
- latest event snapshots