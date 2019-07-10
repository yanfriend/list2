
with user_batch as (
SELECT cast( row(user_id, line_item_batch) as row(col1 integer, col2 integer)) as row0,
sum(case when event_type = 'PAYOUT_RESPONSE' then 1 else 0 end) AS response_count,
sum(case when event_type = 'PAYOUT_SETTLEMENT' then 1 else 0 end) AS settlement_count
from payments.rich_payment_events_v12
WHERE ds>='2019-06-21' and ds<='2019-07-03'
and user_id is not null and line_item_batch is not null
group by user_id, line_item_batch
having sum(case when event_type = 'PAYOUT_RESPONSE' then 1 else 0 end)>0
and sum(case when event_type = 'PAYOUT_SETTLEMENT' then 1 else 0 end)=0
)

select event_id
 from payments.rich_payment_events_v12 rpe
    join (select row0.col1 as col1, row0.col2 as col2 from user_batch) ub
    on rpe.user_id = ub.col1 and rpe.line_item_batch = ub.col2
 WHERE ds>='2019-06-21' and ds<='2019-06-28'
 -- and user_id = user_batch.user_id
 -- and line_item_batch = user_batch.line_item_batch
 and event_type = 'PAYOUT_RESPONSE'
 and status = 'SUCCEEDED'


-- note: use case row to access the fields in the row.

