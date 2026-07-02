with source as (
    select * from {{ source('raw_source', 'yolo_detections') }}
)
select
    cast(message_id as int) as message_id,
    trim(channel_name) as channel_name,
    trim(detected_class) as detected_class,
    cast(confidence_score as numeric) as confidence_score,
    trim(image_category) as image_category,
    trim(image_path) as image_path
from source
