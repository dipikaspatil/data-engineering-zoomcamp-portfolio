

with source as (

    select *
    from `de-zoomcamp-2026-486900`.`omnistream_staging`.`raw_finance_data`

),

renamed as (

    select
        to_hex(md5(
            concat(
                coalesce(cast(symbol as string), ''),
                '|',
                coalesce(cast(timestamp as string), ''),
                '|',
                coalesce(cast(price as string), '')
            )
        )) as event_id,

        timestamp_seconds(timestamp) as event_timestamp,
        date(timestamp_seconds(timestamp)) as event_date,
        extract(hour from timestamp_seconds(timestamp)) as event_hour,

        'finance' as source_type,
        'price_update' as event_type,

        cast(symbol as string) as symbol,
        cast(price as float64) as price,
        cast(volume as int64) as volume,
        cast(change_percent as string) as change_percent,

        current_timestamp() as dbt_loaded_at

    from source
)

select *
from renamed
where event_id is not null