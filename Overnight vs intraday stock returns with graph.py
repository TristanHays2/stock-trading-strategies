import pandas as pd
import yfinance as yf
import datetime
import numpy as np
import matplotlib.pyplot as plt

start = datetime.datetime(2000,1,1)
end = datetime.datetime(2018,1,1)

#['SPY', 'SPXL', 'QQQ', 'TQQQ', 'SOXX', 'SOXL', 'GDX']
Symbol= ['SPY']

# create empty dataframe
stock_final = pd.DataFrame()
VIX = pd.DataFrame()

# download the stock price 
stock = yf.download(Symbol,start=start, end=end, progress=False)

# append the individual stock prices 
for i in Symbol:
	stock['Name']= i
stock_final = stock_final.append(stock,sort=False)

#drop unused columns
stock_final.drop(['High','Low','Adj Close', 'Volume'],axis=1,inplace=True)
		
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

# calc long return
long=((stock_final['Close'].iloc[-1])-stock_final['Close'].iloc[0])/(stock_final['Close'].iloc[0])*100
	
#renumber index
stock_final = stock_final.reset_index(level=0)
	
# calc return time
duration= (stock_final.iloc[-1,0])-stock_final.iloc[0,0]
duration=duration/np.timedelta64(1,'Y')

#calculate overnight return column by using ((Open-Prev.Close)/Prev.Close)*100
stock_final['Overnight Return %'] = ((stock_final['Open'].shift(-1) - stock_final['Close'])/stock_final['Close'])
	
# calculate intraday return % column
stock_final['Intraday Return %'] = ((stock_final['Close'] - stock_final['Open'])/stock_final['Open'])

vix_filter= pd.DataFrame()

	#iterate VIX level
for v in range(10,70):
		
	#reset dataframes
	stock_final_vix = pd.DataFrame(None)
		
	#VIX level filter above
	stock_final_vix = stock_final[(stock_final['VIX Open'] < v ) | (stock_final['VIX Close'] < v)]
	
	#calculate compounding overnight returns
	stock_final_vix['Overnight Total Return'] = (stock_final_vix['Overnight Return %']+1).cumprod()	
	
	#calculate compounding intraday returns
	stock_final_vix['Intraday Total Return'] = (stock_final_vix['Intraday Return %']+1).cumprod()
	
	#calc overnight total return
	try:
		overnight_total = (stock_final_vix['Overnight Total Return'].iloc[-2]*100)	
	except IndexError:
		print('No data')

	#calc intraday total return
	try:
		intraday_total = (stock_final_vix['Intraday Total Return'].iloc[-2]*100)
	except IndexError:
		print('')
		
	try:
		cutoff_data = {'Stock': i, 'Vix Cutoff': v, 'Overnight return' :round(overnight_total, 2), 'Intraday return': round(intraday_total, 2), 'Buy and hold' : long}
	except:
		 cutoff_data= {'Stock': i, 'Vix Cutoff': v, 'Overnight return': 'No data', 'Intraday return': 'No data', 'Buy and hold' : long}
		
	vix_filter=vix_filter.append(cutoff_data, ignore_index= True)

vix_filter.plot(x='Vix Cutoff',)
plt.show()
	
