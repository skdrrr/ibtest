import pandas as pd
import numpy as np
import copy
import pickle
import time
import matplotlib.pyplot as plt
from IPython.display import display
from datetime import datetime
import datetime as dt
import ib_insync
print(ib_insync.__all__)

from ib_insync import *
#Andy - not using Jupyter
util.startLoop()

#Andy- this is the default account, setting so that orders can be allocated to it.
# acc_num = 'DU1870227'
# acc_num = ''

#Connect to IB Gateway
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1,timeout=100)

##DownloadMarketData
ib.reqMarketDataType(3)
excluse=[]
universe = pickle.load(open('/home/sevder/ibtest/sp500univ.pickle', 'rb'))
SPExchangeData = pd.read_csv("SP500data.csv")
SPExchangeData.index= SPExchangeData["Stock"]
### Simple live data
# stocks = 
MyDataLine=pd.DataFrame()
for element in universe:
    time.sleep(0.05)
    if str(element) not in excluse:
        print(element)
        contract = Stock(element.replace("."," "), 'SMART', 'USD', primaryExchange=SPExchangeData.loc[element]["primaryExchange"])
        try:
            m_data = ib.reqMktData(contract)
            while m_data.last != m_data.last: ib.sleep(0.01) #Wait until data is in. 
            ib.cancelMktData(contract)
            high = m_data.high
            low = m_data.low
            last = m_data.last
            volume = m_data.volume
            line = {"symbol":element,"high":high,"low":low,"last":last,"volume":volume}
        except:
            print("ERROR",element)
        MyDataLine = MyDataLine.append(line,ignore_index=True)
    else:
        print(element,"EXCLUS")
MyDataLine.to_csv("marketdata.csv")
#     ib.sleep(0.5)