with trips as (
    select
        *,
        EXTRACT(YEAR FROM pickup_datetime) as year,
        EXTRACT(MONTH FROM pickup_datetime) as month
    from {{ ref('int_trips_unioned') }}
),

monthly_revenue as (
    select
        year,
        month,
        pickup_location_id,
        sum(total_amount) as revenue_monthly_total_amount,
        count(*) as total_monthly_trips
    from trips
    group by 1,2,3
)

select *
from monthly_revenue
