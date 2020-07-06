import requests, os.path, json
from matplotlib import pyplot as plt

keyFile = open("apikeys.key","r")
apiKeys = json.loads(keyFile.read())
keyFile.close()

def buy(shares, price, bPow, equity):
  bPow = bPow - shares*price
  equity = equity + shares*price
  return [shares, bPow, equity, price]

def sell(shares, price, bPow, equity):
  bPow = bPow + shares*price
  equity = equity - shares*price
  shares = 0
  return [shares, bPow, equity, price]


symb = 'RTTR'

# if file exists, use that data, else make the file
if(not os.path.isfile(symb+".txt")):
  url = 'https://www.alphavantage.co/query'
  params= {
    'apikey' : apiKeys["ALPHAVANTAGEKEY"],
    'function' : 'TIME_SERIES_DAILY', #daily resolution (open, high, low, close, volume)
    'symbol' : symb, #ticker symbol
    'outputsize' : 'full' #upt to 20yrs of data
  }

  response = requests.request('GET', url, params=params).text
  out = open(symb+'.txt','w')

  out.write(response)
  out.close()

stonkFile = open(symb+'.txt','r')
stonkData = json.loads(stonkFile.read())
stonkFile.close()


dateData = stonkData[list(stonkData.keys())[1]] #time series (daily) - index 0=meta data
# oneDate = dateData[list(dateData.keys())[date]] #date to get to
# dateInfo = oneDate[list(oneDate.keys())[info]] #stock info to grab

startDate = 15 #how many days ago? must be >= duration and < length
duration = 14 #how long for term
length = min(duration,len(dateData)-1)
startDate = max(min(startDate,len(dateData)-1),duration)


portfolioGain = 20 #% to increase in timeframe
portfolioLoss = 50 #acceptable loss % during timeframe
sellUp = 9 #sell if stock rises this %
sellDn = 19 #sell if stock falls this %
# days2wait = 1 #minimum number of days to wait until selling after buying
buyPow = [0]*length
equ = [0]*length
portfolio = [0]*length
sharesHeld = 0
buyPrice = 0 #price last bought at
sellPrice = 0 #price last sold at
buyPow[0] = 100 #starting buying power



opens = [0]*length
highs = [0]*length
lows = [0]*length
closes = [0]*length
volumes = [0]*length

for i in range(length):
  oneDate = dateData[list(dateData.keys())[startDate-i]] #date to get to
  opens[i] = float(oneDate[list(oneDate.keys())[0]]) #stock info to grab
  highs[i] = float(oneDate[list(oneDate.keys())[1]])
  lows[i] = float(oneDate[list(oneDate.keys())[2]])
  closes[i] = float(oneDate[list(oneDate.keys())[3]])
  volumes[i] = float(oneDate[list(oneDate.keys())[4]])

buyTime = opens #buy at this point of the day
sellTime = opens #sell at this point of the day

salePrices = [0]*length

for i in range(length):
  equ[i] = sellTime[i]*sharesHeld
  # input(str(i)+" buyPow/buyPrice/sharesHeld: "+str(buyPow[i])+" - "+str(buyTime[i])+" - "+str(sharesHeld)+" - New day")

  portfolio[i] = buyPow[i]+equ[i]
  # input("portfolio/equity: "+str(portfolio[i])+" - "+str(equ[i]))



  # input(str(portfolio[i])+" - "+str((1+portfolioGain/100)*portfolio[0]))
  if(portfolio[i]>=(1+portfolioGain/100)*portfolio[0]):
    [sharesHeld, buyPow[i], equ[i], sellPrice] = sell(sharesHeld,sellTime[i],buyPow[i],equ[i])
    for j in range(i,length):
      portfolio[j] = portfolio[i]
      buyPow[j] = buyPow[i]
      equ[j] = equ[i]
    print(str(i)+" - "+str(portfolioGain)+"%")
    break
  elif(portfolio[i]<=(1-portfolioLoss/100)*portfolio[0] and sharesHeld>0):
    # input(buyPow[i]+sharesHeld*sellTime[i])
    [sharesHeld, buyPow[i], equ[i], sellPrice] = sell(sharesHeld,sellTime[i],buyPow[i],equ[i])
    print(str(i)+" - "+str(sellPrice))


  if(sharesHeld==0 and buyTime[i]>=sellPrice):
    # print(str(i)+" - buy")
    [sharesHeld, buyPow[i], equ[i], buyPrice] = buy(int(buyPow[i]/buyTime[i]), buyTime[i], buyPow[i], equ[i])
    # input(str(i)+" buyPow/buyPrice/sharesHeld: "+str(buyPow[i])+" - "+str(buyTime[i])+" - "+str(sharesHeld))
  elif(sharesHeld>0 and (sellTime[i]>=(1+sellUp/100)*buyPrice or sellTime[i]<=(1-sellDn/100)*buyPrice)):
    # print(str(i)+" - sell "+str(sharesHeld)+" at "+str(sellTime[i]))
    [sharesHeld, buyPow[i], equ[i], null] = sell(sharesHeld,sellTime[i], buyPow[i], equ[i])
  else:
    # print(str(i)+" - hold")
    equ[i] = sellTime[i]*sharesHeld

  for j in range(i,length):
    portfolio[j] = portfolio[i]
    buyPow[j] = buyPow[i]
    equ[j] = equ[i]

  salePrices[i] = sellPrice
  # print(str(sellTime[i])+" - "+str(salePrices[i]))
  # print(buyPow[i])

plt.figure(0)
plt.subplot(311)
plt.title('buyTime/sellTime')
plt.plot(buyTime, "-x")
plt.plot(sellTime, "-.")
plt.plot(salePrices, "-.")
plt.legend(['buyTime','sellTime','salePrice'])
plt.subplot(312)
plt.title('portfolio')
plt.plot(portfolio)
plt.subplot(313)
plt.title('equ/buyPow')
plt.plot(equ)
plt.plot(buyPow)
plt.legend(['equity','buying power'])
# plt.figure(1)
plt.show()
