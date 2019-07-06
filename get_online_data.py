import MySQLdb
from yahoo_finance import parse_psr_from_yahoo
import morningstar_finance
import time
from datetime import datetime
import json


def chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]


def get_all_data():
    db = MySQLdb.connect("localhost", "root", "", "finance")
    cursor = db.cursor()

    table_name = 'list2_symbols'
    sql = "SELECT * FROM {table_name} limit 3460, 5000 ".format(table_name=table_name)  # todo, remove offset

    cursor.execute(sql)
    results = cursor.fetchall()

    driver = morningstar_finance.get_driver()

    yahoo_success = morningstar_success = failure = 0
    cnt = 0

    for row_batch in chunks(results, 10):
        for row in row_batch:
            try:
                cnt += 1
                symbol = row[0]
                psr = parse_psr_from_yahoo(symbol)
                yahoo_success += 1
                print('PSR Data: {}: {}'.format(symbol, psr))

                earning5 = morningstar_finance.parse_earning_from_morningstar(driver, symbol) # sleep 10 seconds inside
                morningstar_success += 1
                print('Five Earning:{}'.format(earning5))

                now = datetime.now()
                updated_at = now.strftime('%Y-%m-%d %H:%M:%S')

                update_sql = 'update {table_name} ' \
                             'set psr = {psr},' \
                             ' earning_1 = {earning_1},' \
                             ' earning_2 = {earning_2},'\
                             ' earning_3 = {earning_3},' \
                             ' earning_4 = {earning_4},' \
                             ' earning_5 = {earning_5},' \
                             ' updated_at = "{updated_at}" ' \
                             ' where symbol="{symbol}"'.format(
                    table_name = table_name,
                    psr = psr,
                    earning_1 = earning5[0],
                    earning_2=earning5[1],
                    earning_3=earning5[2],
                    earning_4=earning5[3],
                    earning_5=earning5[4],
                    symbol = symbol,
                    updated_at = updated_at
                )
                # print(update_sql)
                cursor.execute(update_sql)

            except Exception as e:
                print("Error: ", e, row[0])
                failure += 1
                
                try:
                    exception = json.dumps(e.message)
                except Exception as e1:
                    exception = '"{}"'.format(str(e))
                exception = exception if exception!='""' else '"{}"'.format(str(e))
                update_sql = 'update {table_name} ' \
                             'set exception = {exception}' \
                             ' where symbol="{symbol}"'.format(
                    table_name = table_name,
                    exception = exception,
                    symbol = row[0])
                print(update_sql)
                cursor.execute(update_sql)

            if cnt % 25 == 0:
                driver.quit()
                print('Restarting Firefox driver')
                time.sleep(10)
                driver = morningstar_finance.get_driver()  # reset driver

            print('')
        # print('Committing to db')
        db.commit() # for each 10 records.

    driver.quit()

    # disconnect from server
    db.close()
    print('yahoo success:{yahoo_success}, morningstar success:{morningstar_success}. total failure:{failure}'
          .format(yahoo_success=yahoo_success, morningstar_success=morningstar_success, failure=failure))


if __name__ == "__main__":
    print("Fetching all data for prs from yahoo, earnings from morningstar")
    get_all_data()
