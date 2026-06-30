with staging_data as (
    select * from {{ ref('stg_telegram_messages') }}
),

fact_assembly as (
    select
        s.message_id,
        
        -- Foreign Key relationships mappings matching our dimension configurations
        md5(s.channel_name) as channel_key,
        cast(to_char(s.message_date, 'YYYYMMDD') as int) as date_key,
        
        -- Text payloads
        s.message_text,
        s.message_length,
        
        -- Quantifiable numeric facts measurements metrics
        s.view_count,
        s.forward_count,
        s.has_image,
        s.image_path
    from staging_data s
)

select * from fact_assembly
