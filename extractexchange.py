import sys
import pandas as pd
import pickle
import time
import math
from IPython.display import display
import ib_insync
print(ib_insync.__all__)
from ib_insync import *
util.startLoop()

#Connect to IB Gateway
ib = IB()
ib.connect('127.0.0.1', 4000, clientId=3,timeout=100)

excluse = {"UTX","RTN","S","ZAYO","GDI","SBGL","INXN"}

## Long RUN

###Location input
ordine = pd.read_pickle("initial.pickle")
exchange =[]
for element in ordine.columns[1:5]:
    if element not in excluse:
        details = ib.reqContractDetails(Stock(element,"SMART","USD"))
#         str(details).split("primaryExchange='")[1].split("'")[0]
        print(element)
        a = {"Stock":element, "primaryExchange":str(details).split("primaryExchange='")[1].split("'")[0]}
        exchange.append(a)
        time.sleep(0.05)

ExchangeData = pd.DataFrame(exchange)
ExchangeData.index = ExchangeData["Stock"]

####Location output
ExchangeData.to_csv("exchange.csv", index=False)

# ExchangeData = pd.DataFrame(exchange)
# ExchangeData.index = corectexchange["Stock"]
# ExchangeData.to_csv("/home/scadir/MarketData/exchange.csv", index=False)
# ExchangeData = pd.read_csv("/home/scadir/MarketData/exchange.csv")
# ExchangeData.loc["AMZN"]["primaryExchange"]