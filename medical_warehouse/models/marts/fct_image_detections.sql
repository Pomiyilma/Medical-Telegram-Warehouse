with yolo_stg as (
    select * from {{ ref('stg_yolo_detections') }}
),

messages_fct as (
    select message_id, channel_key, date_key from {{ ref('fct_messages') }}
)

select
    y.message_id,
    m.channel_key,
    m.date_key,
    y.detected_class,
    y.confidence_score,
    y.image_category,
    y.image_path
from yolo_stg y
-- Perform an inner join on message_id to ensure every detection is perfectly aligned with a real message record
inner join messages_fct m on y.message_id = m.message_id
