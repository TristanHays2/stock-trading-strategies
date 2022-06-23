import pandas as pd
import yfinance as yf
import yfinance.shared as shared
from datetime import date, timedelta, datetime
import pickle
import os
import random
import tqdm

#check the database latest date
def database_date():

    rand_file = random.choice(os.listdir(database_path))
    database_current_date_df=pd.read_csv(os.path.join(database_path, rand_file), index_col=0)
    all_date= database_current_date_df.index[-1]
    return(all_date)

#database update check
def database_verify_date():
    today_test=pd.DataFrame()
    today_test=vix_download("1993-01-01", date.today())
    today_test=today_test.index[-1]
    today_test=str(pd.Timestamp.date(today_test))
    todays_download_date=datetime.strptime(today_test,"%Y-%m-%d")

    status=database_date()
    database_status=datetime.strptime(status,"%Y-%m-%d")

    if todays_download_date == database_status:
        print("The database is completly up to date")
    else:
        print("\n", "The database is current to:", database_date(), "\n")
        a= input("Would you like to update the database to be current to today? [y/n] ")
        if a=="y":
            start=database_date()
            start=datetime.strptime(start,"%Y-%m-%d")
            start=(start+timedelta(days=1))
            end=(date.today())
            database_update(start,end)
        elif a=="n":
            pass

def vix_download(start, end):
    
    VIX = pd.DataFrame()
    vix_data = yf.download('^VIX',start=start, end=end, progress=False)
    VIX = pd.concat([VIX, vix_data])
    VIX.drop(['High','Low','Adj Close', 'Volume'],axis=1,inplace=True)
    VIX.rename(columns={'Open' : 'VIX Open', 'Close' : 'VIX Close'}, inplace= True)
    return(VIX)


def database_update(start, end):

    #load ticker list
    pickle_in = open("test_tickers.data", "rb")
    verified_tickers = pickle.load(pickle_in)
    #verified_tickers = ['QQQ', 'SPY', 'SOXX', 'AAPL', 'GOOG', 'TSLA', 'BA', 'QWRTY']

    stock_final = pd.DataFrame()
    VIX=vix_download(start,end)
    error_list=[]

    # iterate over each symbol
    for ticker in tqdm.tqdm(verified_tickers): 

        stock_final = pd.DataFrame(None)
        stock = yf.download(ticker, start=start, end=end, auto_adjust= True, progress= False)

        #tickers that fail download
        errors=list(shared._ERRORS.keys())

        if not errors:
            pass
        else:
            error_list.extend(errors)
            
        stock['Name']=ticker
        
        try: stock_final = pd.concat([stock_final,stock])    
        except:
            pass
        
        #drop unused columns
        if stock_final.empty:
            pass
            
        else:
            stock_final.drop(['High','Low'],axis=1,inplace=True)
            stock_final = stock_final.reset_index(level=0)
            stock_final = pd.merge(stock_final, VIX, on= 'Date')
        
        #save to csv
            output_file = os.path.join(database_path, ticker + '.csv')
            
            try:
                open(output_file)
                stock_final.to_csv(output_file, index=False, mode='a', header=False)

            except:
                stock_final.to_csv(output_file, index=False, mode='a') 

    #remove tickers that fail to download
    if not error_list:
        pass

    else:
        print("\n")
        print(error_list)
        question=input("failed to download. Would you like to delete from the ticker list? [y/n] ")        
        if question =="y":
            verified_tickers=[tickers for tickers in verified_tickers if tickers not in error_list ]
            pickle_out = open("test_tickers.data", "wb")
            pickle.dump(verified_tickers, pickle_out)
            pickle_out.close()
            
        elif question =="n":
            pass

#database location
path= os.getcwd()
print("The current database location is:", path, "\n")
while True:
    question= input("Would you like to change the folder? [y/n] ")
    if question=="y":
        path=input("Enter new folder path:")
        break
    elif question=="n":
        break

#database folder check
database_path=os.path.join(path,"Database")
isFile = os.path.isdir(database_path)
if isFile == False:
        question= input("There is no database folder in this directory. Would you like to create a database? [y/n] ")
        if question=="y":
            database_folder=os.path.join(path,"Database")
            os.makedirs(database_folder)
            end=(date.today()-timedelta(days=1))
            database_update("1993-01-01",end)
        elif question=="n":
            quit()

#database folder empty check
try:
    rand_file = random.choice(os.listdir(database_path))
    file_path = os.path.join(database_path, rand_file)
except:
    question= input("The database folder in this directory is empty. Would you like to download the database? [y/n] ")
    if question=="y":
        end=(date.today()-timedelta(days=1))
        database_update("1993-01-01",end)
    elif question=="n":
        quit()
        
database_verify_date()    
    
print("Have a good day")