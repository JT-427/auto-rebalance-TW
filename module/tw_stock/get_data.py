#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 24 23:36:24 2020

@author: jimmytseng
"""
from pandas_datareader import data as web
import yfinance as yf
import warnings
import datetime as dt
import pandas as pd


def get_StockList():
    StocksList = pd.read_csv('TW150 list.csv',index_col = '排行')['證券名稱'].head(50)
    StocksList = list(StocksList)
    for i in range(len(StocksList)):
        StocksList[i] = str(StocksList[i]) + '.TW'
    StocksList.insert(0,'^TWII')
    StocksList.insert(1,'0050.TW')
    
    return StocksList

def get_data():
    Stocks_Data = pd.read_csv('TWStocks_data.csv',index_col=[0], header=[0,1])
    Stocks_Data.index = pd.to_datetime(Stocks_Data.index)
    return Stocks_Data

def add_data():
    Stocks_Data = get_data()
    yf.pdr_override()
    warnings.filterwarnings("ignore")
    StocksList = get_StockList()
    
    start = Stocks_Data.index[-1].date()
    end = dt.date.today()
    
    df = web.get_data_yahoo(StocksList, start, end)
    
    if df.index[-1] != Stocks_Data.index[-1]:
        new = pd.concat([Stocks_Data,df],axis=0)
        new.to_csv('TWStocks_data.csv',index = True)
    return

def get():
    Stocks_Data = get_data()
    
    yf.pdr_override()
    warnings.filterwarnings("ignore")
    start = dt.date.today()+dt.timedelta(days=-10)
    end = dt.date.today()
    
    test = web.get_data_yahoo(['^TWII'], start, end)
    
    if Stocks_Data.index[-1].date() == test.index[-1].date():
        return Stocks_Data
    
    if Stocks_Data.index[-1].date() != test.index[-1].date():
        add_data()
        Stocks_Data = get_data()
        return Stocks_Data

def get_adj():
    Adj_Close_Stocks_Data = get()['Adj Close']
    Adj_Close_Stocks_Data.dropna(how = 'all')
    Adj_Close_Stocks_Data = Adj_Close_Stocks_Data.fillna(method='ffill')
    return Adj_Close_Stocks_Data


