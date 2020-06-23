
import pandas as pd
import numpy as np
import copy
import pickle
import os
import time
#import matplotlib.pyplot as plt
from IPython.display import display
from datetime import datetime
import datetime as dt
import ib_insync
print(ib_insync.__all__)

from ib_insync import *
#Andy - not using Jupyter
util.startLoop()

#Andy- this is the default account, setting so that orders can be allocated to it.
acc_num = 'DU2280941'

#Connect to IB Gateway
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=10,timeout=100)

#subprograms
def format_days(x):
    if len(x)<2:
        return("0"+x)
    else:
        return(x)
    
def intersection(lst1, lst2): 
    lst3 = [value for value in lst1 if value in lst2] 
    return lst3 
#/subprograms
run=2

path = "/home/svdr/ibtest/"
current_run = str(datetime.today().year) + format_days(str(datetime.today().month)) + format_days(str(datetime.today().day))+"_"+str(run)
os.mkdir(path+"logs/"+current_run)


##ExchangeData
#ExchangeData + Strategy Day
ExchangeData = pd.read_csv("exchange.csv")
ExchangeData.index= ExchangeData["Stock"]
#Test line
#print(ExchangeData.loc["AAPL"]["primaryExchange"]=="NASDAQ")
#StrategyDay = str(target_position.index[0].year)+"-"+format_days(str(target_position.index[0].month))+"-"+format_days(str(target_position.index[0].day))
#/ExchangeData

## Build Current Portfolio
CurrentPortfolio = pd.DataFrame()
for element in ib.positions(account=acc_num):
    symbol = str(element).split("symbol='")[1].split("'")[0]
    position =str(element).split("position=")[1].split(",")[0]
    list_row = {"symbol":symbol, "position":position}
    
    CurrentPortfolio = CurrentPortfolio.append(list_row, ignore_index=True)
    
CurrentPortfolio.index = CurrentPortfolio["symbol"]
CurrentPortfolio = CurrentPortfolio.transpose()
CurrentPortfolio = CurrentPortfolio[0:1]
CurrentPortfolio = CurrentPortfolio.astype(float).astype(int)
PreviousPortfolio = CurrentPortfolio.copy()
PreviousPortfolio = PreviousPortfolio[0:1]

## /Build CurrentPortfolio

#TargetPortfolio
target_position = pd.read_csv("/home/svdr/ibtest/Alphas/Alpha7/2020_6_23.csv",index_col='Date')
target_position.index = pd.to_datetime(target_position.index)
target_position = target_position[target_position.index==target_position.index[-1]]
target_position = target_position.round(decimals=0)
target_position = target_position.fillna(0).astype(np.int64)
#/TargetPortfolio


#Outputs
CurrentPortfolio.index = target_position.index
PreviousPortfolio.index = target_position.index

CurrentPortfolio.to_csv(path+"logs/"+current_run+"/"+"CurrentPortfolio.csv")
PreviousPortfolio.to_csv(path+"logs/"+current_run+"/"+"PreviousPortfolio.csv")
target_position.to_csv(path+"logs/"+current_run+"/"+"TargetPosition.csv")
#/Outputs


# Extra positions. Check to see what positions are inexistent in CurrentPortfolio.
inexistent_positions = set(target_position.columns) - set(CurrentPortfolio.columns)
inexistent_positions = pd.DataFrame(inexistent_positions)
inexistent_positions.columns = {"symbol"}
inexistent_positions.to_csv(path+"logs/"+current_run+"/"+"inexistent_positions.csv")
#/ExtraPositions

#in target, but not in Current.
for element in inexistent_positions["symbol"]:
    CurrentPortfolio[element]=0

#currentPortfolio with added inexistent items.
CurrentPortfolio.to_csv(path+"logs/"+current_run+"/"+"new_CurrentPortfolio.csv")
#to be closed:
#set(CurrentPortfolio.columns)-set(target_position.columns)


#Define Excluded Companies
excluded_companies = ["MLNX","LSXMR"]


#Orders
orders = target_position - CurrentPortfolio
execution_log=pd.DataFrame()
excluded_log=pd.DataFrame()
error_log=pd.DataFrame()
already_traded_log = pd.DataFrame()
for column in orders.columns:
    if column not in excluded_companies:
    #     print(column)
        trade_amount = orders[column][0]
        company = column
        if trade_amount > 0:
            direction = "BUY"
        elif trade_amount < 0:
            direction = "SELL"
        elif trade_amount == 0:
            direction = "HOLD"

        trade_amount = abs(trade_amount)

    #EXECUTE        
        if direction!="HOLD":
            print(column,direction)
            try:
                contract = Stock(company, 'SMART', 'USD', primaryExchange=ExchangeData.loc[company]["primaryExchange"])
                order = MarketOrder(direction, trade_amount,account=acc_num) #,account=acc_num
                trade = ib.placeOrder(contract, order)
                ib.sleep(0.05) # (0.2)
                execution_line = {"symbol":column,"direction":direction,"contract":contract,"order":order}
                execution_log = execution_log.append(execution_line, ignore_index=True)
            except:
                error_line = {"symbol":column,"direction":direction,"contract":"ERROR","order":"ERROR"}
                error_log = error_log.append(error_line, ignore_index=True)
                print(element,"NOT EXECUTED")
        if direction == "HOLD":
            already_traded_line = {"symbol":column,"direction":direction,"contract":"traded","order":"not_applicable"}
            already_traded_log = already_traded_log.append(already_traded_line,ignore_index=True)
    else:
        print(column, " EXCLUDED")
        excluded_line = {"symbol":column}
        excluded_log = excluded_log.append(excluded_line,ignore_index=True)

        
already_traded_log.to_csv(path+"logs/"+current_run+"/"+"no_trade_needed.csv")
#already_traded_log.to_csv("/home/svdr/ibtest/current_run/{}_no_trade_needed.csv").format(pd.datetime.today().strftime('%y%m%d'))
execution_log.to_csv(path+"logs/"+current_run+"/"+"execution_log.csv")
excluded_log.to_csv(path+"logs/"+current_run+"/"+"excluded_log.csv")
error_log.to_csv(path+"logs/"+current_run+"/"+"error_log.csv")
        
