-- Since aviation schemas vary a lot, start with a flexible version. Adjust field names to match table.


with source as (

    select *
    from `de-zoomcamp-2026-486900`.`omnistream_staging`.`raw_aviation_data`

),

renamed as (

    select
        to_hex(md5(
            concat(
                coalesce(cast(icao24 as string), ''),
                '|',
                coalesce(cast(timestamp as string), ''),
                '|',
                coalesce(cast(callsign as string), '')
            )
        )) as event_id,

        timestamp_seconds(timestamp) as event_timestamp,
        date(timestamp_seconds(timestamp)) as event_date,
        extract(hour from timestamp_seconds(timestamp)) as event_hour,

        'aviation' as source_type,
        'flight_position' as event_type,

        cast(icao24 as string) as flight_id,
        cast(callsign as string) as callsign,
        cast(origin_country as string) as origin_country,
        cast(latitude as float64) as latitude,
        cast(longitude as float64) as longitude,
        cast(velocity as float64) as velocity,

        current_timestamp() as dbt_loaded_at

    from source
)

select *
from renamed
where event_id is not null