-- This is the key model. It gives you one common analytics layer across all three streams.


with geo as (

    select
        event_id,
        event_timestamp,
        event_date,
        event_hour,
        source_type,
        event_type,

        place as entity_name,
        place as location_name,

        cast(null as string) as flight_id,
        cast(null as string) as callsign,
        cast(null as string) as origin_country,
        cast(null as float64) as velocity,

        cast(null as string) as symbol,
        cast(null as float64) as price,
        cast(null as int64) as volume,
        cast(null as string) as change_percent,

        magnitude,
        depth,
        latitude,
        longitude,

        dbt_loaded_at

    from `de-zoomcamp-2026-486900`.`omnistream_gold`.`stg_geo`

),

aviation as (

    select
        event_id,
        event_timestamp,
        event_date,
        event_hour,
        source_type,
        event_type,

        callsign as entity_name,
        origin_country as location_name,

        flight_id,
        callsign,
        origin_country,
        velocity,

        cast(null as string) as symbol,
        cast(null as float64) as price,
        cast(null as int64) as volume,
        cast(null as string) as change_percent,

        cast(null as float64) as magnitude,
        cast(null as float64) as depth,
        latitude,
        longitude,

        dbt_loaded_at

    from `de-zoomcamp-2026-486900`.`omnistream_gold`.`stg_aviation`

),

finance as (

    select
        event_id,
        event_timestamp,
        event_date,
        event_hour,
        source_type,
        event_type,

        symbol as entity_name,
        cast(null as string) as location_name,

        cast(null as string) as flight_id,
        cast(null as string) as callsign,
        cast(null as string) as origin_country,
        cast(null as float64) as velocity,

        symbol,
        price,
        volume,
        change_percent,

        cast(null as float64) as magnitude,
        cast(null as float64) as depth,
        cast(null as float64) as latitude,
        cast(null as float64) as longitude,

        dbt_loaded_at

    from `de-zoomcamp-2026-486900`.`omnistream_gold`.`stg_finance`

)

select * from geo
union all
select * from aviation
union all
select * from finance