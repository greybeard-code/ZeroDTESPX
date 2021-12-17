# Code to check market conditions based on ZeroDTE-SPX Trades
# By Derek Jones

# Install these packages if needed:
# pip install pandas-datareader
# pip install pandas
# pip install yfinance
# pip install pandas-ta
# pip install pytz holidays
# pip install plotly kaleido


# Import Pandas and Pandas TA for data analysis.
import pandas as pd
from pandas.core.base import SpecificationError
import pandas_ta as ta
import pandas_datareader as pdr 

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
start_date = datetime.datetime.now() - datetime.timedelta(days=80)
# if market is open, get yesterday's data
if afterHours():
    end_date = datetime.datetime.now()
else:
    end_date = datetime.datetime.now() - datetime.timedelta(days=1)

# Use yFinance to get data in pandas_datareader
yf.pdr_override()

#Get last 3months of S&P 500 Index data from Yahoo Finance
print ("Getting data")
SPX_data=pdr.get_data_yahoo('^GSPC', start = start_date, end = end_date, interval = "d")
print (" ")

# Calculate  EMAs based on Close data, store in data
SPX_data['50SMA'] = ta.sma(SPX_data['Close'] , length=50)
SPX_data['34EMA'] = ta.ema(SPX_data['Close'] , length=34)
SPX_data['21EMA'] = ta.ema(SPX_data['Close'] , length=21)
SPX_data['8EMA'] = ta.ema(SPX_data['Close'] , length=8)
SPX_data['5EMA'] = ta.ema(SPX_data['Close'] , length=5)
SPX_data['3EMA'] = ta.ema(SPX_data['Close'] , length=3)

del SPX_data["Open"]
del SPX_data["High"]
del SPX_data["Low"]
del SPX_data["Volume"]
del SPX_data["Adj Close"]


print (SPX_data.tail(5))
print("")

# Pull  EMAs and close from data and compare
last_close = SPX_data['Close'].iloc[-1]
last_date = SPX_data.index[-1].strftime("%m/%d/%Y")
sma50= SPX_data['50SMA'].iloc[-1]
ema34= SPX_data['34EMA'].iloc[-1]
ema21= SPX_data['21EMA'].iloc[-1]
ema8 = SPX_data['8EMA'].iloc[-1]
ema5 = SPX_data['5EMA'].iloc[-1]
ema3 = SPX_data['3EMA'].iloc[-1]
prev_ema3 = SPX_data['3EMA'].iloc[-2]
prev_ema5 = SPX_data['5EMA'].iloc[-2]


print ("S&P 500 Index Market (SPX) Status as of ", last_date, "(last daily closing)")
print("  Last closing price: ${:.2f}".format(last_close) )
# do we need to add a buffer? If it's over by a penny, its a success
# Is Last close price over the 21 EMA?

if  last_close > ema21:
    print("  Last close over 21EMA - Good to trade")
    ema21_status= 'trade'
else:
    print("  Last close over 21EMA - Hold")
    ema21_status= 'hold'

# IS the 5EMA deading up compared to yesterday - Alpha5

if   ema5 > prev_ema5:
    print("  Alpha5 - 5EMA is heading upward - Good to trade")
    ema5_status= 'trade'
else:
    print("  Alpha5 - Hold")
    ema5_status='hold'

# IS the 3EMA heading up compared to yesterday - Alpha3
if  ema3 > prev_ema3:
    print("  Alpha3 - 3EMA is heading upward - Good to trade")
    ema3_status= 'trade'
else:
    print("  Alpha3 - Hold")
    ema3_status='hold'

print("")
print(" -=-=-=-=-=-=- ")
print("  Other trades ")
print("")

# IS the 8EMA over 21ema? - 7dte
if  ema8 > ema21:
    print("  7dte - 8ema is over 21ema - Good to trade")
    ema3_status= 'trade'
else:
    print("  7dte - 8ema is over 21ema - Hold")
    ema8_status='hold'
# IS the 3EMA over 21ema? - 7dte
if  ema3 > ema21:
    print("  7dte - 3ema is over 21ema - Good to trade")
    ema3_status= 'trade'
else:
    print("  7dte - 3ema is over 21ema - Hold")
    ema8_status='hold'

# IS the 3EMA over 8ema - BWB Filter
if   ema3 > ema8:
    print("  BWB - 3EMA is over 8EMA - Good to trade")
    #ema3_status= 'trade'
else:
    print("  BWB 3ema over 8ema - Hold")
    #ema3_status='hold'

# IS the 21ema below 34ems - https://www.stockmarketoptionstrading.net/posts/17485605
# when to buy call options
if   ema34 > ema21 :
    if ema3 > ema5:
        print("  Time to Buy SPY Calls - 34ema over 21ema and 3ema is over 5ema ")
    else:
        print("  Market is down, but hasn't bottomed out - Hold buying calls")
else:
    print("  Market is still on up trend - 21 over 34 ema")


  
# IS the 21EMA over 50sma? - DIA Bull
if  ema21 > sma50:
    print("  DIA Bull - 21ema is over 50sma - Good to trade")

else:
    print("  DIA Bull - 21ema is under 50sma - Hold")


print("")

