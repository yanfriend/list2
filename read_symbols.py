import MySQLdb
from yahoo_finance import parse_psr_from_yahoo
import time


def chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]


def get_all_prs():
    # Open database connection
    db = MySQLdb.connect("localhost", "root", "", "finance")

    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    sql = "SELECT * FROM raw_symbols "

    cursor.execute(sql)
    results = cursor.fetchall()

    for row_batch in chunks(results, 10):
        for row in row_batch:
            try:
                symbol = row[0]
                psr = parse_psr_from_yahoo(symbol)
                print('Data: {}: {}'.format(symbol, psr))

            except Exception as e:
                print("Error: ", e, row[0])

        print('sleeping 5 sec')
        time.sleep(5)

    # disconnect from server
    db.close()


if __name__ == "__main__":
    print("Fetching all data for prs from yahoo")
    get_all_prs()
