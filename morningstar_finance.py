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


def parse_earning_from_morningstar(driver, ticker):
	url = 'http://financials.morningstar.com/income-statement/is.html?t={}&region=usa&culture=en-US'.format(ticker)

	try:
		driver.get(url)
		driver.execute_script("SRT_stocFund.ChangeFreq(3,'Quarterly')")  # change to Quarterly
		time.sleep(10)
		results = driver.find_elements_by_xpath("//div[@id='data_i84']")

		data = results[0].text.split('\n')
		ret = []
		for d in data:
			if d.startswith('('):
				ret.append(-float(d[1:-1]))
			else:
				ret.append(float(d))

		return ret

	except Exception as e:
		# PSR
		# Data: GLDI: 0
		# ('Error: ', JavascriptException(), 'GLDI') # todo: handle this js exception
		raise e  # todo: add morningstart info
		# print("Failed to get morningstar earning data", e)



if __name__=="__main__":
	argparser = argparse.ArgumentParser()
	argparser.add_argument('ticker',help = '')
	args = argparser.parse_args()
	tickers = args.ticker

	driver = get_driver()
	for ticker in tickers.split(','):
		print ("Fetching data for %s"%(ticker))
		scraped_data = parse_earning_from_morningstar(driver, ticker)
		print(scraped_data)

	driver.quit()
