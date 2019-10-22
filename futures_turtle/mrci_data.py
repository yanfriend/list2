import argparse

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import os

from selenium.webdriver.firefox.options import Options

def get_driver():
	dirpath = os.getcwd() + '/geckodriver'
        options = Options()
        options.headless = True
	driver = webdriver.Firefox(executable_path=dirpath, options=options)
	return driver


def parse_one_page_from_mrci(driver, year_date='2019/190910'):
	url = 'https://www.mrci.com/ohlc/{}.php'.format(year_date)  # todo, 2019/190910

	try:
		driver.get(url)
		# driver.execute_script("SRT_stocFund.ChangeFreq(3,'Quarterly')")  # change to Quarterly
		# time.sleep(10)

		results = driver.find_elements_by_xpath('//table[@class="strat"]//th[@class="note1"]')  # get all futures id
		futures_ids = [ret.text for ret in results]
		print(futures_ids)

		for i in range(len(futures_ids)-1):
			xpath ="//tr[preceding-sibling::tr/th='{}' and following-sibling::tr/th='{}']" \
				.format(futures_ids[i], futures_ids[i+1]) # note: this ignore the last futures symbol
			print(xpath)

			results = driver.find_elements_by_xpath(xpath)

			content = [ret.text for ret in results]
			print(content)

		#
		# import ipdb; ipdb.set_trace()
		#
		# data = results[0].text.split('\n')
		# ret = []
		# for d in data:
		# 	if d.startswith('('):
		# 		ret.append(-float(d[1:-1]))
		# 	else:
		# 		ret.append(float(d))
		#
		# return ret

	except Exception as e:
		# PSR
		# Data: GLDI: 0
		# ('Error: ', JavascriptException(), 'GLDI') # todo: handle this js exception
		raise e  # todo: add morningstart info
		# print("Failed to get morningstar earning data", e)



if __name__=="__main__":
	argparser = argparse.ArgumentParser()
	argparser.add_argument('dates',help = '2019/190910')
	args = argparser.parse_args()
	dates = args.dates

	driver = get_driver()
	for one_date in dates.split(','):
		print ("Fetching data for %s"%(one_date))
		scraped_data = parse_one_page_from_mrci(driver, one_date)
		print(scraped_data)

	driver.quit()
