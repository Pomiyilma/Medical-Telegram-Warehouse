with source as (
    -- This special source function tells dbt to look at the table we registered in src_telegram.yml
    select * from {{ source('raw_source', 'telegram_messages') }}
),

renamed_and_cleaned as (
    select
        -- 1. Explicitly clean and cast primary key identifiers
        id as unique_row_id,
        message_id,
        channel_name,

        -- 2. Cast the timestamp correctly
        cast(message_date as timestamptz) as message_date,

        -- 3. Grab the text payload
        message_text,

        -- 4. Calculate helpful new analytics fields on the fly
        coalesce(views, 0) as view_count,
        coalesce(forwards, 0) as forward_count,
        
        -- If has_media boolean is true, set a strong flag string or boolean
        case 
            when has_media = true then true 
            else false 
        end as has_image,

        image_path,

        -- Calculate the exact character string length of the message body
        length(coalesce(message_text, '')) as message_length

    from source
    where 
        -- Business Logic Filter: Strip out completely blank or empty utility messages
        message_text is not null 
        and message_text != ''
)

select * from renamed_and_cleaned
