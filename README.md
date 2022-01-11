# 自動再平衡
> 將台股資料匯入，並執行策略，來看最終的績效如何。  
其中會因為觸發再平衡條件而自動再平衡

## Requirements
- python >= 3.8
- [requirements.txt](https://github.com/JT-427/auto-rebalance-TW-/blob/master/requirements.txt)

## Install package
```
pip install -r requirements.txt
```

## Run
```
python run.py
```

## Description
### Duration
&nbsp; 2011/1~今天
### Strategy
1. 選股池  
&nbsp; 台股市值前150

2. 利用回歸模型，計算出各檔股票的統計數據（資料來源為股價日報酬）  
    ```py
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
    ```

3. 定義熊市、牛市  
&nbsp; 購買標的當天的大盤若低於既季均線，則將市場視為熊市，反之則為牛市
    ```py
    if MA_66 > tt:
        sit = 'bearish' # 定義熊市
        choose = Stock_stat.sort_values('Beta',ascending = True).head(5)
        stop_loss = 0.15

    if MA_66 <= tt:
        sit = 'bullish' # 定義牛市
        choose = Stock_stat.sort_values('Alpha',ascending = False).head(5)
        stop_loss = 0.2
    ```

4. 策略  
    + 當市場為熊市時  
    &nbsp; 選擇Beta最小的五黨股票，並用Markowitz Efficient Frontier來取得權重
    + 當市場為牛市時  
    &nbsp; 選擇Alpha最小的五黨股票，並用Markowitz Efficient Frontier來取得權重
    ```py
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
    ```
5. 再平衡條件
    + 市場反轉  
    &nbsp; 當牛市變成熊市，或熊市變成牛市時，會先檢查投資組合是否呈現虧損，若為虧損，則觸發自動再平衡
    + 停損  
    &nbsp; 牛市：  
    &nbsp; &nbsp; &nbsp; 停損點為投資期間最高價值，與當日價值之報酬若低於-20%，則觸發停損，執行自動再平衡  
    &nbsp; 熊市：  
    &nbsp; &nbsp; &nbsp; 停損點為投資期間最高價值，與當日價值之報酬若低於-15%，則觸發停損，執行自動再平衡  

    &nbsp; &nbsp; &nbsp; **觸發再平衡條件後，會將所有股票賣出，並重新挑選標的買入。**  

    ```py
    v_return = (cc - A_value_1)/A_value_1

    if v_return < - stop_loss:
        selldate = Assets.index[g]
        print('停損')
        break # 停損再平衡

    MA_66 = Stock_data['^TWII'].loc[:Assets.index[g]].rolling(66).mean()[-1]
    tt = Stock_data['^TWII'].loc[:Assets.index[g]][-1]
    if MA_66 > tt:
        sit_1 = sit_1+1
        if sit_1 !=0:
            sit_2 = 0
        if sit_1 == 10 and sit == 'bullish' and A_value < cc:
            selldate = Assets.index[g]
            print('牛市-->熊市')
            break # 牛市-->熊市 且虧損：再平衡

    if MA_66 <= tt:
        sit_2 = sit_2+1
        if sit_2 != 0:
            sit_1 = 0
        if sit_2 == 10 and sit == 'bearish' and A_value < cc:
            selldate = Assets.index[g]
            print('熊市-->牛市')
            break # 熊市-->牛市 且虧損：再平衡
    ```

### Result
投資組合與大盤之價值比較
![img](https://github.com/JT-427/auto-rebalance-TW/blob/master/Output/Portfolio%20vs%20TWII.png)
|          |Portfolio         |TWII              |
|----------|------------------|------------------|
|2011-01-01|1000.0            |1000.0            |
|2011-06-29|1043.3140539357225|949.9273577985762 |
|2012-08-17|1223.9606022136643|827.4428246308946 |
|2013-06-26|1551.8476749660604|862.553023613287  |
|2013-09-13|1624.6019486699322|905.0335900525791 |
|2014-08-18|2232.775609721255 |1012.8537797478931|
|2014-09-04|2242.1077051158272|1044.7176670789568|
|2015-08-20|1793.9409758567822|889.6999558422842 |
|2015-10-21|1824.355214571223 |953.8996045498568 |
|2015-12-21|1864.8379053543952|917.6612792666593 |
|2016-03-01|1945.6509743675615|940.2127685589272 |
|2016-11-22|2019.4603608900588|1011.9786324698466|
|2017-01-13|2032.489335201333 |1039.1740938227563|
|2017-12-18|2422.8753033018156|1164.1229001956635|
|2018-01-12|2499.778230168822 |1205.9433190653017|
|2018-05-04|2997.5798657191153|1166.6547462835722|
|2018-05-24|2998.292869332848 |1211.8123674713986|
|2018-07-06|3010.847795184054 |1175.4301319656738|
|2019-01-28|3109.1175747603297|1109.4774836226377|
|2019-05-27|4348.591907212298 |1145.0221183519832|
|2019-09-19|4478.316326520718 |1207.1333375821112|
|2020-03-02|5093.239818675606 |1237.6875336850007|
|2020-05-18|5224.238999245061 |1190.05346643478  |
|2021-05-24|11059.199470723514|1810.283370048474 |
|2021-06-04|10968.039796860177|1899.9339203211296|
|2022-01-06|10828.822141097882|2035.1664646333052|

投資組合與大盤之波動度比較
![img](https://github.com/JT-427/auto-rebalance-TW/blob/master/Output/Portfolio%20vs%20TWII(return).png)



## Resource
- [yfinance](https://github.com/ranaroussi/yfinance)  
yfinance資料取得方便且免費，但有許多錯誤資料，導致算出來的績效與實際有些出入。



***
### 專案開發期間
2019/12 ~ 2020/1
