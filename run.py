#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  7 18:18:06 2021

@author: jimmytseng
"""
# y = int(input('初始投資 年：'))
# m = int(input('初始投資 月：'))
# d = int(input('初始投資 日：'))

# stop_loss = float(input('停損點：'))
# stop_loss = 0.10

import datetime as dt
starttime = dt.datetime.now() #開始時間
##############################################################################
import sys
import os
path = os.getcwd()
src = os.path.join(path,'Input')
out = os.path.join(path,'Output')

from module.tw_stock import get_data
import pandas as pd
import numpy as np

#=============================================================================
'''股票資料'''
os.chdir(os.path.join(path,'module/tw_stock'))
df = get_data.get_adj()
''''''
#=============================================================================
''''''

'''
==============================================================================
'''
# p_date = dt.date(y,m,d)
p_date = dt.date(2011,1,1)
Value = pd.DataFrame([[1000,1000]],columns=['Portfolio','TWII'],index = [str(p_date)])
daily_Value = pd.DataFrame([[1000,1000]],columns=['Portfolio','TWII'],index = [str(p_date)])

from module.regression import Regression as R
from module.weight import Markowitz as M

Stock_data = df[p_date+dt.timedelta(days=-365):]
record_stock = {}
record_stock_wT = {}
for i in range(100000):
    
    #=============================================================================
    print('======================================================================')
    '''Regression'''
    RStock_data = Stock_data[p_date+dt.timedelta(days=-100):p_date+dt.timedelta(days=-1)]
    print('迴歸期間：',p_date+dt.timedelta(days=-100),'~',p_date+dt.timedelta(days=-1))
    
    return_RStock_data = np.log(RStock_data/RStock_data.shift())
    return_RStock_data = return_RStock_data.fillna(method='ffill')
    return_RStock_data = return_RStock_data.dropna(how = 'all')
    
    Stock_stat = R.Regression(RStock_data)
    ''''''
    #=============================================================================
    '''choose'''
    MA_66 = Stock_data['^TWII'].loc[:p_date].rolling(66).mean()[-1]
    tt = Stock_data['^TWII'].loc[:p_date][-1]
    if MA_66 > tt:
        sit = 'bearish' # 定義熊市
        choose = Stock_stat.sort_values('Beta',ascending = True).head(5)
        stop_loss = 0.15
    
    if MA_66 <= tt:
        sit = 'bullish' # 定義牛市
        choose = Stock_stat.sort_values('Alpha',ascending = False).head(5)
        stop_loss = 0.2
    print(sit)
    ''''''
    #=============================================================================
    '''choose'''
    # choose = Stock_stat.sort_values('Beta',ascending = True).head(20)
    # choose = choose.sort_values('Alpha',ascending = False).head(10)
    # choose = Stock_stat.sort_values('Alpha',ascending = False).head(20)
    # choose = Stock_stat.sort_values('skew',ascending = False).head(10)
    
    
    choose = list(choose.index)
    print('choose:',choose)
    ''''''
    #=============================================================================
    '''weight'''
    C_return = return_RStock_data[choose]
    wT = M.weights(C_return)[0]
    vol = M.weights(C_return)[1]
    print('weights:',np.round(wT,2))
    print('volatility:',vol)
    ''''''
    #=============================================================================
    record_stock_wT[i] = pd.DataFrame([list(np.round(wT,2))],
                                   index = ['weight'],
                                   columns = choose)

    #=============================================================================
    PStock_data = Stock_data[p_date:][choose]
    Assets = pd.DataFrame(np.dot(PStock_data,wT))
    Assets.index = PStock_data.index
    
    OStock_data = Stock_data['^TWII'][p_date:]
    
    A_value = float(Assets.iloc[0])
    A_value_1 = A_value
    sit_1 = 0
    sit_2 = 0
    for g in range(len(Assets)):
        
        
        cc =float(Assets.iloc[g])
        if A_value < cc:
            A_value_1 = cc
        
        v_return = (cc - A_value_1)/A_value_1

        if v_return < - stop_loss:
            selldate = Assets.index[g]
            print('停損')
            break # 停損再平衡
        
        MA_20 = Stock_data['^TWII'].loc[:Assets.index[g]].rolling(66).mean()[-1]
        tt = Stock_data['^TWII'].loc[:Assets.index[g]][-1]
        if MA_20 > tt:
            sit_1 = sit_1+1
            if sit_1 !=0:
                sit_2 = 0
            if sit_1 == 10 and sit == 'bullish' and A_value < cc:
                selldate = Assets.index[g]
                print('牛市-->熊市')
                break # 牛市-->熊市 且虧損：再平衡
        
        if MA_20 <= tt:
            sit_2 = sit_2+1
            if sit_2 != 0:
                sit_1 = 0
            if sit_2 == 10 and sit == 'bearish' and A_value < cc:
                selldate = Assets.index[g]
                print('熊市-->牛市')
                break # 熊市-->牛市 且虧損：再平衡
            
        if Assets.index[g] == Assets.index[-1]:
            selldate = Assets.index[g]
            break
        
        '''計算每日價值'''
        if g+1 != len(Assets):
            unit = float(daily_Value['Portfolio'].iloc[-1]/Assets.iloc[g])
            spread = float(Assets.iloc[g+1] - Assets.iloc[g])
            C = daily_Value['Portfolio'].iloc[-1] + unit*spread
            
            unit = Value['TWII'].iloc[-1]/OStock_data.iloc[g]
            spread = OStock_data.iloc[g+1] - OStock_data.iloc[g]
            P = daily_Value['TWII'].iloc[-1] + unit*spread
            
            con = pd.DataFrame([[C,P]],columns = Value.columns , index = [str(Assets.index[g].date())])
            daily_Value = daily_Value.append(con)
        ''''''
            
        
    perid = str(p_date)+'~'+str(selldate.date())
    print ('投資期間：',perid)
    print('======================================================================\n')
    PStock_data = PStock_data[:selldate]
    record_stock[i] = PStock_data # 每一投資期間之個股變化情況
    
    #=============================================================================
    '''計算報酬'''
    CStock_data = Assets[0][:selldate]
    buyprice = CStock_data.iloc[0]
    sellprice = CStock_data.iloc[-1]
    
    unit = Value['Portfolio'].iloc[-1]/buyprice
    spread = sellprice - buyprice
    C = Value['Portfolio'].iloc[-1] + unit*spread
    
    P_0050 = df['^TWII'][p_date:selldate]
    buyprice = P_0050.iloc[0]
    sellprice = P_0050.iloc[-1]
    
    unit = Value['TWII'].iloc[-1]/buyprice
    spread = sellprice - buyprice
    P = Value['TWII'].iloc[-1] + unit*spread
    
    con = pd.DataFrame([[C,P]],columns = Value.columns , index = [str(selldate.date())])
    Value = Value.append(con)
    ''''''
    #=============================================================================
    
    p_date = selldate.date()
    
    if selldate >= df.index[-1]:
        print('finish')
        break
#=============================================================================


'''
==============================================================================
'''#存檔
os.chdir(out)

#=============================================================================
''''''
with pd.ExcelWriter('record.xlsx') as writer:
    for i in range(len(record_stock)):
        record_stock[i].loc['spread']=record_stock[i].iloc[-1]-record_stock[i].iloc[0]
        WW = pd.concat([record_stock_wT[i],record_stock[i]])
        sn = str(WW.index[1].date())+'~'+str(WW.index[-2].date())
        WW.to_excel(writer, sheet_name = sn)


daily_Value.index = pd.to_datetime(daily_Value.index)
daily_Value.to_csv('Portfolio vs TWII(daily).csv',index = True)
Value.to_csv('Portfolio vs TWII.csv',index = True)

print(Value)

# for i in record_stock:
#     plt.figure(figsize=(16, 9),dpi=500)
#     plt.plot(record_stock[i][record_stock[i].columns[0]], data = record_stock[i], linewidth=2)
#     plt.plot(record_stock[i][record_stock[i].columns[1]], data = record_stock[i], linewidth=2)
#     plt.plot(record_stock[i][record_stock[i].columns[2]], data = record_stock[i], linewidth=2)
#     plt.plot(record_stock[i][record_stock[i].columns[3]], data = record_stock[i], linewidth=2)
#     plt.plot(record_stock[i][record_stock[i].columns[4]], data = record_stock[i], linewidth=2)
#     plt.legend(prop={'size':10},loc=2)
#     plt.grid(True)
#     plt.title( str(record_stock[i].index[0].date())+'~'+str(record_stock[i].index[-1].date()),fontsize=18)
#     plt.xlabel( 'Date' ,fontsize=15)
#     plt.ylabel( 'Value' ,fontsize=15) # 每一投資期間之個股變化情況 折線圖

# ''''''
# def make_patch_spines_invisible(ax):
#     ax.set_frame_on(True)
#     ax.patch.set_visible(False)
#     for sp in ax.spines.values():
#         sp.set_visible(False)
# fig, host = plt.subplots()
# fig.subplots_adjust(right=0.75)

# par1 = host.twinx()
# par2 = host.twinx()

# # Offset the right spine of par2.  The ticks and label have already been
# # placed on the right by twinx above.
# par2.spines["right"].set_position(("axes", 1.2))
# # Having been created by twinx, par2 has its frame off, so the line of its
# # detached spine is invisible.  First, activate the frame but make the patch
# # and spines invisible.
# make_patch_spines_invisible(par2)
# # Second, show the right spine.
# par2.spines["right"].set_visible(True)

# p1, = host.plot([0, 1, 2], [0, 1, 2], "b-", label="Density")
# p2, = par1.plot([0, 1, 2], [0, 3, 2], "r-", label="Temperature")
# p3, = par2.plot([0, 1, 2], [50, 30, 15], "g-", label="Velocity")

# host.set_xlim(0, 2)
# host.set_ylim(0, 2)
# par1.set_ylim(0, 4)
# par2.set_ylim(1, 65)

# host.set_xlabel("Distance")
# host.set_ylabel("Density")
# par1.set_ylabel("Temperature")
# par2.set_ylabel("Velocity")

# host.yaxis.label.set_color(p1.get_color())
# par1.yaxis.label.set_color(p2.get_color())
# par2.yaxis.label.set_color(p3.get_color())

# tkw = dict(size=4, width=1.5)
# host.tick_params(axis='y', colors=p1.get_color(), **tkw)
# par1.tick_params(axis='y', colors=p2.get_color(), **tkw)
# par2.tick_params(axis='y', colors=p3.get_color(), **tkw)
# host.tick_params(axis='x', **tkw)

# lines = [p1, p2, p3]

# host.legend(lines, [l.get_label() for l in lines])

# plt.show()
# ''''''


#=============================================================================


'''
==============================================================================
'''#繪圖
import matplotlib.pyplot as plt

#=============================================================================
'''折線圖'''
plt.figure(figsize=(16, 9),dpi=500)
plt.plot( daily_Value['Portfolio'], data = daily_Value, color = '#f01111', linewidth=0.5)
plt.plot( daily_Value['TWII'], data = daily_Value, color = '#5DADE2', linewidth=0.5)

plt.legend(prop={'size':10})
plt.grid(True)
plt.title( 'Portfolio vs TWII',fontsize=18)
# plt.xticks(rotation=15) 
plt.xlabel( 'Date' ,fontsize=15)
plt.ylabel( 'Value' ,fontsize=15)
plt.savefig('Portfolio vs TWII.png' )
''''''
#=============================================================================
#=============================================================================
'''折線圖（Ｙ軸調整）'''
fig,ax = plt.subplots(figsize=(16, 9),dpi=500)
ax.plot(daily_Value['Portfolio'], data = daily_Value, color = '#f01111', linewidth=0.5)
ax.set_ylabel('Portfolio',color='#f01111',fontsize=20)
ax.tick_params(axis='y',labelcolor='#f01111')
plt.grid()
ax.legend(loc='upper left')

ax2=ax.twinx()
ax2.plot(daily_Value['TWII'], data = daily_Value, color = '#5DADE2', linewidth=0.5)
ax2.set_ylabel('TWII',color='#5DADE2',fontsize=20)
ax2.tick_params(axis='y',labelcolor='#5DADE2')
ax2.legend(loc='upper right')

plt.title('Portfolio vs TWII',fontsize=18)

plt.savefig('Portfolio vs TWII(adj).png' )
''''''
#=============================================================================
#=============================================================================
'''績效表現'''
years = (daily_Value.index[-1]-daily_Value.index[0]).days/365.25
IRR = (daily_Value.iloc[-1]/daily_Value.iloc[0])**(1/years)-1


return_daily_Value = np.log(daily_Value/daily_Value.shift(1))
return_daily_Value = return_daily_Value.fillna(method='ffill')
return_daily_Value = return_daily_Value.dropna(how = 'all')

ER = return_daily_Value.mean() * len(daily_Value)/years
sigma = return_daily_Value.std() * ((len(daily_Value)/years)**(1/2))
rf = 0.05
Sharp_Ratio = (ER - rf)/sigma

performance = pd.concat([IRR,sigma,Sharp_Ratio],axis=1)
performance.rename(columns={0:'IRR',1:'sigma',2:'Shape_Ratio'},inplace=True)
performance = np.round(performance,4)
performance.to_csv('performance.csv')
''''''
#=============================================================================
#=============================================================================
'''報酬波動圖'''
plt.figure(figsize=(16, 9),dpi=500)
plt.plot( return_daily_Value['Portfolio'], data = return_daily_Value, color = '#f01111', linewidth=0.5)
plt.plot( return_daily_Value['TWII'], data = return_daily_Value, color = '#5DADE2', linewidth=0.5)

plt.legend(prop={'size':10})
plt.grid(True)
plt.title( 'return\nPortfolio vs TWII',fontsize=18)
# plt.xticks(rotation=15) 
plt.xlabel( 'Date' ,fontsize=15)
plt.ylabel( 'Value' ,fontsize=15)
plt.savefig('Portfolio vs TWII(return).png' )
''''''
#=============================================================================
#=============================================================================
'''報酬波動圖（Ｙ軸調整）'''
fig,ax = plt.subplots(figsize=(16, 9),dpi=500)
ax.plot(return_daily_Value['Portfolio'], data = return_daily_Value, color = '#f01111', linewidth=0.5)
ax.set_ylabel('Portfolio',color='#f01111',fontsize=20)
ax.tick_params(axis='y',labelcolor='#f01111')
plt.grid()
ax.legend(loc='upper left')

ax2=ax.twinx()
ax2.plot(return_daily_Value['TWII'], data = return_daily_Value, color = '#5DADE2', linewidth=0.5)
ax2.set_ylabel('TWII',color='#5DADE2',fontsize=20)
ax2.tick_params(axis='y',labelcolor='#5DADE2')
ax2.legend(loc='upper right')

plt.title('return\nPortfolio vs TWII',fontsize=18)

plt.savefig('Portfolio vs TWII(adj return_).png' )
img = plt
''''''
#=============================================================================

'''
==============================================================================
'''

##############################################################################
endtime = dt.datetime.now() #結束時間
print(endtime - starttime) #程式執行時間

'''
MA_20 = Stock_data['^TWII'].rolling(20).mean()
MA_20.dropna(inplace=True)
MA_20 = MA_20.loc[str(dt.date(2019,1,1)):]
MA_20.name = '20 MA'

MA_60 = Stock_data['^TWII'].rolling(60).mean()
MA_60.dropna(inplace=True)
MA_60 = MA_60.loc[str(dt.date(2019,1,1)):]
MA_60.name = '60 MA'

TWII = Stock_data['^TWII'].loc[str(dt.date(2019,1,1)):]
TWII.name = 'TWII'


plt.figure(figsize=(16, 9),dpi=500)
plt.plot( TWII,data = TWII , color = '#f01111', linewidth=1.5)
plt.plot( MA_20,data = MA_20 , color = '#cd853f', linewidth=1)
plt.plot( MA_60,data = MA_60 , color = '#5DADE2', linewidth=1)


plt.legend(prop={'size':14})
plt.grid(True)
plt.title( 'MA',fontsize=18)
# plt.xticks(rotation=15) 
plt.xlabel( 'Date' ,fontsize=15)
plt.ylabel( 'Value' ,fontsize=15)
plt.savefig('MA.png' )
'''


