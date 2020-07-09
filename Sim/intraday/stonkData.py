#this is used to simulate minute to minute data

import os.path, csv
from matplotlib import pyplot as plt

import datetime as dt


symb = 'XSPA'

# if file exists, use that data, else make the file
if(not os.path.isfile(symb+"-daily.csv")):
  url = 'https://www.alphavantage.co/query'
  params= {
    'apikey' : '9G93AVR38ZCBIZMN', #my key to alpha vantage
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

plt.plot(times,opens)
plt.show()



cash = 100
price = 0
sharesHeld = 0
startPortVal = price*sharesHeld+cash
portVal = 0

portVals = []

time = dt.datetime.now()
openTime = 0

buyPrice = 0
price = 0

sellDn = 16
sellUp = 5
sellUpDn = 3
sellFlag = 0
maxPrice = 0

timeFromClose = 300/60
timeSinceStart = 300/60
tradedToday = 0

#we're simulating every minute instead of every day in this one
for i in range(len(times)):
  time = times[i]
  price = opens[i]
  portVal = round(cash+sharesHeld*price,2)
  
  if(i==0 or time.day-times[i-1].day>0):
    print("\nMarket is open | "+str(time)+" | portVal: "+str(portVal))
    portVals.append(portVal)
    openTime = time
    tradedToday = 0
    

  if((time-openTime).seconds/60<=timeSinceStart):
    if(sharesHeld>0):
      print(str(sharesHeld)+" shares held, portVal: "+str(portVal)+" | "+str(time))
      if(price>(1+sellUp/100)*buyPrice and not tradedToday):
        sellFlag = 1
    else:
      print("no shares held. Waiting till near close to buy"+" | "+str(time))
  else:
    if(i>=len(times)-timeFromClose or times[i+int(timeFromClose)].day>times[i].day):
      print("near close | "+str(time))
      if(sharesHeld>0):
        print("shares Held"+" | "+str(time))
      else:
        if(not tradedToday):
          print("no shares held, buying"+" | "+str(time))
          #TODO: insert buyDnUp logic here
          sharesHeld = int(cash/price)
          buyPrice = price
          cash = cash-sharesHeld*price
          tradedToday = 1
  
  if(sellFlag):
    print("Sell Flag set")
    maxPrice = max(maxPrice,price)
    if(price<maxPrice*(1-sellUpDn/100)):
      print("selling at $"+str(price))
      cash = cash+sharesHeld*price
      sharesHeld = 0
      sellFlag = 0
      tradedToday = 1

print("")
print(portVals)