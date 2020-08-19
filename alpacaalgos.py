import random, sys, threading
import datetime as dt
from workdays import networkdays as nwd
import alpacafxns as a
import otherfxns as o


gainers = [] #global list of potential gaining stocks
gainerDates = {} #global list of gainers plus their initial jump date and predicted next jump date
stocksUpdatedToday = False

#generates list of potential gainers, trades based off amount of cash
def mainAlgo():
  o.init('../stockStuff/apikeys.key', '../stockStuff/stockData/') #init settings and API keys, and stock data directory
  ''' buy/sell logic:
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
  global gainers, gainerDates, stocksUpdatedToday
  
  minBuyPow = 1000 #min buying power to hold onto if..
  buyPowMargin = 1.5 # actual buy pow > this*minBuyPow
  dolPerStock = 10 #$ to dedicate to an individual stock

  minPortVal = 50 #stop trading if portfolio reaches this amount
  reducedCash = 100 #enter reduced cash mode if portfolio reaches under this amount
  reducedBuy = 10 #buy this many unique stocks if in reduced cash mode
  lowCash = 10 #enter low cash mode if portfolio reaches under this amount
  lowBuy = 5 #buy this many unique stocks if in low cash mode
  minCash = 1 #buy until this amt is left in buying power/cash balance

  sellUp = 1+.2 #trigger point. Additional logic to see if it goes higher
  sellDn = 1-.3 #limit loss
  sellUpDn = 1-.02 #sell if it triggers sellUp then drops sufficiently
  
  #TODO: change save dirs so we don't write to the sd card a bajillion times and remove csv files when done to not suck up room
  #init the stock list if we rereun during the week
  if(dt.date.today().weekday()<5): #not saturday or sunday
    f = open("../stockStuff/latestTrades.json","r")
    latestTrades = a.json.loads(f.read())
    f.close()

  portVal = float(a.getAcct()['portfolio_value'])

  while portVal>minPortVal:
    random.shuffle(gainers) #randomize list so when buying new ones, they won't always choose the top of the original list
    
    if(a.marketIsOpen()):
      print("\nMarket is open")
      f = open("../stockStuff/latestTrades.json","r")
      latestTrades = a.json.loads(f.read())
      f.close()
      
      portVal = float(a.getAcct()['portfolio_value'])
      print("Portfolio val is $"+str(portVal)+". Sell targets are "+str(sellUp)+" or "+str(sellDn))
      
      #update te stock list 20 minutes before close, if it's not already updated and if it's not currently updating
      if(a.timeTillClose()<20*60 and (not stocksUpdatedToday) and ('listUpdate' not in [t.getName() for t in threading.enumerate()])):
        updateThread = threading.Thread(target=updateStockList) #init the thread
        updateThread.setName('listUpdate') #set the name to the stock symb
        updateThread.start() #start the thread
      

      #check here if the time is close to close - in the function, check that the requested stock didn't peak today
      if(a.timeTillClose()<=5*60): #must be within 5 minutes of close to start buying
        #check2buy(latestTrades, minPortVal,reducedCash,reducedBuy,lowCash,lowBuy,minCash)
        #TODO: may want to make this its own thread
        check2buy2(latestTrades, minBuyPow, buyPowMargin, dolPerStock)
      
      print("Tradable Stocks:")
      check2sell(a.getPos(), latestTrades, sellDn, sellUp, sellUpDn)

      f = open("../stockStuff/webData.json",'w')
      f.write(a.json.dumps({"portVal":round(portVal,2),"updated":dt.datetime.now().strftime("%Y-%m-%d, %H:%M")+" CST"}))
      f.close()
      a.time.sleep(60)
      
    else:
      stocksUpdatedToday = False
      if(dt.date.today().weekday()<4): #mon-thurs
        tto = a.timeTillOpen()
      else: #fri-sun
        tto = (a.openCloseTimes(str(dt.date.today()+dt.timedelta(days=7-dt.date.today().weekday())))[0]-dt.datetime.now()).total_seconds()

      print("Market closed. Opening in "+str(int(tto/60))+" minutes")
      a.time.sleep(tto)
      

#check to sell a list of stocks
def check2sell(symList, latestTrades, sellDn, sellUp, sellUpDn):
  global gainerDates
  for e in symList:
    if(a.isAlpacaTradable(e['symbol'])): #just skip it if it can't be traded
      try:
        lastTradeDate = dt.datetime.strptime(latestTrades[e['symbol']][0],'%Y-%m-%d').date()
        lastTradeType = latestTrades[e['symbol']][1]
      except Exception:
        lastTradeDate = dt.date.today()-dt.timedelta(1)
        lastTradeType = "NA"
      
      #TODO: check for change from day's open - not from the buyPrice (in case the stock falls a bunch since we bought it, then if it jumps the x%, it might not reach the x% gain from when we bought it, but that's the risk of the market
      if(lastTradeDate<dt.date.today() or lastTradeType=="sell" or float(e['current_price'])/float(e['avg_entry_price'])>=1.75): #prevent selling on the same day as a buy (only sell if only other trade today was a sell or price increased substantially)
        #openPrice = o.getOpen(e['symbol']
        buyPrice = float(e['avg_entry_price'])
        curPrice = float(e['current_price'])
        maxPrice = 0
        print(e['symbol']+"\t-\tAppx Jump Date: "+o.goodBuy(e['symbol'],260)+"\t-\tchange: "+str(round(curPrice/buyPrice,2))) #goodbuy() defaults to look at the last 25 days, but we can force it to look farther back (in this case ~260 trading days in a year)
        
        if(curPrice/buyPrice<=sellDn):
          print("Lost it on "+e['symbol'])
          print(a.createOrder("sell",e['qty'],e['symbol']))
          latestTrades[e['symbol']] = [str(dt.date.today()), "sell"]
          f = open("../stockStuff/latestTrades.json","w")
          f.write(a.json.dumps(latestTrades, indent=2))
          f.close()
        elif(curPrice/buyPrice>=sellUp):
          print("Trigger point reached on "+e['symbol']+". Seeing if it will go up...")
          if(not e['symbol'] in [t.getName() for t in threading.enumerate()]): #if the thread is not found in names of the running threads, then start it (this stops multiple instances of the same stock thread)
            triggerThread = threading.Thread(target=triggeredUp, args=(e, curPrice, buyPrice, maxPrice, sellUpDn, latestTrades)) #init the thread
            triggerThread.setName(e['symbol']) #set the name to the stock symb
            triggerThread.start() #start the thread

#triggered selling-up - this is the one that gets multithreaded
def triggeredUp(symbObj, curPrice, buyPrice, maxPrice, sellUpDn, latestTrades):
  print("Starting thread for "+symbObj['symbol'])
  while(curPrice/buyPrice>=maxPrice/buyPrice*sellUpDn and a.timeTillClose()>=30):
    curPrice = a.getPrice(symbObj['symbol'])
    maxPrice = max(maxPrice, curPrice)
    print(symbObj['symbol']+" - "+str(round(curPrice/buyPrice,2))+" - "+str(round(maxPrice/buyPrice*sellUpDn,2)))
    a.time.sleep(3)
  
  print(a.createOrder("sell",symbObj['qty'],symbObj['symbol']))
  latestTrades[symbObj['symbol']] = [str(dt.date.today()), "sell"]
  f = open("../stockStuff/latestTrades.json","w")
  f.write(a.json.dumps(latestTrades, indent=2))
  f.close()

#whether to buy a stock or not
def check2buy(latestTrades, minPortVal, reducedCash, reducedBuy, lowCash, lowBuy, minCash):
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
  
  #TODO: check here for the day's high to see if it reached the threshold for each stock - remove ones that it did from the gainers list
  if(buyPow>reducedCash): #in normal operating mode
    print("Normal Operation Mode. Available Buying Power: $"+str(buyPow))
    #div cash over all gainers
    for e in gainers:
      if(a.isAlpacaTradable(e)):
        curPrice = a.getPrice(e)
        if(curPrice>0 and reducedBuy>0): #don't bother buying if the stock is invalid (no div0)
          shares2buy = int((buyPow/reducedBuy)/curPrice)
          try:
            lastTradeDate = dt.datetime.strptime(latestTrades[gainers[i]][0],'%Y-%m-%d').date()
            lastTradeType = latestTrades[gainers[i]][1]
          except Exception:
            lastTradeDate = dt.date.today()-dt.timedelta(1)
            lastTradeType = "NA"
            
          #check to make sure that we're not buying/selling on the same day
          if(shares2buy>0 and (lastTradeDate<dt.date.today() or lastTradeType=="NA" or lastTradeType=="buy")):
            print(a.createOrder("buy",shares2buy,e,"market","day"))
            latestTrades[e] = [str(dt.date.today()), "buy"]
            f = open("../stockStuff/latestTrades.json","w")
            f.write(a.json.dumps(latestTrades, indent=2))
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
              lastTradeDate = dt.datetime.strptime(latestTrades[gainers[i]][0],'%Y-%m-%d').date()
              lastTradeType = latestTrades[gainers[i]][1]
            except Exception:
              lastTradeDate = dt.date.today()-dt.timedelta(1)
              lastTradeType = "NA"
              
            if(shares2buy>0 and (lastTradeDate<dt.date.today() or lastTradeType=="NA" or lastTradeType=="buy")):
              print(a.createOrder("buy",shares2buy,gainers[i],"market","day"))
              latestTrades[gainers[i]] = [str(dt.date.today()), "buy"]
              f = open("../stockStuff/latestTrades.json","w")
              f.write(a.json.dumps(latestTrades, indent=2))
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
                lastTradeDate = dt.datetime.strptime(latestTrades[gainers[i]][0],'%Y-%m-%d').date()
                lastTradeType = latestTrades[gainers[i]][1]
              except Exception:
                lastTradeDate = dt.date.today()-dt.timedelta(1)
                lastTradeType = "NA"
                
              if(shares2buy>0 and (lastTradeDate<dt.date.today() or lastTradeType=="NA" or lastTradeType=="buy")):
                print(a.createOrder("buy",shares2buy,gainers[i],"market","day"))
                latestTrades[gainers[i]] = [str(dt.date.today()), "buy"]
                f = open("../stockStuff/latestTrades.json","w")
                f.write(a.json.dumps(latestTrades, indent=2))
                f.close()
      else:
        print("Buying power is less than minCash - Holding")


#buy int(buyPow/10) # of individual stocks. If buyPow>minBuyPow*1.5, then usablebuyPow=buyPow-minBuyPow
def check2buy2(latestTrades, minBuyPow, buyPowMargin, dolPerStock):
  global gainers, gainerDates

  usableBuyPow = a.getBuyPow() #this must be updated in the loop because it will change during every buy
  if(usableBuyPow>=minBuyPow*buyPowMargin): #if we have more buying power than the min plus some leeway, then reduce it to hold onto that buy pow
    print("Can withdrawl $"+str(round(minBuyPow,2))+" safely.")
    usableBuyPow = max(usableBuyPow-minBuyPow,0) #use max just in case buyPowMargin is accidentally set to <1

  i=0
  stocksBought = 0
  stocks2buy = int(usableBuyPow/dolPerStock)
  while(stocksBought<stocks2buy and i<len(gainers)):
    symb = gainers[i]
    if(symb not in [t.getName() for t in threading.enumerate()]): #make sure the stock isn't trying to be sold already
      try:
        lastTradeDate = dt.datetime.strptime(latestTrades[symb][0],'%Y-%m-%d').date()
        lastTradeType = latestTrades[symb][1]
      except Exception:
        lastTradeDate = dt.datetime.today()-dt.timedelta(1)
        lastTradeType = "NA"

      if(lastTradeDate < dt.date.today() or lastTradeType != "sell"):
        if(a.isAlpacaTradable(symb)): #first make sure we can actually buy it
          curPrice = a.getPrice(symb)
          if(curPrice>0):
            shares2buy = int(dolPerStock/curPrice)
            print(a.createOrder("buy",shares2buy,symb,"market","day"))
            #TODO: make sure it actually executed the order, then increment
            stocksBought += 1
            i += 1
          else:
            i += 1
        else:
          i += 1
      else:
        i += 1
    else:
      i += 1

  print("Done buying")



#update the stock list - takes ~5 minutes to process 400 stocks
def updateStockList():
  global gainers, gainerDates, stocksUpdatedToday
  print("Updating stock list")
  #list of stocks that may gain in the near future as well as currently held stocks and their last gain date
  gainerDates = o.getGainers(list(set(o.getList()+[e['symbol'] for e in a.getPos()]))) #combine nasdaq list & my stocks & remove duplicates - order doesn't matter
  gainers = list(gainerDates) #list of just the stock symbols
  stocksUpdatedToday = True
  print("Done updating list")
