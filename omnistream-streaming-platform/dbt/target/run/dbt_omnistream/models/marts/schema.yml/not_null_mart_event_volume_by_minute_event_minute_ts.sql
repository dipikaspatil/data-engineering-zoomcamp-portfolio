select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select event_minute_ts
from `de-zoomcamp-2026-486900`.`omnistream_gold`.`mart_event_volume_by_minute`
where event_minute_ts is null



      
    ) dbt_internal_test