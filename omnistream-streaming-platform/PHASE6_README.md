# Phase 6 — Dashboards

This should consume only the dbt marts, not raw tables.

## Goal:

- show business/analytics value from your pipeline
- make the project easy to understand during evaluation
- Build a dashboard on top of:
    - de-zoomcamp-2026-486900.omnistream_gold.mart_event_volume_by_source
    - de-zoomcamp-2026-486900.omnistream_gold.mart_event_volume_by_hour

That gives the minimum 2-tile dashboard.

## Best first dashboard:

- Tile 1: records by source/domain
- Tile 2: records over time

## Phase 6 scope

### Dashboard 1: Pipeline Overview

- KPI: total records processed
- bar chart: records by source
- line chart: hourly event volume

### Optional domain-specific views

If time allows:

- Geo: recent events by place/type
- Aviation: events by aircraft/status
- Finance: activity by symbol

But the overview dashboard should come first.

### Objective

Show that the pipeline produces useful analytics, not just raw ingestion.

- Best first dashboard
    - OmniStream Pipeline Overview
        - Tile 1 — Records by source
            - Chart type:
                - bar chart
            - Source:
                - mart_event_volume_by_source
            - Shows:
                - Geo vs Aviation vs Finance
            - Fields:
                - dimension: source_type
                - metric: event_count

        - Tile 2 — Records over time
            - Chart type:
                - line chart
            - Source:
                - mart_event_volume_by_hour
            - Shows:
                - event volume per hour
            - Fields:
                - dimension: event_date + event_hour
                - breakdown: source_type
                - metric: event_count

- Stronger dashboard version
    - Add 2 more tiles to look more complete:
        - Tile 3 — Latest geo events
            - Chart type:
                - table
            - Source:
                - mart_geo_activity or direct recent-event mart
        - Tile 4 — Top finance symbols / aviation activity
            - Chart type:
                - bar chart or table
            - Source:
                - mart_geo_activity or direct recent-event mart

## Phase 6 deliverables
- one dashboard
- minimum 2 tiles
- dashboard reads only from dbt marts
- screenshots for README later
- short explanation of what each chart shows

## priority order
- bar chart by source
- line chart by hour
- optional domain-specific tile
- optional KPI cards

## Phase 6 approach - Use Looker Studio.

### Dashboard v1 - OmniStream Pipeline Overview

#### Tile 1 — Records by source

Use:

- table: mart_event_volume_by_source
- chart: bar chart

Config:

- Dimension: source_type
- Metric: event_count

What it shows:

- aviation vs geo vs finance volume

#### Tile 2 — Records over time

Use:

- table: mart_event_volume_by_hour
- chart: time series / line chart

Config:

- Dimension: create a datetime field from event_date + event_hour
- Breakdown dimension: source_type
- Metric: event_count

What it shows:

- how event volume changes over time by domain

#### Tile 3 - KPI scorecards

Since aviation dominates volume, add one more tile to feel more complete:

Examples:

Total Aviation Events
Total Geo Events
Total Finance Events
Total Events

Use:

- table: mart_event_volume_by_source.
- chart: line chart

### Important modeling note for Looker Studio
- For the line chart, Looker Studio works better with a single timestamp field than separate event_date and event_hour.

#### Best small Phase 6 enhancement

Create a model like this:

models/marts/mart_event_volume_by_hour.sql

Enhance it to include:

```sql
{{ config(materialized='table') }}

select
    event_date,
    event_hour,
    timestamp(datetime(event_date, time(event_hour, 0, 0))) as event_hour_ts,
    source_type,
    count(*) as event_count
from {{ ref('int_events_unified') }}
group by 1, 2, 3, 4
order by event_date, event_hour, source_type
```

This gives: `event_hour_ts` for clean plotting in Looker Studio


#### Verify

```bash
dbt % bq query --use_legacy_sql=false \
'select * from `de-zoomcamp-2026-486900.omnistream_gold.mart_event_volume_by_hour`
 order by event_hour_ts desc
 limit 20'

 # Output 

+------------+------------+---------------------+-------------+-------------+
| event_date | event_hour |    event_hour_ts    | source_type | event_count |
+------------+------------+---------------------+-------------+-------------+
| 2026-03-30 |          9 | 2026-03-30 09:00:00 | geo         |           8 |
| 2026-03-30 |          8 | 2026-03-30 08:00:00 | geo         |           3 |
| 2026-03-30 |          1 | 2026-03-30 01:00:00 | geo         |           6 |
| 2026-03-30 |          0 | 2026-03-30 00:00:00 | geo         |           6 |
| 2026-03-30 |          0 | 2026-03-30 00:00:00 | finance     |           4 |
| 2026-03-30 |          0 | 2026-03-30 00:00:00 | aviation    |         560 |
+------------+------------+---------------------+-------------+-------------+
```

## Build the dashboard in Looker Studio

### Data source 1

Connect:

- BigQuery
- project: de-zoomcamp-2026-486900
- dataset: omnistream_gold
- table: mart_event_volume_by_source

### Data source 2

Connect:

- BigQuery
- project: de-zoomcamp-2026-486900
- dataset: omnistream_gold
- table: mart_event_volume_by_hour

## Dashbords

Link - https://lookerstudio.google.com/s/lAdyPoHoQf0

Screenshots

![Dashboards](../08-capstone/images/Dashboards.png)

The dashboard visualizes event volume across geo, aviation, and finance streams. A bar chart shows overall distribution, while a time-series chart highlights temporal trends. An interactive filter allows isolating individual data sources for deeper analysis.