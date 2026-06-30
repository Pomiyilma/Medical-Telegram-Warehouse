with date_series as (
    -- Dynamically extract every unique date present across our dataset messages
    select distinct 
        cast(message_date as date) as full_date
    from {{ ref('stg_telegram_messages') }}
),

date_breakdown as (
    select
        -- 1. Create a clean surrogate integer date key (e.g., 20260630)
        cast(to_char(full_date, 'YYYYMMDD') as int) as date_key,
        full_date,
        
        -- 2. Breakdown calendar components
        extract(isodow from full_date) as day_of_week,
        to_char(full_date, 'Day') as day_name,
        extract(week from full_date) as week_of_year,
        extract(month from full_date) as month_number,
        to_char(full_date, 'Month') as month_name,
        extract(quarter from full_date) as quarter,
        extract(year from full_date) as year,
        
        -- 3. Flag weekend status
        case 
            when extract(isodow from full_date) in (6, 7) then true 
            else false 
        end as is_weekend
    from date_series
)

select * from date_breakdown
