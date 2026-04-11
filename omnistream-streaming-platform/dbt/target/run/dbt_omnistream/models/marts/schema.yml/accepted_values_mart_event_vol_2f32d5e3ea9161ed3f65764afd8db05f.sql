select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    

with all_values as (

    select
        source_type as value_field,
        count(*) as n_records

    from `de-zoomcamp-2026-486900`.`omnistream_gold`.`mart_event_volume_by_minute`
    group by source_type

)

select *
from all_values
where value_field not in (
    'geo','aviation','finance'
)



      
    ) dbt_internal_test