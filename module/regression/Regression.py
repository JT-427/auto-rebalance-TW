#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  7 00:40:57 2021

@author: jimmytseng
"""
import pandas as pd
import numpy as np
import statsmodels.api as sm
import scipy.stats as si

def Regression (Stock_data):
    StocksList = list(Stock_data.columns)
    return_Stock_data = np.log(Stock_data/Stock_data.shift())
    return_Stock_data = return_Stock_data.fillna(method='ffill')
    return_Stock_data = return_Stock_data.dropna(how = 'all')
    #=============================================================================
    '''迴歸'''
    XX=sm.add_constant(return_Stock_data['^TWII'])
    
    lr_list=[]
    A = {}
    l_alpha = []
    l_alpha_P = []
    l_beta = []
    l_beta_P = []
    
    for g in StocksList:
        est = sm.OLS(return_Stock_data[g] , XX)
        est = est.fit()
        sol = est.summary()
        lr_list.append(sol.as_csv())
        
        An = pd.DataFrame(est.params)
        An['coeff'] = est.params
        An["p_values"] = est.summary2().tables[1]["P>|t|"]
        An = An.iloc[:, [1, 2]]
        An.rename(index = {'const' : 'Alpha','^TWII' : 'Beta'},inplace = True)
        A[g] = An
        
        l_alpha.append(A[g].iloc[0,0]) #alpha
        l_alpha_P.append(A[g].iloc[0,1]) #alpha P-value
        l_beta.append(A[g].iloc[1,0]) #beta
        l_beta_P.append(A[g].iloc[1,1]) #beta
    ''''''
    #=============================================================================
    ''''''
    mean = return_Stock_data.mean()
    std = return_Stock_data.std()
    skew = pd.Series(si.skew(Stock_data), index = (StocksList))
    kurt = pd.Series(si.kurtosis(Stock_data), index = (StocksList))
    alpha = pd.Series(l_alpha, index = (StocksList))
    alpha_P = pd.Series(l_alpha_P, index = (StocksList))
    beta = pd.Series(l_beta, index = (StocksList))
    beta_P = pd.Series(l_beta_P, index = (StocksList))
    
    Stock_stat = pd.concat([mean, std, skew, kurt, alpha, alpha_P, beta, beta_P],axis = 1)
    Stock_stat.columns = ['mean', 'std', 'skew', 'kurt', 'Alpha', 'alpha_P', 'Beta', 'beta_P']
    ''''''
    #=============================================================================
    return Stock_stat