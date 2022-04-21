import yfinance as yf
import pandas as pd
import datetime
import requests
import io
import pickle

url="https://pkgstore.datahub.io/core/nasdaq-listings/nasdaq-listed_csv/data/7665719fb51081ba0bd834fde71ce822/nasdaq-listed_csv.csv"

s = requests.get(url).content
companies = pd.read_csv(io.StringIO(s.decode('utf-8')))

Symbols = companies['Symbol'].tolist()

#enter date
start_date_entry = input('Enter a start date in YYYY-MM-DD format: ')
year, month, day=map(int, start_date_entry.split('-'))
start = datetime.date(year, month, day)

end_date_entry = input('Enter an end date in YYYY-MM-DD format: ')
year, month, day=map(int, end_date_entry.split('-'))
end = datetime.date(year, month, day)

# create empty dataframe and list
stock_final = pd.DataFrame()
valid_tickers=pd.DataFrame()
ticker_list=[]

# iterate over each symbol
for i in Symbols: 

	#reset dataframes
	stock_final = pd.DataFrame(None)
	VIX = pd.DataFrame(None)

	# download the stock price 
	stock = yf.download(i, start=start, end=end, progress=False)
		
	# append the individual stock prices 
	stock['Name']=i
	stock_final = stock_final.append(stock,sort=False)
	
	try:
		#valid_tickers=stock_final.append(stock_final.iloc[0,6], sort=False)
		ticker_list.append(stock_final.iloc[0,6])
		
	except:
		pass
		
#save ticker data to file
pickle_out = open("verified_tickers.data", "wb")
pickle.dump(ticker_list, pickle_out)
pickle_out.close()