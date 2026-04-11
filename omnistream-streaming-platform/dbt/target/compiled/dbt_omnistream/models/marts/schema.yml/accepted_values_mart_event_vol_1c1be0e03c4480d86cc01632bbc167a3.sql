
    
    

with all_values as (

    select
        source_type as value_field,
        count(*) as n_records

    from `de-zoomcamp-2026-486900`.`omnistream_gold`.`mart_event_volume_by_source`
    group by source_type

)

select *
from all_values
where value_field not in (
    'geo','aviation','finance'
)


