#this is used to simulate minute to minute data

import os.path, csv
from matplotlib import pyplot as plt
import time as t
import datetime as dt


symb = 'XSPA'

# if file exists, use that data, else make the file
if(not os.path.isfile(symb+"-daily.csv")):
  url = 'https://www.alphavantage.co/query'
  params= {
    'apikey' : '', #my key to alpha vantage
    'function' : 'TIME_SERIES_INTRADAY', #daily resolution (open, high, low, close, volume)
    'symbol' : symb, #ticker symbol
    'outputsize' : 'full', #up to 1 trade week of data
    'datatype' : 'csv',
    'interval' : '1min'
  }

  response = requests.request('GET', url, params=params).text
  out = open(symb+'-daily.csv','w')

  out.write(response)
  out.close()

stonkFile = open(symb+'-daily.csv','r')
stonkData = list(csv.reader(stonkFile))
stonkFile.close()

opens = [float(i[1]) for i in stonkData[1:len(stonkData)]][::-1]
times = [dt.datetime.strptime(i[0],"%Y-%m-%d %H:%M:%S") for i in stonkData[1:len(stonkData)]][::-1]

# plt.plot(opens)
# plt.show()



cash = 100
price = 0
sharesHeld = 0
startPortVal = price*sharesHeld+cash
portVal = 0

portVals = []
openPrices = []

time = dt.datetime.now()
openTime = 0

buyPrice = 0
price = 0

buyDnUp = 2
buyTriggered = 0

sellDnUp = 5
sellUpDn = 10
sellTriggered = 0

maxPrice = 0
minPrice = 10000

tradedToday = 0

#we're simulating every minute instead of every day in this one
for i in range(len(times)):
  time = times[i]
  price = opens[i]
  portVal = round(cash+sharesHeld*price,2)
  # t.sleep(0.01)
  
  if(i==0 or time.day-times[i-1].day>0):
    print("\nMarket is open | "+str(time)+" | portVal: "+str(portVal))
    portVals.append(portVal)
    openPrices.append(price)
    openTime = time
    tradedToday = 0
    maxPrice = 0
    minPrice = 10000
  else:
    
    if(not tradedToday):
      if(time.minute==0):
        print("No trades made yet today")
      minPrice = min(minPrice,price)
      maxPrice = max(maxPrice,price)
      # print("price: "+str(price)+", min: "+str(minPrice)+", max: "+str(maxPrice))
      if(sharesHeld==0):
        if(time.minute==0):
          print("no shares held")
        if(price>minPrice*(1+buyDnUp/100)):
          print("buying at "+str(price))
          sharesHeld = int(cash/price)
          cash = cash-sharesHeld*price
          tradedToday = 1
        # else:
          #do nothing?/just wait?
      else:
        if(time.minute==0):
          print(str(sharesHeld)+" shares held")
        if(price<maxPrice*(1-sellUpDn/100)):
          print("selling up at "+str(price))
          cash = cash+sharesHeld*price
          sharesHeld = 0
          tradedToday = 1
        elif(price>minPrice*(1+sellDnUp/100)):
          print("selling down at "+str(price))
          cash = cash+sharesHeld*price
          sharesHeld = 0
          tradedToday = 1
    else:
      if(time.minute==0):
        print("done trading for the day")
    
    
print("\n")
print(portVals)
print(openPrices)
