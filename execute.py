import sys
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats.stats import pearsonr
import random
import json
from itertools import permutations
import numpy as np
import copy
import pickle
import time
import multiprocessing as mp
import math
import matplotlib.pyplot as plt
from IPython.display import display
from datetime import datetime
import datetime as dt
import ib_insync
print(ib_insync.__all__)

from ib_insync import *
#Andy - not using Jupyter
#util.startLoop()

#Andy- this is the default account, setting so that orders can be allocated to it.
acc_num = ''

#Connect to IB Gateway
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=3,timeout=100)



def format_days(x):
    if len(x)<2:
        return("0"+x)
    else:
        return(x)
    
def intersection(lst1, lst2): 
    lst3 = [value for value in lst1 if value in lst2] 
    return lst3 

#inut file
#Andy - No dailyorders.pickle yet. Testing with a csv from GitHub.
#target_position = pd.read_pickle("dailyorders.pickle")
target_position = pd.read_csv("2020_6_5.csv",index_col='Date')
target_position.index = pd.to_datetime(target_position.index)
target_position = target_position[target_position.index==target_position.index[-1]]


##insert the location of the exchange.
ExchangeData = pd.read_csv("exchange.csv")
ExchangeData.index= ExchangeData["Stock"]
#Andy - this seems to be a test line
#ExchangeData.loc["AAPL"]["primaryExchange"]=="NASDAQ"
StrategyDay = str(target_position.index[0].year)+"-"+format_days(str(target_position.index[0].month))+"-"+format_days(str(target_position.index[0].day))


#Construct CurrentPortfolio
#Andy - this portfolio() only works for the default account, and I can't yet find how to set this.
CurrentPortfolio = pd.DataFrame()
for element in ib.positions():
    symbol = str(element).split("symbol='")[1].split("'")[0]
    position =str(element).split("position=")[1].split(",")[0]
    list_row = {"symbol":symbol, "position":position}
    
    CurrentPortfolio = CurrentPortfolio.append(list_row, ignore_index=True)


for company in target_position.columns:
    if company not in CurrentPortfolio:
        symbol = company
        position = 0
        list_row = {"symbol":symbol, "position":position}
        
        CurrentPortfolio = CurrentPortfolio.append(list_row, ignore_index=True)

CurrentPortfolio.index = CurrentPortfolio["symbol"]
PreviousPortfolio = CurrentPortfolio.copy()
excluse = {"UTX","RTN","S","ZAYO","GDI","SBGL","INXN","CY","MSG","LK"}



####

# My file destination.

#Currently not used
##existing_stocks = set(CurrentPortfolio["symbol"]).intersection(set(target_position))



###Execution
for element in target_position.columns:
    print(element)
    amount_portfolio = CurrentPortfolio[CurrentPortfolio.index==element]["position"] 
    new_amount_portfolio = target_position[target_position.index==StrategyDay][element]

    
    # ROUNDING
    #Andy - added try to handle NaN amount
    try:
        amount_portfolio = int(round(amount_portfolio))
        new_amount_portfolio = int(round(new_amount_portfolio))
    except:
        print(element)
        continue
    
    # Buy / Sell / Hold
    if new_amount_portfolio>amount_portfolio:
        direction = "BUY"
        trade_amount = new_amount_portfolio - amount_portfolio
    if new_amount_portfolio<amount_portfolio:
        direction = "SELL"
        trade_amount = amount_portfolio - new_amount_portfolio
    if new_amount_portfolio==amount_portfolio:
        direction = "HOLD"
        trade_amount = 0
    
    if direction!="HOLD":
        #Andy - changed to element as no stock variable set
        if(element not in excluse):
            try:
                contract = Stock(element, 'SMART', 'USD', primaryExchange=ExchangeData.loc[element]["primaryExchange"])
                order = MarketOrder(direction, trade_amount,account=acc_num)
    #             trade = ib.placeOrder(contract, order)
                ib.sleep(0.2)
                print(contract)
                print(order)
            except:
                print(element)