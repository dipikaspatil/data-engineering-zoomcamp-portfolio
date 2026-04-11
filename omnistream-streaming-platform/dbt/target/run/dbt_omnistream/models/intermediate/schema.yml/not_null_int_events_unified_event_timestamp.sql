select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select event_timestamp
from `de-zoomcamp-2026-486900`.`omnistream_gold`.`int_events_unified`
where event_timestamp is null



      
    ) dbt_internal_test