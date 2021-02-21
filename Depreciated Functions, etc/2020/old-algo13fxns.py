from matplotlib import pyplot as plt
#depreciated functions from algo13.py that are no longer used

#get list of common penny stocks under $price and sorted by gainers (up) or losers (down) - source: stockunder1.org
def getPennies(price=1,updown="up"):
  url = 'https://stocksunder1.org/nasdaq-penny-stocks/'
  # url = 'https://stocksunder1.org/nasdaq-stocks-under-1/' #alt url that can be used
  while True:
    try:
      html = requests.post(url, params={"price":price,"volume":0,"updown":updown}).content
      break
    except Exception:
      print("No connection, or other error encountered. Trying again...")
      time.sleep(3)
      continue

  tableList = read_html(html)
  # print(tableList)
  try:
    symList = tableList[5][0:]['Symbol']
  except Exception:
    symList = tableList[5][1:][0] #this keeps changing (possibly intentionally - possibly due to switching btw windows and linux?)
  
  symList = [re.sub(r'\W+','',e.replace(' predictions','')) for e in symList] #strip "predictions" and any non alphanumerics
  # print(tableList[5][0:]['Symbol'])
  return symList

#not really OBE, but not really used
#gets a list of volatile stocks using criteria outlined here: https://stocksunder1.org/how-to-trade-penny-stocks/
def getVolatile(lbound=0.8, ubound=5,minPercChange=30, minVol=8000000):
  url = 'https://www.marketwatch.com/tools/stockresearch/screener/results.asp'
  params = {"submit":"Screen",
            "Symbol":"true",
            "ChangePct":"true",
            "CompanyName":"false",
            "Volume":"true",
            "Price":"true",
            "Change":"false",
            "SortyBy":"Symbol",
            "SortDirection":"Ascending",
            "ResultsPerPage":"OneHundred",
            "TradesShareEnable":"true",
            "TradesShareMin":str(lbound),
            "TradesShareMax":str(ubound),
            "PriceDirEnable":"true",
            "PriceDir":"Up",
            "PriceDirPct":str(minPercChange),
            "TradeVolEnable":"true",
            "TradeVolMin":str(minVol),
            "TradeVolMax":"",
            "Exchange":"NASDAQ",
            "IndustryEnable":"false",
            "MoreInfo":"false"}
  while True:
    try:
      html = requests.post(url, params=params).content
      break
    except Exception:
      print("No connection, or other error encountered. Trying again...")
      time.sleep(3)
      continue

  tableList = read_html(html)
  symList = tableList[0].transpose().to_dict() #transpose for organization, dictionary to have all wanted data
  return symList

#function to sim stocks that have already peaked and return the good ones - OBE
def simPast(symList):
  '''
  the idea is to look at what happens in the following days after a big jump and trade accordingly
  '''
  global apiKeys
  global someSettings
  
  #generate data files for each stock
  print("Getting stock data...")
  winners = {}
  for i,symb in enumerate(symList):
    print("("+str(i+1)+"/"+str(len(symList))+") "+symb)
    if(not os.path.isfile(stockDir+symb+".txt")):
      url = apiKeys["ALPHAVANTAGEURL"]
      params= { # NOTE: the information is also available as CSV which would be more efficient
        'apikey' : apiKeys["ALPHAVANTAGEKEY"],
        'function' : 'TIME_SERIES_DAILY', #daily resolution (open, high, low, close, volume)
        'symbol' : symb, #ticker symbol
        'outputsize' : 'full' #up to 20yrs of data
      }
      while True:
        try:
          response = requests.request('GET', url, params=params).text #send request and store response
          stonkData = json.loads(response) #read in as json data
          dateData = stonkData[list(stonkData.keys())[1]] #time series (daily) - index 0=meta data, 1=stock data
          break
        except Exception:
          print("No connection, or other error encountered. Trying again...")
          time.sleep(3)
          continue
      if(i<len(symList)): #only delay if it's not the last one
        time.sleep(12.5) #max requests of 5 per minute for free alphavantage account, delay to stay under that limit
  
      out = open(stockDir+symb+'.txt','w') #write to file for later usage
      out.write(response)
      out.close()
      
    
    #gather info about single stock
    stonkFile = open(stockDir+symb+'.txt','r') #open the file containing stonk data
    stonkData = json.loads(stonkFile.read()) #read in as json data
    stonkFile.close()
  
    dateData = stonkData[list(stonkData.keys())[1]] #time series (daily) - index 0=meta data, 1=stock data
    period = min(someSettings['periodLength'],len(dateData)-1) #how long for period
    
    dates = [e for e in dateData]
    lows = [max(float(dateData[e]['3. low']),0.0000001) for e in dateData] #must not be 0 due to being a devisor
    highs = [float(dateData[e]['2. high']) for e in dateData]
    opens = [max(float(dateData[e]['1. open']),0.0000001) for e in dateData] #must not be 0 due to being a devisor
    closes = [float(dateData[e]['4. close']) for e in dateData]
    volumes = [float(dateData[e]['5. volume']) for e in dateData]
    volatility = [(highs[i]-lows[i])/(lows[i]) for i in range(len(lows))] #this isn't the real volatility measurement, but it's good enough for me - vol = 1 means price doubled, 0 = no change
    delDayRatio = [(closes[i]-opens[i])/(closes[i+1]) for i in range(len(closes)-1)] #this is the change over the day normalized to the opening price
    
    #start sim here
    
    startDate = someSettings['periodLength']-1 #here we're looking for the most recent big jump - init at least 1 period length ago
    '''
    the following conditions should be true when asking if the date should be skipped (in order as they appear in the while statement):
    make sure we're in range
    arbirary volatility of the day - higher= more volatility in a given day (volImpulse is minimum volatility to have)
    look only for positive daily changes
    the difference between today's (startDate-1) change and yesterdays must be sufficiently large (and negative) to constitute underdamped oscilation - at least 1/2 of original
    '''
    while startDate<len(volatility)-2 and\
          (volatility[startDate]<someSettings['volImpulse'] or\
           (delDayRatio[startDate]<.25 or\
            (delDayRatio[startDate-1]-delDayRatio[startDate])>-.75\
           )\
          ):
      startDate += 1
      
    # start data analysis here
    
    if(startDate<len(volatility)-2 and startDate<90 and closes[startDate-1]>closes[startDate]): #only show info if the jump happened in the past year/few months (ignore if it reaches the end)
      for i in range(startDate,startDate-someSettings['periodLength'],-1):
        print(dates[i]+" - "+str(round(volatility[i],2))+" - "+str(opens[i])+" - "+str(round(delDayRatio[i]-delDayRatio[i+1],2)))
        
      #symbols that show up in the graph/meet the conditions
      winners[symb] = {"volatility":volatility[startDate],
                       "startDelDayRatio":delDayRatio[startDate]-delDayRatio[startDate+1],
                       "nextDelDayRatio":delDayRatio[startDate-1]-delDayRatio[startDate],
                       "diff":(delDayRatio[startDate]-delDayRatio[startDate+1])-(delDayRatio[startDate-1]-delDayRatio[startDate])}
      
      # plt.figure(1)
      # plt.subplot(211)
      # plt.plot([delDayRatio[i]-delDayRatio[i+1] for i in range(startDate,startDate-someSettings['periodLength'],-1)], label=symb)
      # plt.title("today-yesterday delDayRatio ((close-open)/open)")
      # plt.legend(loc='right')
      # 
      # plt.subplot(212)
      # plt.plot([volatility[i] for i in range(startDate,startDate-someSettings['periodLength'],-1)], label=symb)
      # plt.title("volatility ((high-low)/low)")
      # plt.legend(loc='right')
      
      plt.figure(2)
      # plt.plot([delDayRatio[i]-delDayRatio[i+1] for i in range(startDate,startDate-someSettings['periodLength'],-1)], label=symb)
      plt.plot([closes[i]/closes[startDate] for i in range(startDate+80, startDate-someSettings['periodLength'],-1)], label=symb)
      # plt.title("today-yesterday delDayRatio ((close-open)/close-1)")
      plt.legend(loc='right')

  # print('\n\n')
  
  sortedSyms = sorted(list(winners.keys()), key=lambda k: float(winners[k]['diff']))[::-1]
  # print(sortedSyms)
  plt.show()
 
  return sortedSyms

# return if a stock should be put on a watchlist - OBE
# https://stocksunder1.org/how-to-trade-penny-stocks/
def presentList(symList):
  global apiKeys
  global someSettings
  validBuys = {}
  #TODO: check date, market last open date, etc - how many trading days since initial bump
  for i,symb in enumerate(symList):
    print("("+str(i+1)+"/"+str(len(symList))+") "+symb)
    if(not os.path.isfile(stockDir+symb+".txt")):
      url = apiKeys["ALPHAVANTAGEURL"]
      params= { # NOTE: the information is also available as CSV which would be more efficient
        'apikey' : apiKeys["ALPHAVANTAGEKEY"],
        'function' : 'TIME_SERIES_DAILY', #daily resolution (open, high, low, close, volume)
        'symbol' : symb, #ticker symbol
        'outputsize' : 'full' #up to 20yrs of data
      }
      while True:
        try:
          response = requests.request('GET', url, params=params).text #send request and store response
          break
        except Exception:
          print("No connection, or other error encountered. Trying again...")
          time.sleep(3)
          continue

      if(len(symList)>=5):
        time.sleep(11) #max requests of 5 per minute for free alphavantage account, delay to stay under that limit
  
      out = open(stockDir+symb+'.txt','w') #write to file for later usage
      out.write(response)
      out.close()
    
    #calc price % diff over past 20 days (current price/price of day n) - current must be >= 80% for any
    #calc volume % diff over average past some days (~60 days?) - must be sufficiently higher (~300% higher?)
    #TODO: clean up the indexing in here - this looks gross and I think it can be improved
    dateData = json.loads(open(stockDir+symb+".txt","r").read()) #dictionary of all data returned from AV
    dateData = dateData[list(dateData)[1]] #dict without the metadata - just the date data
    
    volAvgDays = min(60,len(list(dateData))) #arbitrary number to avg volumes over
    checkPriceDays = 20 #check if the price jumped substantially over the last __ days
    checkPriceAmt = 1.7 #check if the price jumped by this amount in the above days (% - i.e 1.5 = 150%)
    volGain = 3 #check if the volume increased by this amout (i.e. 3 = 300% or 3x)
    
    avgVol = sum([int(dateData[list(dateData)[i]]['5. volume']) for i in range(volAvgDays)])/volAvgDays #avg of volumes over a few days
    
    lastVol = int(dateData[list(dateData)[0]]['5. volume']) #the latest volume
    lastPrice = float(dateData[list(dateData)[0]]['2. high']) #the latest highest price

    validBuys[symb] = "Do Not Watch"
    if(lastVol/avgVol>volGain): #much larger than normal volume
      dayPrice = lastPrice
      i = 1
      while(i<=checkPriceDays and lastPrice/dayPrice<checkPriceAmt): #
        dayPrice = float(dateData[list(dateData)[i]]['2. high'])
        # print(str(i)+" - "+str(lastPrice/dayPrice))
        i += 1
      if(lastPrice/dayPrice>=checkPriceAmt):
        validBuys[symb] = "Watch"
    
      
    
    
    #save ?
    # f = open(stockDir+symb+"--"+str(dt.date.today())+".txt","w")
    # f.write(
  return validBuys #return a dict of whether a stock is a valid purchase or not

#basically do what presentList is doing, but like, better... - OBE
def getGainers_old(symList):
  global apiKeys
  global someSettings
  validBuys = {}
  #TODO: check date, market last open date, etc - how many trading days since initial bump
  for i,symb in enumerate(symList):
    print("("+str(i+1)+"/"+str(len(symList))+") "+symb)
    if(os.path.isfile(stockDir+symb+".txt")): #if a file exists
      dateData = json.loads(open(stockDir+symb+".txt","r").read()) #read it
      
      if((dt.date.today()-dt.datetime.fromtimestamp(os.stat(stockDir+symb+".txt").st_mtime).date()).days>0): #if the last time it was pulled was more than __ days ago
        os.remove(stockDir+symb+".txt") #delete it
      
        
    if(not os.path.isfile(stockDir+symb+".txt")): #if the file doesn't exist
      url = apiKeys["ALPHAVANTAGEURL"]
      params= { # NOTE: the information is also available as CSV which would be more efficient
        'apikey' : apiKeys["ALPHAVANTAGEKEY"],
        'function' : 'TIME_SERIES_DAILY', #daily resolution (open, high, low, close, volume)
        'symbol' : symb, #ticker symbol
        'outputsize' : 'compact' #compact=last 100 days, full=up to 20 years
      }
      while True:
        try:
          response = requests.request('GET', url, params=params).text #send request and store response
          dateData = json.loads(response) #dictionary of all data returned from AV
          dateData = dateData[list(dateData)[1]] #dict without the metadata - just the date data
          break
        except Exception:
          print("No connection, or other error encountered. Trying again...")
          time.sleep(3)
          continue
      out = open(stockDir+symb+'.txt','w') #write to file for later usage
      out.write(response)
      out.close()
    
      if(len(symList)>=5 and i<len(symList)-1):
        time.sleep(12.5) #max requests of 5 per minute for free alphavantage account, delay to stay under that limit
  
    #calc price % diff over past 20 days (current price/price of day n) - current must be >= 80% for any
    #calc volume % diff over average past some days (~60 days?) - must be sufficiently higher (~300% higher?)
    #TODO: clean up the indexing in here - this looks gross and I think it can be improved
    dateData = json.loads(open(stockDir+symb+".txt","r").read()) #dictionary of all data returned from AV
    dateData = dateData[list(dateData)[1]] #dict without the metadata - just the date data
    
    days2wait4fall = 3 #wait for stock price to fall for this many days
    startDate = days2wait4fall+1 #add 1 to account for the jump day itself
    days2look = 25 #look back this far for a jump
    firstJumpAmt = 1.3 #stock first must jump by this amount (1.3=130% over 1 day)
    sellUp = 1.25 #% to sell up at
    sellDn = 0.5 #% to sell dn at
    
    while(float(dateData[list(dateData)[startDate]]['4. close'])/float(dateData[list(dateData)[startDate+1]]['4. close'])<firstJumpAmt and startDate<min(days2look,len(dateData)-2)):
      startDate += 1
    #we know the date of the initial jump (startDate)
    
    if(float(dateData[list(dateData)[startDate]]['4. close'])/float(dateData[list(dateData)[startDate+1]]['4. close'])>=firstJumpAmt):
      #make sure that the jump happened in the time frame rather than too long ago
      volAvgDays = min(60,len(list(dateData))) #arbitrary number to avg volumes over
      checkPriceDays = 20 #check if the price jumped substantially over the last __ days
      checkPriceAmt = 1.7 #check if the price jumped by this amount in the above days (% - i.e 1.5 = 150%)
      volGain = 3 #check if the volume increased by this amout (i.e. 3 = 300% or 3x, 0.5 = 50% or 0.5x)
      volLoss = .5 #check if the volume decreases by this amount
      priceDrop = .4 #price should drop this far when the volume drops
      
      avgVol = sum([int(dateData[list(dateData)[i]]['5. volume']) for i in range(startDate,min(startDate+volAvgDays,len(dateData)))])/volAvgDays #avg of volumes over a few days
      
      lastVol = int(dateData[list(dateData)[startDate]]['5. volume']) #the latest volume
      lastPrice = float(dateData[list(dateData)[startDate]]['2. high']) #the latest highest price
  
      if(lastVol/avgVol>volGain): #much larger than normal volume
        #volume had to have gained
        #if the next day's price has fallen significantly and the volume has also fallen
        if(float(dateData[list(dateData)[startDate-days2wait4fall]]['2. high'])/lastPrice-1<priceDrop and int(dateData[list(dateData)[startDate-days2wait4fall]]['5. volume'])<=lastVol*volLoss):
          #the jump happened, the volume gained, the next day's price and volumes have fallen
          dayPrice = lastPrice
          i = 1 #magic number? TODO: figure out exactly what this counter is doing
          # check within the the last few days, check the price has risen compared to the past some days, and we're within the valid timeframe
          while(i<=checkPriceDays and lastPrice/dayPrice<checkPriceAmt and startDate+i<len(dateData)):
            dayPrice = float(dateData[list(dateData)[startDate+i]]['2. high'])
            i += 1
          
          if(lastPrice/dayPrice>=checkPriceAmt):
            #the price jumped compared to both the previous day and to the past few days, the volume gained, and the price and the volume both fell
              
            #check to see if we missed the next jump (where we want to strike)
            missedJump = False
            for e in range(0,startDate):
              diff = float(dateData[list(dateData)[e]]['4. close'])/float(dateData[list(dateData)[e+1]]['4. close'])
              if(diff>=sellUp):
                missedJump = True
            if(not missedJump):
              validBuys[symb] = list(dateData)[startDate] #return the stock and the date it initially jumped
          
  return validBuys #return a dict of valid stocks and the date of their latest jump




#whether to buy a stock or not
def check2buy(latestTrades, minPortVal, reducedCash, reducedBuy, lowCash, lowBuy, minCash):
  '''
    original buy/sell logic:
  - if cash<some amt (reduced cash mode) 
    - buy max of 10 unique from list
  - else (standard mode) buy as many as we can off the list generated by the sim
  - if cash<10 (low cash mode)
    - buy max of 5 unique from list
  - if portVal<5 (bottom out mode)
    - error, sell all and stop trading
  - stop loss at ~60%
  - limit gain at ~25%
  '''
  
  '''
  reducedCash = 100 #enter reduced cash mode if portfolio reaches under this amount
  reducedBuy = 10 #buy this many unique stocks if in reduced cash mode
  lowCash = 10 #enter low cash mode if portfolio reaches under this amount
  lowBuy = 5 #buy this many unique stocks if in low cash mode
  minCash = 1 #buy until this amt is left in buying power/cash balance
  '''
  
  global gainers
  acct = a.getAcct()
  gainers = [e for e in gainers if e not in [t.getName() for t in threading.enumerate()]] #remove stocks currently trying to be sold
  portVal = float(acct['portfolio_value'])


  buyPow = float(acct['buying_power'])
  '''
  add something like this:
  if(buyPow >= maxPortVal):
    buyPow = buyPow - cash2Hold
  where maxPortVal is ~20k and cash2Hold is ~1k
  '''
  
  if(buyPow>reducedCash): #in normal operating mode
    print("Normal Operation Mode. Available Buying Power: $"+str(buyPow))
    #div cash over all gainers
    for e in gainers:
      if(a.isAlpacaTradable(e)):
        curPrice = a.getPrice(e)
        if(curPrice>0 and reducedBuy>0): #don't bother buying if the stock is invalid (no div0)
          shares2buy = int((buyPow/reducedBuy)/curPrice)
          try:
            lastTradeDate = a.o.dt.datetime.strptime(latestTrades[gainers[i]][0],'%Y-%m-%d').date()
            lastTradeType = latestTrades[gainers[i]][1]
          except Exception:
            lastTradeDate = a.o.dt.date.today()-a.o.dt.timedelta(1)
            lastTradeType = "NA"
            
          #check to make sure that we're not buying/selling on the same day
          if(shares2buy>0 and (lastTradeDate<a.o.dt.date.today() or lastTradeType=="NA" or lastTradeType=="buy")):
            print(a.createOrder("buy",shares2buy,e,"market","day"))
            latestTrades[e] = [str(a.o.dt.date.today()), "buy"]
            f = open("../stockStuff/latestTrades.json","w")
            f.write(a.o.json.dumps(latestTrades, indent=2))
            f.close()
  else:
    if(buyPow>lowCash): #in reduced cash mode
      print("Reduced Cash Mode. Available Buying Power: $"+str(buyPow))
      #div cash over $reducedBuy stocks
      for i in range(min(reducedBuy,len(gainers))):
        if(a.isAlpacaTradable(gainers[i])): #just skip it if it can't be traded
          curPrice = a.getPrice(gainers[i])
          if(curPrice>0 and reducedBuy>0): #don't bother buying if the stock is invalid
            shares2buy = int((buyPow/reducedBuy)/curPrice)
            try:
              lastTradeDate = a.o.dt.datetime.strptime(latestTrades[gainers[i]][0],'%Y-%m-%d').date()
              lastTradeType = latestTrades[gainers[i]][1]
            except Exception:
              lastTradeDate = a.o.dt.date.today()-a.o.dt.timedelta(1)
              lastTradeType = "NA"
              
            if(shares2buy>0 and (lastTradeDate<a.o.dt.date.today() or lastTradeType=="NA" or lastTradeType=="buy")):
              print(a.createOrder("buy",shares2buy,gainers[i],"market","day"))
              latestTrades[gainers[i]] = [str(a.o.dt.date.today()), "buy"]
              f = open("../stockStuff/latestTrades.json","w")
              f.write(a.o.json.dumps(latestTrades, indent=2))
              f.close()
    else:
      if(buyPow>minCash): #in low cash mode
        print("Low Cash Mode. Available Buying Power: $"+str(buyPow))
        #div cash over $lowBuy cheapest stocks in list
        for i in range(min(lowBuy,len(gainers))):
          if(a.isAlpacaTradable(gainers[i])): #just skip it if it can't be traded
            curPrice = a.getPrice(gainers[i])
            if(curPrice>0): #don't bother buying if the stock is invalid
              shares2buy = int((buyPow/reducedBuy)/curPrice)
              try:
                lastTradeDate = a.o.dt.datetime.strptime(latestTrades[gainers[i]][0],'%Y-%m-%d').date()
                lastTradeType = latestTrades[gainers[i]][1]
              except Exception:
                lastTradeDate = a.o.dt.date.today()-a.o.dt.timedelta(1)
                lastTradeType = "NA"
                
              if(shares2buy>0 and (lastTradeDate<a.o.dt.date.today() or lastTradeType=="NA" or lastTradeType=="buy")):
                print(a.createOrder("buy",shares2buy,gainers[i],"market","day"))
                latestTrades[gainers[i]] = [str(a.o.dt.date.today()), "buy"]
                f = open("../stockStuff/latestTrades.json","w")
                f.write(a.o.json.dumps(latestTrades, indent=2))
                f.close()
      else:
        print("Buying power is less than minCash - Holding")
