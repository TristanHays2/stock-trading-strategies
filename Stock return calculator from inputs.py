import pandas as pd
import yfinance as yf
import datetime
import numpy as np

#Ticker symbol input list
Symbols= input('Enter ticker symbols: ').split()

#enter date
start_date_entry = input('Enter a start date in YYYY-MM-DD format: ')
year, month, day=map(int, start_date_entry.split('-'))
start = datetime.date(year, month, day)

end_date_entry = input('Enter an end date in YYYY-MM-DD format: ')
year, month, day=map(int, end_date_entry.split('-'))
end = datetime.date(year, month, day)

#VIX level
v = float(input('Enter VIX upper level cutoff: '))

# create empty dataframe
stock_final = pd.DataFrame()
VIX = pd.DataFrame()

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
	
	#drop unused columns
	stock_final.drop(['High','Low','Adj Close', 'Volume'],axis=1,inplace=True)
	
	#renumber index
	stock_final = stock_final.reset_index(level=0)
	
	# calc return time
	duration= (stock_final.iloc[-1,0])-stock_final.iloc[0,0]
	duration=duration/np.timedelta64(1,'Y')
	
	# calc long return
	long=((stock_final['Close'].iloc[-1])-stock_final['Close'].iloc[0])/(stock_final['Close'].iloc[0])*100
		
	# download VIX
	vix_data = yf.download('^VIX',start=start, end=end, progress=False)
	
	# add data to db
	VIX = VIX.append(vix_data,sort=False)
	
	#drop columns
	VIX.drop(['High','Low','Adj Close', 'Volume'],axis=1,inplace=True)
	
	#rename headers
	VIX.rename(columns={'Open' : 'VIX Open', 'Close' : 'VIX Close'}, inplace= True)
	
	# merge with vix
	stock_final = pd.merge(stock_final, VIX, on= 'Date')

	#calculate overnight return column by using ((Open-Prev.Close)/Prev.Close)*100
	stock_final['Overnight Return %'] = ((stock_final['Open'].shift(-1) - stock_final['Close'])/stock_final['Close'])
	
	# calculate intraday return % column
	stock_final['Intraday Return %'] = ((stock_final['Close'] - stock_final['Open'])/stock_final['Open'])
	
	#VIX level filter above
	stock_final = stock_final[(stock_final['VIX Open'] < v ) | (stock_final['VIX Close'] < v)]
	
	#calculate compounding overnight returns
	stock_final['Overnight Total Return'] = (stock_final['Overnight Return %']+1).cumprod()
	stock_final['Overnight Total Return'].iat[0] = 1	
	
	#calculate compounding intraday returns
	stock_final['Intraday Total Return'] = (stock_final['Intraday Return %']+1).cumprod()
	
	#calc overnight total return
	overnight_total = (stock_final['Overnight Total Return'].iloc[-2]*100)

	#calc intraday total return
	intraday_total = (stock_final['Intraday Total Return'].iloc[-2]*100)
	
	print (i, "=", round(overnight_total, 2), '% overnight \n vs', round(intraday_total, 2), '% intraday \n',round(long, 2), '% buy and hold over', round(duration, 1), 'years \n')
