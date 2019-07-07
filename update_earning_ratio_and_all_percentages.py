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


def update_earning_growth_ratios():
    db = MySQLdb.connect("localhost", "root", "", "finance")
    cursor = db.cursor()

    table_name = 'list2_symbols'
    sql = "SELECT symbol, earning_1, earning_2, earning_3, earning_4, earning_5 FROM {table_name}"\
        .format(table_name=table_name)

    cursor.execute(sql)
    results = cursor.fetchall()

    success = 0
    for row_batch in chunks(results, 100):
        for row in row_batch:
            symbol = row[0]
            earning1 = row[1]; earning2 = row[2]; earning3 = row[3]; earning4 = row[4]; earning5 = row[5]

            if earning1 is None or earning2 is None \
                    or earning3 is None or earning4 is None or earning5 is None:
                continue  # one is null -> not process

            if (earning1 < 0 and earning2 < 0 and earning3 < 0 and earning4 < 0) or \
                    (earning2 < 0 and earning3 < 0 and earning4 < 0 and earning5 < 0):
                continue

            maxe = max(earning1, earning2, earning3, earning4, earning5)
            mine = min(earning1, earning2, earning3, earning4, earning5)
            dist = maxe - mine
            if dist < 0.0000001:
                earning_growth = 0
            else:
                recent4 = float(earning2 + earning3 + earning4 + earning5 - 4 * mine) / dist
                old4 = float(earning1 + earning2 + earning3 + earning4 - 4 * mine) / dist
                earning_growth = recent4 - old4

            update_sql = 'update {table_name} ' \
                         ' set earning_growth = {earning_growth}' \
                         ' where symbol="{symbol}"'.format(
                table_name=table_name,
                earning_growth=earning_growth,
                symbol=symbol,
            )
            print(update_sql)
            cursor.execute(update_sql)
            success += 1
            print('')

        db.commit()  # for each 10 records.

    db.close()
    print('updated earning gorwth:{success}.'.format(success=success))


def update_percentage(compared_col, updated_col):
    db = MySQLdb.connect("localhost", "root", "", "finance")
    cursor = db.cursor()
    table_name = 'list2_symbols'

    sql = "SELECT symbol,{compared_col} FROM {table_name} order by {compared_col} desc"\
        .format(table_name=table_name, compared_col=compared_col)
    cursor.execute(sql)

    results = cursor.fetchall();
    cnt = len(results)
    batch_size = cnt/100

    percentage = 100
    for row_batch in chunks(results, batch_size):
        for row in row_batch:
            symbol = row[0]
            update_sql = 'update {table_name} ' \
                         ' set {updated_col} = {percentage}' \
                         ' where symbol="{symbol}"'.format(
                table_name=table_name,
                updated_col=updated_col,
                percentage=percentage,
                symbol=symbol
            )
            # print(update_sql)
            cursor.execute(update_sql)
        percentage -= 1
        db.commit()  # for each batch_size records.

    db.close()


if __name__ == "__main__":
    print("Updating earning growth ratios and all percentages")
    update_earning_growth_ratios()
    update_percentage('price_ratio', 'price_percentage')
    update_percentage('psr', 'psr_percentage')
    update_percentage('earning_growth', 'earning_growth_percentage')
