{{ config(
    materialized='table',
    cluster_by = ["source_type"]
) }}

select
    source_type,
    count(*) as event_count
from {{ ref('int_events_unified') }}
group by 1