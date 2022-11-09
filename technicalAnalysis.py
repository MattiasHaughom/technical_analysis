#%% Imports
import numpy as np
import pandas as pd
import os
import yfinance as yf
from datetime import timedelta
import datetime as datetime

directory = "input_folder"
os.chdir(directory)
industry = pd.read_excel('OBStickers.xlsx')
allTickers = pd.read_excel('all_tickers.xlsx')


#%% Technical analysis
# importing data from relevant tickers
obx = pd.read_excel('all_tickers.xlsx')

    
tickers = list(obx['ticker'])

for tick in tickers:
    obx.loc[obx['ticker']== tick,'ticker'] = str(tick) + ".OL"

tickers = list(obx['ticker'])


now = datetime.datetime.now()
yesterday = (now - timedelta(days=1)).strftime('%Y-%m-%d')
n = 365
# # Add 2 minutes to datetime object containing current time
past_time = now - timedelta(days=n)

now = now.strftime('%Y-%m-%d')
# Convert datetime object to string in specific format 
past_time = past_time.strftime('%Y-%m-%d')



data1 = yf.download(  # or pdr.get_data_yahoo(...
        # tickers list or string as well
        tickers = tickers,

        # use "period" instead of start/end
        # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        # (optional, default is '1mo')
        start=past_time, 
        end=now,

        # fetch data by interval (including intraday if period < 60 days)
        # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        # (optional, default is '1d')
        interval = "1d",

        # group by ticker (to access via data['SPY'])
        # (optional, default is 'column')
        #group_by = 'ticker',

        # adjust all OHLC automatically
        # (optional, default is False)
        auto_adjust = True,

        # download pre/post regular market hours data
        # (optional, default is False)
        prepost = True,

        # use threads for mass downloading? (True/False/Integer)
        # (optional, default is True)
        threads = True,

        # proxy URL scheme use use when downloading?
        # (optional, default is None)
        proxy = None)


yahoo_data = data1.stack()
yahoo_data.reset_index(drop=False, inplace=True)
yahoo_data.rename(columns=({'Date':'date','level_1':'ticker'}), inplace = True)
prices = data1['Close']
prices.index = pd.to_datetime(prices.index)
try:
    if all([np.isnan(i) for i in prices.loc[now,:]]):
        prices = prices.loc[:yesterday,:]
except KeyError:
    pass


#prices = prices.loc[prices.index <= prices.index[-2],:]



##### 10 day Rate of change
def tenRoC(formation,tick):
    try:
        RoC = prices.loc[formation,tick]/prices.iloc[-10,:][tick]-1
        return RoC
    except KeyError:
        return 0


##### Monthly Rate of change
def monthRoC(formation,tick):
    try:
        RoC = prices.loc[formation,tick]/prices.iloc[-21,:][tick]-1
        return RoC
    except KeyError:
        return 0


##### 50 day Rate of change
def fiftyRoC(formation,tick):
    try:
        RoC = prices.loc[formation,tick]/prices.iloc[-50,:][tick]-1
        return RoC
    except KeyError:
        return 0


##### 50 day Rate of change
def Q3RoC(formation,tick):
    try:
        RoC = prices.loc[formation,tick]/prices.iloc[-200,:][tick]-1
        return RoC
    except KeyError:
        return 0



##### one month reversial
mtl_ret = prices.pct_change().resample('M').agg(lambda x: (x+1).prod() -1)

def reversial(tick):
    try:
        tmp = mtl_ret.loc[mtl_ret.index == mtl_ret.index[len(mtl_ret)-1],:]
        tmp = tmp.T
        tmp = tmp.sort_values(by = [str(tmp.columns[0])]).reset_index().reset_index()
        tmp = tmp.loc[tmp['index'] == tick,'level_0'].values
        return tmp[0]
    except KeyError:
        return 0

#### Standard deviation of returns over 80 days
def vol80(tick):
    try:
        tmp = prices.iloc[-80:,:][tick].pct_change()
        stdDev = tmp[1:].apply(lambda x: np.log(1+x)).std()*np.sqrt(len(tmp[1:]))
        return stdDev
    except KeyError:
        return 0


#### Standard deviation of returns over 30 days
def vol30(tick):
    try:
        tmp = prices.iloc[-21:,:][tick].pct_change()
        stdDev = tmp[1:].apply(lambda x: np.log(1+x)).std()*np.sqrt(len(tmp[1:]))
        return stdDev
    except KeyError:
        return 0


indicators = pd.DataFrame(columns= ('ticker','10day','21day','50day','200day','1Mrev','vol80','vol30'))
for number,stock in enumerate(prices.columns):
    latest = prices.index[len(prices)-1]
    indicators.at[number,'ticker'] = prices.columns[number]
    indicators.at[number,'10day'] = tenRoC(latest,stock)
    indicators.at[number,'21day'] = monthRoC(latest,stock)
    indicators.at[number,'50day'] = fiftyRoC(latest,stock)
    indicators.at[number,'200day'] = Q3RoC(latest,stock)
    indicators.at[number,'1Mrev'] = reversial(stock)
    indicators.at[number,'vol80'] = vol80(stock)
    indicators.at[number,'vol30'] = vol30(stock)



lovVol = list(indicators.sort_values(['vol30']).loc[np.logical_and(indicators['vol30']>0,pd.notna(indicators['vol30'])),'ticker'].head(50))
# Samle noen aksjer som har høy kortsiktig (ukesmomentum) momentum og lav volatilitet
volMom10 = indicators.loc[np.logical_and([indicators.loc[item,'10day'] > indicators.loc[item,'21day'] for item in indicators.index], 
                                       [item in lovVol for item in indicators['ticker']]),:].sort_values('10day', ascending = False).reset_index(drop = True)

tidager = [ticker for number,ticker in enumerate(volMom10['ticker']) if np.logical_and(volMom10.loc[number,'10day'] > volMom10.loc[number,'21day'], volMom10.loc[number,'10day'] > 0)]


# Sample noen aksjer som har høy måndes momentum og lav volatilitet
volMom21 = indicators.loc[np.logical_and([indicators.loc[item,'21day'] > indicators.loc[item,'50day'] for item in indicators.index], 
                                       [item in lovVol for item in indicators['ticker']]),:].sort_values('10day', ascending = False).reset_index(drop = True)

tjuedager = [ticker for number,ticker in enumerate(volMom21['ticker']) if np.logical_and(volMom21.loc[number,'21day'] > volMom21.loc[number,'50day'], volMom21.loc[number,'21day'] > 0)]

# Se etter aksjer som treffer alle kriterier; kan vel være en god investering?
resultat = set(tidager).intersection(tjuedager)
print(resultat)










