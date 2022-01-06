#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 30 11:09:15 2020

@author: jimmytseng
"""

import os
from pandas_datareader import data as web
import yfinance as yf
import warnings
import datetime as dt
import pandas as pd

path = os.getcwd()
os.chdir(path)
Stocks_Data = pd.read_csv('TWStocks_data.csv',index_col=[0], header=[0,1])
Stocks_Data.index = pd.to_datetime(Stocks_Data.index)

StocksList = pd.read_csv('TW150 list.csv',index_col = '排行')['證券名稱'].head(50)
StocksList = list(StocksList)
for i in range(len(StocksList)):
    StocksList[i] = str(StocksList[i]) + '.TW'
StocksList.insert(0,'^TWII')
StocksList.insert(1,'0050.TW')

yf.pdr_override()
warnings.filterwarnings("ignore")

start = dt.date(2000,1,1)
end = dt.date.today()
df = web.get_data_yahoo(StocksList, start, end)
df.drop(df.index[0],inplace=True)
df.to_csv('TWStocks_data.csv',index = True)


# StocksList = pd.read_csv('TW150 list.csv',index_col = '排行')['證券名稱'].tail(150)
# StocksList = list(StocksList)
# for i in range(len(StocksList)):
#     StocksList[i] = str(StocksList[i]) + '.TW'
# StocksList.insert(0,'^TWII')
# StocksList.insert(1,'0050.TW')

# yf.pdr_override()
# warnings.filterwarnings("ignore")

# start = dt.date(2000,1,1)
# end = dt.date.today()
# df = web.get_data_yahoo(StocksList, start, end)
# df.drop(df.index[0],inplace=True)
# df.to_csv('TWStocks_data_tail.csv',index = True)