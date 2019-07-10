import csv

response_events = []
with open('event_id_6-21.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    line_count = 0
    for row in csv_reader:
        response_events.append("'{}'".format(row['event_id']))
        line_count += 1
    print(f'Processed {line_count} lines.')

print(response_events[0])
print('finished!')



#############################



import airpy
import pandas as pd
import matplotlib.pyplot as plt
import time

# todo: output to a file.
# bvi_writer = csv.writer(bvi_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

chunk_size = 1000
batch_size = len(response_events) // chunk_size + 1

for i in range(batch_size):
    finished = False

    while not finished:
        try:
            piece = response_events[i * chunk_size:(i + 1) * chunk_size]
            piece_str = ','.join(piece)

            #     events_str = ','.join(response_events)

            query_str = """
            select DISTINCT attempted_bill_version_item_token from payments.panama_production_bill_tenders
            where token in (
            select bill_tender_token from payments.panama_production_tender_events
            where gateway_transaction_token in (
            select token from payments.panama_production_gateway_transactions
            where external_reference_token in (
            select transaction_token
            from payments.rich_payment_events_v12
            where event_id in ({events_str}) and ds>='2019-06-20'
            )))
            """.format(events_str=piece_str)

            print(query_str)

            ret = airpy.presto(query_str, use_cache=False)

            bvi_file = open('bvi_token_6-21.csv', mode='a')

            # display(ret)
            bvis = ret['attempted_bill_version_item_token'].tolist()

            for bvi in bvis:
                bvi_file.write(bvi + '\n')

            bvi_file.close()
            finished = True
        except Exception as e:
            print('sleeping 60 seconds')
            time.sleep(60)

'''
-- sql reference
-- find bvi token from event ids
with events_ids as (
values
'0Ga00JdXtxkBvas8fuSjcbVzfGU',
'0Ga00UbAOxQyHYEMpIevh30SyYQ',
'0Ga3SEiW1kU1SqTNZFR3raOfEHD',
'0Ga00NjZe21EJa9tXgSzDFFIiCQ',
'0Ga2uKHj19PCM4T1ZqtS92DIeuC',
'sample_event_ids'
)

select DISTINCT attempted_bill_version_item_token from payments.panama_production_bill_tenders
where token in (
select bill_tender_token from payments.panama_production_tender_events
where gateway_transaction_token in (
select token from payments.panama_production_gateway_transactions
where external_reference_token in (
select transaction_token
from payments.rich_payment_events_v12
where event_id in (select * from events_ids) and ds>'2019-01-01'
)))

'''
