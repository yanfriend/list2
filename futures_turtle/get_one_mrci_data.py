from collections import defaultdict
from pprint import pprint


class PriceUnit(object):
    def __init__(self, yr_date, open, high, low, close, volume):
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.yr_date = yr_date

    def __str__(self):
        return '%s, %f, %f, %f, %f, %f ' % (self.yr_date, self.open, self.high, self.low, self.close, self.volume)


def parse_one_page_from_mrci(driver, year_date):
    # year_date format is '2019/190910'
    url = 'https://www.mrci.com/ohlc/{}.php'.format(year_date)

    try:
        driver.get(url)
        # time.sleep(10)

        results = driver.find_elements_by_xpath('//table[@class="strat"]//th[@class="note1"]')  # get all futures id
        futures_ids = [relt.text for relt in results]
        # print(futures_ids)

        ret = defaultdict(lambda: defaultdict(dict))

        for i in range(len(futures_ids) - 1):
            xpath = "//tr[preceding-sibling::tr/th='{}' and following-sibling::tr/th='{}']" \
                .format(futures_ids[i], futures_ids[i + 1])  # note: this ignore the last futures symbol
            # print(xpath)

            results = driver.find_elements_by_xpath(xpath)

            content = [relt.text for relt in
                       results]
            # each element is one line: 'Sep19 190910 268.50 268.80 268.40 268.80 +1.15 149,832 308,130 -42,484'
            # print(content)

            for line in content:
                line = line.strip()
                if line.startswith('Total Volume and Open Interest'): continue  # last line, skip
                if len(line.split(' ')) < 10: continue  # not enough data, skip

                expiry, yr_date, open, high, low, \
                close, price_change, volume, open_interest, interest_change = line.split(' ')

                price_unit = PriceUnit(
                    yr_date,
                    float(open.replace(',', '').replace('~', '.')),  # for bond price: 163~100,
                    float(high.replace(',', '').replace('~', '.')),
                    float(low.replace(',', '').replace('~', '.')),
                    float(close.replace(',', '').replace('~', '.')),
                    float(volume.replace(',', ''))
                )
                ret[futures_ids[i]][expiry][yr_date] = price_unit

        pprint({k: {k2: {k3: v3.__str__() for k3, v3 in v2.items()} for k2, v2 in v.items()} for k, v in ret.items()})
        # dict of: future_id => expiry => yr_date => price_unit

        return ret

    except Exception as e:
        raise e
