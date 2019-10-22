import os
from collections import defaultdict
import datetime
from pprint import pprint

from get_one_mrci_data import parse_one_page_from_mrci
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def get_driver():
    dirpath = os.getcwd() + '/geckodriver'
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(executable_path=dirpath, options=options)
    return driver


def get_formatted_dates():
    # get current day, and return a list of previous 35 days in the specific format 2019/190910

    LOOKBACK_PERIOD = 35
    now = datetime.datetime.now()
    current_yr = now.year  # maybe use when acrossing year
    today = datetime.datetime.today()

    ret = []
    for i in range(LOOKBACK_PERIOD):
        dt = today - datetime.timedelta(days=i)
        one_date = dt.strftime('%Y/%y%m%d')
        ret.append(one_date)

    return ret


def traverse_and_alert(final_ret):
    # pass the final_ret, to get last close value vs previous 19 day highest/lowest close
    print('Begin alerting')
    alert_messages = []
    for futures_id in final_ret.keys():
        selected_expiry = ''
        largest_vol = 0

        # for each expiry, find the latest date's volume. Select the largest volume's expiry
        for expiry, date_price_unit in final_ret[futures_id].items():
            price_unit = date_price_unit[max(date_price_unit.keys())]  # get largest volume
            if price_unit.volume > largest_vol:
                largest_vol = price_unit.volume
                selected_expiry = expiry

        # now for each futures_ids, we have expiry we should use, and query to get prices of date series.
        print('For futures {futures_id}, {expiry}, the largest current day volume is {volume}'
              .format(futures_id=futures_id,
                      expiry=selected_expiry,
                      volume=largest_vol))

        # get series of data for the futures_id, expiry, all dates of unit price.
        price_series = []
        for yr_date, price_unit in sorted(final_ret[futures_id][selected_expiry].items(), reverse=True):
            price_series.append(price_unit)

        alert_messages.extend(alert_to_messages(price_series, futures_id, selected_expiry))

    # write to a file
    now_date = datetime.datetime.today()
    file_name = now_date.strftime('alert_%Y%m%d.txt')
    with open(file_name, 'a') as writer:
        writer.write('ALERTS for {} **********************\n'.format(now_date.strftime('%Y/%m/%d')))
        writer.write('\n'.join(alert_messages))

    print('Finish alerting')


def alert_to_messages(price_series, futures_id, selected_expiry):
    # the last step, check current close price, with previous 19th high/low
    if not price_series: return []

    return_msg = []
    price_series = price_series[:20]  # most recent 20 days
    last_min_price = min([unit.close for unit in price_series])
    last_max_price = max([unit.close for unit in price_series])

    # consider put output in a file.
    if price_series[0].close >= last_max_price:
        return_msg.append(('{futures_id}, {expiry}, today close price is higher than 20 days high:{close}'
              .format(futures_id=futures_id,
                      expiry=selected_expiry,
                      close=price_series[0].close)))
    if price_series[0].close <= last_min_price:
        return_msg.append(('{futures_id}, {expiry}, today close price is lower than 20 days low:{close}'
              .format(futures_id=futures_id,
                      expiry=selected_expiry,
                      close=price_series[0].close)))
    return return_msg


if __name__ == "__main__":
    driver = get_driver()

    final_ret = defaultdict(lambda: defaultdict(dict))
    dates = get_formatted_dates()
    parsed_dates = 0

    HIGH_LOW_LOOKBACK = 20
    for one_date in dates:
        if parsed_dates > HIGH_LOW_LOOKBACK: break  # only parse 20 days data

        print("Fetching data for %s" % (one_date))

        scraped_data = parse_one_page_from_mrci(driver, one_date)
        if len(scraped_data) == 0: continue
        parsed_dates += 1

        for futures_id, v in scraped_data.items():
            for expiry, price_unit in v.items():
                final_ret[futures_id][expiry].update(price_unit)

    pprint({k: {k2: {k3: v3.__str__() for k3, v3 in v2.items()} for k2, v2 in v.items()} for k, v in final_ret.items()})

    driver.quit()

    traverse_and_alert(final_ret)
