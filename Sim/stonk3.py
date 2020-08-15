import requests, os.path, json
from matplotlib import pyplot as plt
import statistics as stat

keyFile = open("apikeys.key","r")
apiKeys = json.loads(keyFile.read())
keyFile.close()

#function to "buy" shares of stock
def buy(shares, price, bPow, equity):
  bPow = bPow - shares*price
  equity = equity + shares*price
  return [shares, bPow, equity, price]

#function to "sell" shares of stock
def sell(shares, price, bPow, equity):
  bPow = bPow + shares*price
  equity = equity - shares*price
  shares = 0
  return [shares, bPow, equity, price]


symb = 'XSPA' #ticker symbol

a = 270 #how many days ago?
b = 10 #time frame duration in days
s = 6 #step (must be int, 1=highest resolution, increase for more speed)

portfolioGain = 20 # target % to increase in timeframe
portfolioLoss = 25 #acceptable loss % during timeframe
sellUp = 1 #sell if stock rises this % (helps reach the goal easier by breaking into easier chunks)
sellDn = 16 #sell if stock falls this % (depends on your risk tolerance, probably should be higher than sellUp?)

winsZeros = [] #% by which the portfolio has increased/surpassed target %
winTime = [] # number of days it took to win
losesZeros = [] #% by which the portfolio has lost it's value (e.g. if we start w/ $100 and we stop at 60% but it's value is $30, then the loss is 70%)
midsZeros = [] #if the portfolio doesn't reach the goal or fail out, then it goes here

print("\nSimulating "+symb+" data from "+str(a)+" days ago for a duration of "+str(b)+" days, checking every "+str(s)+" day(s)...")
print("Portfolio Gain/loss %: "+str(portfolioGain)+"/"+str(portfolioLoss)+" - Stock gain/loss %: "+str(sellUp)+"/"+str(sellDn))
for c in range(a,b-s,-s): #loop through the days - every day/window will be different, so we need to account for each one and get an average


  # if file exists, use that data, else make the file
  if(not os.path.isfile(symb+".txt")):
    url = 'https://www.alphavantage.co/query'
    params= { # NOTE: the information is also available as CSV which would be more efficient
      'apikey' : apiKeys["ALPHAVANTAGEKEY"],
      'function' : 'TIME_SERIES_DAILY', #daily resolution (open, high, low, close, volume)
      'symbol' : symb, #ticker symbol
      'outputsize' : 'full' #upt to 20yrs of data
    }

    response = requests.request('GET', url, params=params).text #send request and store response
    out = open(symb+'.txt','w') #write to file for later usage
    out.write(response)
    out.close()

  stonkFile = open(symb+'.txt','r') #open the file containing stonk data
  stonkData = json.loads(stonkFile.read()) #read in as json data
  stonkFile.close()


  dateData = stonkData[list(stonkData.keys())[1]] #time series (daily) - index 0=meta data, 1=stock data

  startDate = c #how many days ago? must be >= duration and < length
  duration = b #how long for term
  #clean values

  length = min(duration,len(dateData)-1)
  startDate = max(min(startDate,len(dateData)-1),duration)


  
  #TODO: add days2wait functionality
  # days2wait = 1 #minimum number of days to wait until selling after buying
  buyPow = [0]*length #running info of the account buying power
  equ = [0]*length #running info of the account equity
  portfolio = [0]*length #running info of the portfolio value
  sharesHeld = 0 #sharesHeld at a given day
  buyPrice = 0 #price last bought at
  sellPrice = 0 #price last sold at
  buyPow[0] = 100 #starting buying power in $
  salePrices = [0]*length #this variable is not needed - it is only used as a reference (and graphing) but is a running value of sellPrice

  #init stock data from sheet
  opens = [0]*length
  highs = [0]*length
  lows = [0]*length
  closes = [0]*length
  volumes = [0]*length

  #assign stock data
  for i in range(length):
    oneDate = dateData[list(dateData.keys())[startDate-i]] #date to get to
    opens[i] = float(oneDate[list(oneDate.keys())[0]]) #stock info to grab
    highs[i] = float(oneDate[list(oneDate.keys())[1]])
    lows[i] = float(oneDate[list(oneDate.keys())[2]])
    closes[i] = float(oneDate[list(oneDate.keys())[3]])
    volumes[i] = float(oneDate[list(oneDate.keys())[4]])

  buyTime = closes #buy at this point of the day
  sellTime = opens #sell at this point of the day


  for i in range(length): #for every day in the timeframe we're looking at
    equ[i] = sellTime[i]*sharesHeld #update the equity
    portfolio[i] = buyPow[i]+equ[i] #update the portfolio value

    #if the portfolio value has reached the target gain
    if(portfolio[i]>=(1+portfolioGain/100)*portfolio[0]):
      [sharesHeld, buyPow[i], equ[i], sellPrice] = sell(sharesHeld,sellTime[i],buyPow[i],equ[i]) #sell everything
      #update the running values
      for j in range(i,length):
        portfolio[j] = portfolio[i]
        buyPow[j] = buyPow[i]
        equ[j] = equ[i]
      winTime.append(i)
      winsZeros.append((portfolio[i]-portfolio[0])/portfolio[0]*100)
      midsZeros.append(0)
      losesZeros.append(0)
      break #stop trading for the timeframe
    #else if we've failed out
    elif(portfolio[i]<=(1-portfolioLoss/100)*portfolio[0] and sharesHeld>0):
      [sharesHeld, buyPow[i], equ[i], sellPrice] = sell(sharesHeld,sellTime[i],buyPow[i],equ[i]) #sell all
      if(i==length-1): #if we've reached the end of the timeframe
        losesZeros.append((portfolio[i]-portfolio[0])/portfolio[0]*100)
        winsZeros.append(0)
        midsZeros.append(0)
    #else if we haven't reached the target, but we haven't failed out either by the end of the timeframe
    elif(portfolio[i]>(1-portfolioLoss/100)*portfolio[0] and portfolio[i]<(1+portfolioGain/100)*portfolio[0] and i==length-1):
      midsZeros.append((portfolio[i]-portfolio[0])/portfolio[0]*100)
      winsZeros.append(0)
      losesZeros.append(0)

    #this is an all-or-nothing system, if we don't have shares and it's okay to buy (i.e. we've rebounded from a fail out)
    if(sharesHeld==0 and buyTime[i]>=sellPrice):
      [sharesHeld, buyPow[i], equ[i], buyPrice] = buy(int(buyPow[i]/buyTime[i]) if buyTime[i] else 0, buyTime[i], buyPow[i], equ[i]) #buy as many as we can afford
    #else if we have shares and it's okay to sell (either up or down)
    elif(sharesHeld>0 and (sellTime[i]>=(1+sellUp/100)*buyPrice or sellTime[i]<=(1-sellDn/100)*buyPrice)):
      [sharesHeld, buyPow[i], equ[i], null] = sell(sharesHeld,sellTime[i], buyPow[i], equ[i]) #sell all shares
    #else we didn't buy or sell - so we hold
    else:
      equ[i] = sellTime[i]*sharesHeld

    for j in range(i,length):
      portfolio[j] = portfolio[i]
      buyPow[j] = buyPow[i]
      equ[j] = equ[i]

    salePrices[i] = sellPrice #update the running sales list

wins = [winsZeros[j] for j in [i for i, e in enumerate(winsZeros) if e != 0]]
mids = [midsZeros[j] for j in [i for i, e in enumerate(midsZeros) if e != 0]]
loses = [losesZeros[j] for j in [i for i, e in enumerate(losesZeros) if e != 0]]
winNum = len(wins)
midsNum = len(mids)
loseNum = len(loses)


#print the output data
print("\n\nTotal win: "+str(winNum)+" - Total Mid Ranges: "+str(midsNum)+" - Total Lost: "+str(loseNum))

avgWinTime = round(stat.mean(winTime) if len(winTime) else 0,2)
totalWin = round(winNum/(winNum+midsNum+loseNum)*100,2)
totalMids = round(midsNum/(winNum+midsNum+loseNum)*100,2)
totalLose = round(loseNum/(winNum+midsNum+loseNum)*100,2)
avgWin = round(stat.mean(wins) if winNum else 0,2)
avgMids = round(stat.mean(mids) if midsNum else 0,2)
avgLose = round(stat.mean(loses) if loseNum else 0,2)
weightedAvgWin =round(len(winTime)/len(winTime+loses+mids)*sum(wins)/float(winNum) if float(winNum) else 0,2)
weightedAvgMids = round(midsNum/len(winTime+loses+mids)*sum(mids)/float(midsNum) if float(midsNum) else 0,2)
weightedAvgLose = round(loseNum/len(winTime+loses+mids)*sum(loses)/float(loseNum) if float(loseNum) else 0,2)

winMidQ = sorted(wins)
winMidQ = winMidQ[int(len(winMidQ)/4):int(3*len(winMidQ)/4)]
winMidQ = str(round(min(winMidQ or [0]),2))+":"+str(round(max(winMidQ or [0]),2))
midMidQ = sorted(mids)
midMidQ = midMidQ[int(len(midMidQ)/4):int(3*len(midMidQ)/4)]
midMidQ = str(round(min(midMidQ or [0]),2))+":"+str(round(max(midMidQ or [0]),2))
loseMidQ = sorted(loses)
loseMidQ = loseMidQ[int(len(loseMidQ)/4):int(3*len(loseMidQ or [0])/4)]
loseMidQ = str(round(min(loseMidQ or [0]),2))+":"+str(round(max(loseMidQ or [0]),2))
allMidQ = sorted(wins+mids+loses)
allMidQ = allMidQ[int(len(allMidQ)/4):int(3*len(allMidQ)/4)]
midQavg = round(stat.mean(allMidQ) if len(allMidQ) else 0,2)

print("\nAvg win time (d): "+str(avgWinTime))

print("\nWins (%): "+str(totalWin))
print("Mids (%): "+str(totalMids))
print("Lose (%): "+str(totalLose))

print("\nAvg win Amount (%): "+str(avgWin))
print("Avg mids Amount (%): "+str(avgMids))
print("Avg lose Amount (%): "+str(avgLose))

print("\nWeighted avg win Amount (%): "+str(weightedAvgWin))
print("Weighted avg mids Amount (%): "+str(weightedAvgMids))
print("Weighted avg lose Amount (%): "+str(weightedAvgLose))

print("\nTotal weighted Average (%): "+str(round(weightedAvgWin+weightedAvgLose+weightedAvgMids,2)))
print("All Data Mid Q Avg (%): "+str(midQavg)+"\n")

#need stdDev of wins, loses, mids, and all
winStdDev = round(stat.stdev(wins) if winNum>1 else 0,2)
midsStdDev = round(stat.stdev(mids) if midsNum>1 else 0,2)
loseStdDev = round(stat.stdev(loses) if loseNum>1 else 0,2)

print("Wins/Mids/Loses/All stdDev (%): "+str(winStdDev)+", "+str(midsStdDev)+", "+str(loseStdDev)+"\n")

print("Lowest MidQ: "+str(round(min(allMidQ),2))+", Highest MidQ: "+str(round(max(allMidQ),2)))
print("Win/mids/loses MidQs (%): "+winMidQ+", "+midMidQ+", "+loseMidQ+"\n\n")

'''
plt.subplot(311)
plt.title('wins')
plt.plot(winsZeros)
plt.subplot(312)
plt.title('mids')
plt.plot(midsZeros)
plt.subplot(313)
plt.title('loses')
plt.plot(losesZeros)
plt.show()
'''
'''
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
'''