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
util.startLoop()

#Connect to IB Gateway
ib = IB()
ib.connect('127.0.0.1', 4000, clientId=1,timeout=100)

def format_days(x):
    if len(x)<2:
        return("0"+x)
    else:
        return(x)
    
def intersection(lst1, lst2): 
    lst3 = [value for value in lst1 if value in lst2] 
    return lst3 

#inut file
target_position = pd.read_pickle("dailyorders.pickle")
target_position.index = pd.to_datetime(target_position.index)
target_position = target_position[target_position.index==target_position.index[-1]]


##insert the location of the exchange.
ExchangeData = pd.read_csv("exchange.csv")
ExchangeData.index= ExchangeData["Stock"]
ExchangeData.loc["AAPL"]["primaryExchange"]=="NASDAQ"
StrategyDay = str(target_position.index[0].year)+"-"+format_days(str(target_position.index[0].month))+"-"+format_days(str(target_position.index[0].day))


#Construct CurrentPortfolio
CurrentPortfolio = pd.DataFrame()
for element in ib.portfolio():
    symbol = str(element).split("symbol='")[1].split("'")[0]
#     primaryExchange = str(element).split("primaryExchange='")[1].split("'")[0]
    position =str(element).split("position=")[1].split(",")[0]
    unrealizedPNL = str(element).split("unrealizedPNL=")[1].split(",")[0]
    realizedPNL = str(element).split("realizedPNL=")[1].split(",")[0]
    marketValue = str(element).split("marketValue=")[1].split(",")[0]
    list_row = {"symbol":symbol, "position":position,"unrealizedPNL":unrealizedPNL,"realizedPNL":realizedPNL,"marketValue":marketValue}
    
    CurrentPortfolio = CurrentPortfolio.append(list_row, ignore_index=True)

for company in target_position.columns:
    if company not in CurrentPortfolio:
        symbol = company
        position = 0
        unrealizedPNL = 0 
        realizedPNL = 0
        marketValue = 0
        list_row = {"symbol":symbol, "position":position,"unrealizedPNL":unrealizedPNL,"realizedPNL":realizedPNL,"marketValue":marketValue}
        
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
    amount_portfolio = CurrentPortfolio[CurrentPortfolio.index==element]["position"] 
    new_amount_portfolio = target_position[target_position.index==StrategyDay][element]

    
    # ROUNDING
    amount_portfolio = int(round(amount_portfolio))
    new_amount_portfolio = int(round(new_amount_portfolio))
    
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
        if(stock not in excluse):
            try:
                contract = Stock(element, 'SMART', 'USD', primaryExchange=ExchangeData.loc[element]["primaryExchange"])
                order = MarketOrder(direction, trade_amount)
    #             trade = ib.placeOrder(contract, order)
#                 print(contract)
#                 print(order)
            except:
#                 print(element)
