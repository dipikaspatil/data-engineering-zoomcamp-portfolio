# Phase 3

## 👉 Define Phase 3: Validation + DLQ + Processed Topics

That’s where your architecture becomes truly differentiated.

- exact Flink logic
- topic design
- validation rules
- DLQ structure

## Phase 3 goal

Build the validation, routing, and isolation layer in Flink so that each incoming raw record is:

- identified by type
- validated against basic quality rules
- routed to a clean processed topic if valid
- routed to DLQ if invalid or unknown

## What Phase 3 should produce

At the end of this phase, your flow should look like:

```
raw_aviation_data
raw_geo_data
raw_finance_data
        ↓
Flink Parser + Validator + Router
        ↓
processed_aviation_data
processed_geo_data
processed_finance_data
        +
dead_letter_queue
```

So the output of Phase 3 is not BigQuery-first.
It is trusted streaming topics first.

## Phase 3 responsibilities

Your Flink layer should now do 4 things:

1. Parse - Read raw JSON safely.

2. Identify - Figure out whether the record is aviation, geo, or finance.

3. Validate - Apply domain-specific rules.

4. Route - Send:
    - valid records → processed topic
    - invalid records → DLQ

## Processed topics

Separate processed topics:

- processed_aviation_data
- processed_geo_data
- processed_finance_data

And one shared DLQ:

- dead_letter_queue

## DLQ schema

Objective - Make DLQ records rich enough to debug later.

Example:
```json
{
  "source_topic": "raw_geo_data",
  "record_type": "geo",
  "error_type": "VALIDATION_ERROR",
  "error_reason": "latitude out of range",
  "raw_payload": "{\"id\":\"...\",\"mag\":3.2,...}",
  "failed_at": 1774809999000
}
```

Recommended fields:

- source_topic
- record_type
- error_type
- error_reason
- raw_payload
- failed_at

Optional later:

- pipeline_stage
- retryable
- schema_version

## Validation rules by domain

I am keeping Phase 3 simple.

### Geo validation

A geo record is valid if:

- id is not null or blank
- timestamp is not null
- lat is between -90 and 90
- lon is between -180 and 180
- depth is not null
- mag is not null

Method:

```java
private static boolean isValidGeo(GeoRecord r) {
    return r != null
        && r.getId() != null && !r.getId().isBlank()
        && r.getTimestamp() != null
        && r.getLat() != null && r.getLat() >= -90 && r.getLat() <= 90
        && r.getLon() != null && r.getLon() >= -180 && r.getLon() <= 180
        && r.getDepth() != null
        && r.getMag() != null;
}
```

### Finance validation

A finance record is valid if:

- symbol is not null or blank
- price is not null and > 0
- timestamp is not null

Optional:

- volume >= 0

### Aviation validation

A flight record is valid if:

- icao24 is not null or blank
- timestamp is not null
- latitude is valid if present
- longitude is valid if present
- velocity is non-negative if present

I am not making aviation too strict at first because flight APIs often have partial nulls.

### Error categories

For phase3 using small set of error categories.

- PARSE_ERROR
- UNKNOWN_TYPE
- VALIDATION_ERROR

Examples:

- bad JSON → PARSE_ERROR
- cannot fingerprint record → UNKNOWN_TYPE
- missing required field → VALIDATION_ERROR

### Flink design

I already have MultiTypeParser from Phase 2.

Evolving it into:

- One process function with side outputs

This is best for your current design.

#### Main flow:

- input String rawJson
- attempt parse
- detect type
- map to POJO
- validate
- output valid records to type-specific side outputs
- output DLQ records to DLQ side output

#### Side outputs

Inside MultiTypeParser:

- AVIATION_TAG
- GEO_TAG
- FINANCE_TAG
- DLQ_TAG

Then StreamingJob can sink each one independently.

#### Job wiring

StreamingJob should do something like this conceptually:

```java
SingleOutputStreamOperator<Void> branchedStream = rawStream.process(new MultiTypeParser());

DataStream<FlightRecord> aviationStream = branchedStream.getSideOutput(MultiTypeParser.AVIATION_TAG);
DataStream<GeoRecord> geoStream = branchedStream.getSideOutput(MultiTypeParser.GEO_TAG);
DataStream<FinanceRecord> financeStream = branchedStream.getSideOutput(MultiTypeParser.FINANCE_TAG);
DataStream<DlqRecord> dlqStream = branchedStream.getSideOutput(MultiTypeParser.DLQ_TAG);
```

Then:

- aviation → processed_aviation_data
- geo → processed_geo_data
- finance → processed_finance_data
- dlq → dead_letter_queue

After that, BigQuery sinks should ideally read from the processed streams, not directly from raw-stage parse output like in Phase 2.

#### Architecture Modification

Phase 2 

```
raw topic → parse → BigQuery
```

Phase 3 

```
raw topic → parse/validate → processed topic → BigQuery
                           ↘ DLQ
```

#### POJO for DLQ

```java
package com.omnistream.model;

import java.io.Serializable;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class DlqRecord implements Serializable {
    private String sourceTopic;
    private String recordType;
    private String errorType;
    private String errorReason;
    private String rawPayload;
    private Long failedAt;
}
```

### implementation order

#### Step 1
    - Create DlqRecord model.

#### Step 2
- Update MultiTypeParser to:
    - detect type
    - validate
    - send invalid messages to DLQ_TAG

#### Step 3

Add Kafka sinks for:

- processed_aviation_data
- processed_geo_data
- processed_finance_data
- dead_letter_queue

#### Step 4

- Keep BigQuery sinks temporarily, but attach them to validated streams only.

#### Step 5

- Add GCS archive/error lake.

### Minimal acceptance criteria for Phase 3

When all of this works:

- valid geo message lands in processed_geo_data
- invalid geo message lands in dead_letter_queue
- unknown JSON lands in dead_letter_queue
- valid finance and aviation also route correctly
- BigQuery only receives validated records

### Sanity test cases

Valid geo - Should go to GEO_TAG

```json
{
  "id": "abc123",
  "mag": 3.4,
  "place": "California",
  "timestamp": 1774807640,
  "lon": -121.9,
  "lat": 37.3,
  "depth": 8.2
}
```

Invalid geo - Should go to DLQ_TAG

```bash
docker exec -i redpanda rpk topic produce raw_geo_data <<'EOF'
{"id":"bad-geo-1","mag":2.5,"place":"Test Bad Record","timestamp":1774825000,"lon":-999.0,"lat":37.5,"depth":4.2}
EOF
Produced to partition 1 at offset 18 with timestamp 1774825009480.
```

```json
{
    "id":"bad-geo-1",
    "mag":2.5,
    "place":"Test Bad Record",
    "timestamp":1774825000,
    "lon":-999.0,
    "lat":37.5,
    "depth":4.2
}
```

Output

```bash
{
  "topic": "dead_letter_queue",
  "value": "{\"sourceTopic\":\"raw_geo_data\",\"recordType\":\"geo\",\"errorType\":\"VALIDATION_ERROR\",\"errorReason\":\"Longitude out of range\",\"rawPayload\":\"{\\\"id\\\":\\\"bad-geo-1\\\",\\\"mag\\\":2.5,\\\"place\\\":\\\"Test Bad Record\\\",\\\"timestamp\\\":1774825000,\\\"lon\\\":-999.0,\\\"lat\\\":37.5,\\\"depth\\\":4.2}\",\"failedAt\":1774825009520}",
  "timestamp": 1774825009480,
  "partition": 0,
  "offset": 0
}
```

Unknown type - Should go to DLQ_TAG

```json
{
  "foo": "bar"
}
```

Broken JSON - Should go to DLQ_TAG

```json
{"id":
```