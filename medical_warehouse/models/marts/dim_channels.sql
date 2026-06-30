with channel_metrics as (
    select
        channel_name,
        -- Calculate structural performance aggregates per channel channel metrics
        min(message_date) as first_post_date,
        max(message_date) as last_post_date,
        count(unique_row_id) as total_posts,
        round(avg(view_count), 2) as avg_views
    from {{ ref('stg_telegram_messages') }}
    group by channel_name
),

channel_enrichment as (
    select
        -- Generate a safe string MD5 hash based surrogate key for the channel identifier
        md5(channel_name) as channel_key,
        channel_name,
        
        -- Business classification logic rule engine mapping
        case 
            when lower(channel_name) like '%pharma%' or lower(channel_name) like '%med%' then 'Pharmaceutical/Medical'
            when lower(channel_name) like '%cosmetic%' or lower(channel_name) like '%beauty%' then 'Cosmetics'
            else 'Medical Business'
        end as channel_type,
        
        first_post_date,
        last_post_date,
        total_posts,
        avg_views
    from channel_metrics
)

select * from channel_enrichment
