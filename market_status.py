# Code to chack market conditions based on ZeroDTE-SPX Trades
# By Derek Jones

# Install these packages if needed:
# pip install pandas-datareader
# pip install pandas
# pip install yfinance
# pip install pandas-ta
# pip install pytz holidays


# Import Pandas and Pandas TA for data analysis.
#import numpy as np
import pandas as pd
import pandas_ta as ta
from datetime import datetime

#PDR package to pull data
from pandas_datareader import data

# pandas_datareader isn't reading Yahoo correctly. Use yFinance to pull Data
import yfinance as yf
#from datetime import datetime, timedelta
import datetime, pytz, holidays

# Need to know if the market is open because yfinance will pull intrasdays
tz = pytz.timezone('US/Eastern')
us_holidays = holidays.US()
def afterHours(now = None):
        if not now:
            now = datetime.datetime.now(tz)
            openTime = datetime.time(hour = 9, minute = 30, second = 0)
            closeTime = datetime.time(hour = 16, minute = 0, second = 0)
        # If a holiday
        if now.strftime('%Y-%m-%d') in us_holidays:
            return True
        # If before 0930 or after 1600
        if (now.time() < openTime) or (now.time() > closeTime):
            return True
        # If it's a weekend
        if now.date().weekday() > 4:
            return True

        return False

# define start and end dates. Start 60 days of data
start_date = datetime.datetime.now() - datetime.timedelta(days=60)
# if market is open, get yesterday's data
if afterHours():
    end_date = datetime.datetime.now()
else:
    end_date = datetime.datetime.now() - datetime.timedelta(days=1)

# Use yFinance to get data in pandas_datareader
yf.pdr_override()

#Get last 3months of S&P 500 Index data from Yahoo Fininace
print ("Getting data")
SPX_data=data.get_data_yahoo('^GSPC', start = start_date, end = end_date, interval = "1d")
print (" ")

# Calculate 21 day and 5 daye EMAs based on Close data, store in data
SPX_data['21EMA'] = ta.ema(SPX_data['Close'] , length=21)
SPX_data['5EMA'] = ta.ema(SPX_data['Close'] , length=5)

print (SPX_data.tail(5))

# Pull  EMAs and close from data and compare
ema21 = SPX_data['21EMA'].iloc[-1]
ema5 = SPX_data['5EMA'].iloc[-1]
prev_ema5 = SPX_data['5EMA'].iloc[-2]
last_close = SPX_data['Close'].iloc[-1]
last_date = SPX_data.index[-1].strftime("%m/%d/%Y")


print ("S&P 500 Index Market Status as of ", last_date)
# do we need to add a buffer? If it's over by a penny, its a success
# Is Last close price over the 21 EMA?
if  last_close > ema21:
    print("Over 21EMA - Good to trade")
else:
    print("Hold")

# IS the 5EMA deading up compared to yesterday
if   ema5 > prev_ema5:
    print("5EMA is heading upward - Good to trade")
else:
    print("Hold")
