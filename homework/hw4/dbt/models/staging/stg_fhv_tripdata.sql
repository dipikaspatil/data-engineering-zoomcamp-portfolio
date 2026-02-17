WITH source AS (

    SELECT *
    FROM {{ source('raw', 'fhv_tripdata') }}
    WHERE dispatching_base_num IS NOT NULL

),

renamed AS (

    SELECT
        dispatching_base_num                    AS dispatching_base_num,
        affiliated_base_number                  AS affiliated_base_number,

        {{ safe_cast('pickup_datetime', 'timestamp') }}   AS pickup_datetime,
        {{ safe_cast('dropOff_datetime', 'timestamp') }}  AS dropoff_datetime,

        CAST(PUlocationID AS INT64)              AS pickup_location_id,
        CAST(DOlocationID AS INT64)              AS dropoff_location_id,

        CAST(SR_Flag AS INT64)                   AS sr_flag

    FROM source
    WHERE {{ safe_cast('pickup_datetime', 'timestamp') }} >= TIMESTAMP('2019-01-01')
      AND {{ safe_cast('pickup_datetime', 'timestamp') }} <  TIMESTAMP('2020-01-01')

)

SELECT *
FROM renamed
