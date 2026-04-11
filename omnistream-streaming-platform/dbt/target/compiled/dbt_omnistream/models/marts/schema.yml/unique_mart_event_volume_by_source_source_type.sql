
    
    

with dbt_test__target as (

  select source_type as unique_field
  from `de-zoomcamp-2026-486900`.`omnistream_gold`.`mart_event_volume_by_source`
  where source_type is not null

)

select
    unique_field,
    count(*) as n_records

from dbt_test__target
group by unique_field
having count(*) > 1


