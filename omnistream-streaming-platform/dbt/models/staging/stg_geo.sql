-- This is a staging model for the 'geo' source data.
-- Purpose:
    -- clean raw geo records
    -- standardize names
    -- normalize timestamp
    -- keep only useful columns
{{ config(materialized='view') }}

with source as (

    select *
    from {{ source('omnistream_staging', 'raw_geo_data') }}

),

renamed as (

    select
        cast(id as string) as event_id,

        timestamp_seconds(timestamp) as event_timestamp,
        date(timestamp_seconds(timestamp)) as event_date,
        extract(hour from timestamp_seconds(timestamp)) as event_hour,

        'geo' as source_type,
        'earthquake' as event_type,

        cast(place as string) as place,
        cast(mag as float64) as magnitude,
        cast(depth as float64) as depth,
        cast(lat as float64) as latitude,
        cast(lon as float64) as longitude,

        current_timestamp() as dbt_loaded_at

    from source
)

select *
from renamed
where event_id is not null