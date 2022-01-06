#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  7 00:19:12 2021

@author: jimmytseng
"""

import numpy as np
from scipy.optimize import minimize

#=============================================================================
'''Markowitz'''
# return and volatility functions
def Portfolio_performance(weights, mean_returns, cov_matrix):
	returns = np.sum(mean_returns *weights )
	std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
	return std, returns
# volatility function of portfolio
def Portfolio_volatility(weights, mean_returns, cov_matrix):
	return Portfolio_performance(weights, mean_returns, cov_matrix)[0]
# MV model
def min_variance(mean_returns, cov_matrix):
	num_assets = len(mean_returns)
	args = (mean_returns, cov_matrix)
	constraints = ({'type':'eq', 'fun': lambda x: np.sum(x)-1})
	bound = (0,1)
	bounds = tuple(bound for asset in range(num_assets))
	result = minimize(Portfolio_volatility, num_assets *[1/num_assets , ], args=args ,
                   method= 'SLSQP' , bounds=bounds , constraints=constraints )
	return result
''''''
#=============================================================================

def weights(choose_return_Stock_data):
    mean_return = choose_return_Stock_data.mean()
    cov_matrix = choose_return_Stock_data.cov()
    wT = min_variance(mean_return,cov_matrix)['x']
    vol = Portfolio_volatility(wT,mean_return,cov_matrix)
    return wT ,vol