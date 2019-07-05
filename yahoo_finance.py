import argparse

import requests
from bs4 import BeautifulSoup


def parse_psr_from_yahoo(ticker):
	url = "http://finance.yahoo.com/quote/{}/key-statistics?p={}&.tsrc=fin-srch".format(ticker,ticker)

	try:
		web_data = requests.get(url)
		beautify_data = BeautifulSoup(web_data.content, "html.parser")

		rows = beautify_data.find_all('tr')
		for row in rows:
			cols = row.find_all('td')
			if len(cols) < 2: continue
			if cols[0].text.startswith('Price/Sales'):
				return float(cols[1].text)
		return 0
	except Exception as e:
		raise e  # todo: add yahoo info
		# print("Failed to get yahoo psr data", e)


if __name__=="__main__":
	argparser = argparse.ArgumentParser()
	argparser.add_argument('ticker',help = '')
	args = argparser.parse_args()
	ticker = args.ticker

	print ("Fetching data for %s"%(ticker))
	scraped_data = parse_psr_from_yahoo(ticker)
	print(scraped_data)

	# print ("Writing data to output file")
	# with open('%s-summary.json'%(ticker),'w') as fp:
	# 	json.dump(scraped_data,fp,indent = 4)
