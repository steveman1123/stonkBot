#determine what the best penny stocks to buy are based on the algorithm
#TODO: place stock data files into separate folder to keep main directory clean (and not accidentally remove the keys file)

import requests, json, re, os.path, time, operator
from pandas import read_html
from datetime import datetime as dt
import statistics as stat

keyFile = open("apikeys.key","r")
apiKeys = json.loads(keyFile.read())
keyFile.close()

#get list of common penny stocks under $price and sorted by gainers (up) or losers (down)
def getPennies(price=1,updown="up"):
  url = 'https://stocksunder1.org/'
  html = requests.post(url, params={"price":price,"volume":0,"updown":updown}).content
  tableList = read_html(html)
  # print(tableList[5][1:][0])
  # symList = tableList[5][0:]['Symbol']
  symList = tableList[5][1:][0] #this keeps changing (possibly intentionally)
  symList = [e.replace(' predictions','') for e in symList]
#  print(tableList[5][0:]['Symbol'])
  return symList


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


def stonkData(symb):
  a = 270 #how many days ago?
  b = 10 #time frame duration in days
  s = 1 #step (must be int, 1=highest resolution, increase for more speed)

  wins = [] #% by which the portfolio has increased/surpassed target %
  winTime = [] # number of days it took to win
  loses = [] #% by which the portfolio has lost it's value (e.g. if we start w/ $100 and we stop at 60% but it's value is $30, then the loss is 70%)
  mids = [] #if the portfolio doesn't reach the goal or fail out, then it goes here

  # print("\nSimulating "+symb+" data from "+str(a)+" days ago for a duration of "+str(b)+" days, checking every "+str(s)+" day(s)...")

  # if file exists, use that data, else make the file
  print(symb)
  if(not os.path.isfile(symb+".txt")):
    # url = 'https://www.alphavantage.co/query'
    url = apiKeys["ALPHAVANTAGEURL"]
    params= { # NOTE: the information is also available as CSV which would be more efficient
      'apikey' : apiKeys["ALPHAVANTAGEKEY"],
      'function' : 'TIME_SERIES_DAILY', #daily resolution (open, high, low, close, volume)
      'symbol' : symb, #ticker symbol
      'outputsize' : 'full' #upt to 20yrs of data
    }
    response = requests.request('GET', url, params=params).text #send request and store response
    time.sleep(19) #max requests of 5 per minute for free alphavantage account, delay to stay under that limit

    out = open(symb+'.txt','w') #write to file for later usage
    out.write(response)
    out.close()

  stonkFile = open(symb+'.txt','r') #open the file containing stonk data
  stonkData = json.loads(stonkFile.read()) #read in as json data
  stonkFile.close()

  dateData = stonkData[list(stonkData.keys())[1]] #time series (daily) - index 0=meta data, 1=stock data
  length = min(b,len(dateData)-1) #how long for term
  a = min(a, len(dateData)-1) #minimize the inputs as needed
  b = min(b, len(dateData)-1)
  s = min(s, len(dateData)-1)

  for c in range(a,b-s,-s): #loop through the days - every day/window will be different, so we need to account for each one and get an average

    startDate = min(c,len(dateData)) #how many days ago? must be >= duration and < length
    startDate = max(min(startDate,len(dateData)-1),length)

    portfolioGain = 20 # target % to increase in timeframe
    portfolioLoss = 25 #acceptable loss % during timeframe
    sellUp = 5 #sell if stock rises this % (helps reach the goal easier by breaking into easier chunks)
    sellDn = 16 #sell if stock falls this % (depends on your risk tolerance, probably should be higher than sellUp?)
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
        wins.append((portfolio[i]-portfolio[0])/portfolio[0]*100)
        break #stop trading for the timeframe
      #else if we've failed out
      elif(portfolio[i]<=(1-portfolioLoss/100)*portfolio[0] and sharesHeld>0):
        [sharesHeld, buyPow[i], equ[i], sellPrice] = sell(sharesHeld,sellTime[i],buyPow[i],equ[i]) #sell all
        if(i==length-1): #if we've reached the end of the timeframe
          loses.append((portfolio[i]-portfolio[0])/portfolio[0]*100)
      #else if we haven't reached the target, but we haven't failed out either by the end of the timeframe
      elif(portfolio[i]>(1-portfolioLoss/100)*portfolio[0] and portfolio[i]<(1+portfolioGain/100)*portfolio[0] and i==length-1):
        mids.append((portfolio[i]-portfolio[0])/portfolio[0]*100)

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


  #print the output data

  avgWinTime = round(stat.mean(winTime) if len(winTime) else 0,2)
  totalWin = round(len(wins)/len(wins+loses+mids)*100,2)
  totalMids = round(len(mids)/len(wins+loses+mids)*100,2)
  totalLose = round(len(loses)/len(wins+loses+mids)*100,2)
  avgWin = round(stat.mean(wins) if len(wins) else 0,2)
  avgMids = round(stat.mean(mids) if len(mids) else 0,2)
  avgLose = round(stat.mean(loses) if len(loses) else 0,2)
  weightedAvgWin =round(len(wins)/len(wins+loses+mids)*sum(wins)/float(len(wins)) if float(len(wins)) else 0,2)
  weightedAvgMids = round(len(mids)/len(wins+loses+mids)*sum(mids)/float(len(mids)) if float(len(mids)) else 0,2)
  weightedAvgLose = round(len(loses)/len(wins+loses+mids)*sum(loses)/float(len(loses)) if float(len(loses)) else 0,2)
  greaterThan0 = len([i for i in wins+mids+loses if i>0])


  winMidQ = sorted(wins)
  winMidQ = winMidQ[int(len(winMidQ)/4):int(3*len(winMidQ)/4)] or [0]
  winQ1 = round(winMidQ[0],2)
  winQ3 = round(winMidQ[len(winMidQ)-1],2)

  midMidQ = sorted(mids)
  midMidQ = midMidQ[int(len(midMidQ)/4):int(3*len(midMidQ)/4)] or [0]
  midQ1 = round(midMidQ[0],2)
  midQ3 = round(midMidQ[len(midMidQ)-1],2)

  loseMidQ = sorted(loses)
  loseMidQ = loseMidQ[int(len(loseMidQ)/4):int(3*len(loseMidQ)/4)] or [0]
  loseQ1 = round(loseMidQ[0],2)
  loseQ3 = round(loseMidQ[len(loseMidQ)-1],2)
  allMidQ = sorted(wins+mids+loses)
  allMidQ = allMidQ[int(len(allMidQ)/4):int(3*len(allMidQ)/4)]
  midQavg = round(stat.mean(allMidQ) if len(allMidQ) else 0,2)



  outs = {}
  outs["win"] = str(len(wins)) # total won
  outs["mids"] = str(len(mids)) #total in the middle
  outs["lose"] = str(len(loses)) #total lost

  outs["winPerc"] = str(totalWin) # % of total simulated won
  outs["midPerc"] = str(totalMids) # % of total simulated in the middle
  outs["losePerc"] = str(totalLose) # % of total simulated lost

  outs["avgWinTime"] = str(avgWinTime) #average days to win

  outs["avgWinAmt"] = str(avgWin) #avg % change of portfolio of the wins
  outs["avgMidsAmt"] = str(avgMids) #avg % change of portfolio of the middles
  outs["avgLoseAmt"] = str(avgLose) #avg % change of portfolio of the loses

  outs["weightedAvgWin"] = str(weightedAvgWin) #weighted average portfolio change of the wins
  outs["weightedAvgMids"] = str(weightedAvgMids) #weighted average portfolio change of the mids
  outs["weightedAvgLose"] = str(weightedAvgLose) #weighted average portfolio change of the Loses

  outs["totalWeightedAvg"] = str(round(weightedAvgWin+weightedAvgLose+weightedAvgMids,2)) #sum of the weighted averages
  outs["totalAvg"] = str(round(stat.mean(wins+mids+loses) if len(wins+mids+loses) else 0,2))
  outs["midQavg"] = str(midQavg)


  #these are useful, but can easily mislead because the data probably aren't normally distributed
  # outs["winStdDev"] = round(stat.stdev(wins) if len(wins)>1 else 0,2)
  # outs["midsStdDev"] = round(stat.stdev(mids) if len(mids)>1 else 0,2)
  # outs["loseStdDev"] = round(stat.stdev(loses) if len(loses)>1 else 0,2)

  outs["winQ1"] = str(winQ1)
  outs["winQ3"] = str(winQ3)
  outs["winMidQ"] = str(round(winQ3-winQ1,2))
  outs["midQ1"] = str(midQ1)
  outs["midQ3"] = str(midQ3)
  outs["midMidQ"] = str(round(midQ3-midQ1,2))
  outs["loseQ1"] = str(loseQ1)
  outs["loseQ3"] = str(loseQ3)
  outs["loseMidQ"] = str(round(loseQ3-loseQ1,2))
  outs["greaterThan0"] = greaterThan0

  return outs



stonks = {}
if(not os.path.isfile("allStonks.txt")):
  out = open('allStonks.txt','w') #write to file for later usage
  for i,s in enumerate(getPennies()):
    stonks[s] = stonkData(s)
  out.write(json.dumps(stonks))
  out.close()

else:
  stonkFile = open('allStonks.txt','r') #open the file containing stonk data
  stonks = json.loads(stonkFile.read()) #read in as json data
  stonkFile.close()

byWeightedAvg = sorted(list(stonks.keys()), key=lambda k: float(stonks[k]["totalWeightedAvg"]),reverse=True)
byMidQavg = sorted(list(stonks.keys()), key=lambda k: float(stonks[k]["midQavg"]),reverse=True)
byWin = sorted(list(stonks.keys()), key=lambda k: float(stonks[k]["win"]),reverse=True)
byWinMid = sorted(list(stonks.keys()), key=lambda k: float(stonks[k]["winMidQ"]))
byWinTime = sorted(list(stonks.keys()), key=lambda k: float(stonks[k]["avgWinTime"]))

# print("\nWeighted Avg\tWins\t\tWin Mid Q\tWin Time")
# for i in range(len(stonks)):
#   print(byWeightedAvg[i]+"\t\t"+byWin[i]+"\t\t"+byWinMid[i]+"\t\t"+byWinTime[i])
# print("\n")

weightedAvgWeight = .8
midQavgWeight = 1
winWeight = .7
winMidWeight = .5
winTimeWeight = .2

scores = {}
for e in stonks:
  scores[e] = int(midQavgWeight*byMidQavg.index(e)+weightedAvgWeight*byWeightedAvg.index(e)+winWeight*byWin.index(e)+winMidWeight*byWinMid.index(e)+winTimeWeight*byWinTime.index(e))

scoreList = sorted(list(scores.keys()), key=lambda k: float(scores[k]))

print("\nThe lower the score, the better the stock")

print("\nSymb\tScore\tWin %\twQ1\twQ3\t\tMid %\tmQ1\tmQ3\t\tLose %\tlQ1\tlQ3\t\tTotal Avg Rtn\tMid Q Avg Rtn\tAvg Win Time\tn")
for e in scoreList:
  print(e+"\t"+str(scores[e])+"\t"+stonks[e]["winPerc"]+"\t"+stonks[e]["winQ1"]+"\t"+stonks[e]["winQ3"]+"\t\t"+stonks[e]["midPerc"]+"\t"+stonks[e]["midQ1"]+"\t"+stonks[e]["midQ3"]+"\t\t"+stonks[e]["losePerc"]+"\t"+stonks[e]["loseQ1"]+"\t"+stonks[e]["loseQ3"]+"\t\t"+stonks[e]["totalWeightedAvg"]+"\t\t"+stonks[e]["midQavg"]+"\t\t"+stonks[e]["avgWinTime"]+"\t\t"+str(int(stonks[e]["win"])+int(stonks[e]["mids"])+int(stonks[e]["lose"])))
