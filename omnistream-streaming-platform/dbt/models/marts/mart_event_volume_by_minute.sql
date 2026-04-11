{{ config(
    materialized='table',
    partition_by={
      "field": "event_date",
      "data_type": "date",
      "granularity": "day"
    },
    cluster_by=["source_type"]
) }}

select
    event_date,
    timestamp_trunc(event_timestamp, minute) as event_minute_ts,
    source_type,
    count(*) as event_count
from {{ ref('int_events_unified') }}
group by 1, 2, 3