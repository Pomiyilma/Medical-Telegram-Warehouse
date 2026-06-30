-- This query returns any records where the post date is set in the future compared to the current system timestamp.
-- To PASS, this query must return 0 rows.
select
    message_id,
    message_date
from {{ ref('stg_telegram_messages') }}
where message_date > now()
