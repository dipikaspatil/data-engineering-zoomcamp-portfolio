

select
    event_date,
    timestamp_trunc(event_timestamp, minute) as event_minute_ts,
    source_type,
    count(*) as event_count
from `de-zoomcamp-2026-486900`.`omnistream_gold`.`int_events_unified`
group by 1, 2, 3