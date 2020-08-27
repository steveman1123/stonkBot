import random, sys, threading
from workdays import networkdays as nwd
import alpacafxns as a


gainers = [] #global list of potential gaining stocks
gainerDates = {} #global list of gainers plus their initial jump date and predicted next jump date
stocksUpdatedToday = False

#TODO: add master/slave functionality to enable a backup to occur - that is if this is run on 2 computers, one can be set to master, the other to slave, and if the master dies, the slave can become the master

#generates list of potential gainers, trades based off amount of cash
def mainAlgo():
  '''
  buy/sell logic:
   - limit gain to at least 20%, sell if it drops by 2% or is close to close
   - buy $minDolPerStock ($5) worth of stocks until usableBuyPow>(minDolPerStock*len(gainers)) - then increase dolPerStock
   - stop loss at ~70%
  '''
  a.o.init('../stockStuff/apikeys.txt', '../stockStuff/stockData/') #init settings and API keys, and stock data directory
  global gainers, gainerDates, stocksUpdatedToday
  
  minBuyPow = 1000 #min buying power to hold onto if..
  buyPowMargin = 1.5 # actual buy pow > this*minBuyPow
  minDolPerStock = 5 #min $ to dedicate to an individual stock

  minPortVal = 50 #stop trading if portfolio reaches this amount

  sellUp = 1+.2 #trigger point. Additional logic to see if it goes higher
  sellDn = 1-.3 #limit loss
  sellUpDn = 1-.02 #sell if it triggers sellUp then drops sufficiently
  
  #init the stock list if we rereun during the week
  if(a.o.dt.date.today().weekday()<5): #not saturday or sunday
    f = open("../stockStuff/latestTrades.json","r")
    latestTrades = a.o.json.loads(f.read())
    f.close()

  portVal = float(a.getAcct()['portfolio_value'])

  while portVal>minPortVal:
    random.shuffle(gainers) #randomize list so when buying new ones, they won't always choose the top of the original list
    
    if(a.marketIsOpen()):
      print("\nMarket is open")
      f = open("../stockStuff/latestTrades.json","r")
      latestTrades = a.o.json.loads(f.read())
      f.close()
      
      acctInfo = a.getAcct()
      
      portVal = float(acctInfo['portfolio_value'])
      print("Portfolio val is $"+str(portVal)+". Sell targets are "+str(sellUp)+" or "+str(sellDn))
      
      #only update the stock list and buy stocks if the gainers list is done being populated/updated and that we actually have enough money to buy things
      if('listUpdate' not in [t.getName() for t in threading.enumerate()] and float(acctInfo['buying_power'])>=minDolPerStock):
        #update the stock list 20 minutes before close, if it's not already updated
        if((not stocksUpdatedToday) and a.timeTillClose()<=20*60):
          updateThread = threading.Thread(target=updateStockList) #init the thread
          updateThread.setName('listUpdate') #set the name to the stock symb
          updateThread.start() #start the thread
      
        #check here if the time is close to close - in the function, check that the requested stock didn't peak today
        if('buying' not in [t.getName() for t in threading.enumerate()] and a.timeTillClose()<=10*60): #must be within 10 minutes of close to start buying and buying thread cannot be running already
          #Use this for the non-threading option
          check2buy(latestTrades, minBuyPow, buyPowMargin, minDolPerStock)
          #use this for the threading option
          #buyThread = threading.Thread(target=check2buy, args=(latestTrades, minBuyPow, buyPowMargin, dolPerStock)) #init the thread
          #buyThread.setName('buying') #set the name to the stock symb
          #a.o.buyThread.start() #start the thread
          
      
      print("Tradable Stocks:")
      check2sell(a.getPos(), latestTrades, sellDn, sellUp, sellUpDn)

      f = open("../stockStuff/webData.json",'w')
      f.write(a.o.json.dumps({"portVal":round(portVal,2),"updated":a.o.dt.datetime.now().strftime("%Y-%m-%d, %H:%M")+" CST"}))
      f.close()
      a.o.time.sleep(60)
      
    else:
      stocksUpdatedToday = False
      if(a.o.dt.date.today().weekday()<4): #mon-thurs
        tto = a.timeTillOpen()
      else: #fri-sun
        tto = (a.openCloseTimes(str(a.o.dt.date.today()+a.o.dt.timedelta(days=7-a.o.dt.date.today().weekday())))[0]-a.o.dt.datetime.now()).total_seconds()

      print("Market closed. Opening in "+str(int(tto/60))+" minutes")
      a.o.time.sleep(tto)
      

#check to sell a list of stocks - symlist is the output of a.getPos()
def check2sell(symList, latestTrades, sellDn, sellUp, sellUpDn):
  global gainerDates
  for e in symList:
    #if(a.isAlpacaTradable(e['symbol'])): #just skip it if it can't be traded - skipping this for slower connections & to save a query
    try:
      lastTradeDate = a.o.dt.datetime.strptime(latestTrades[e['symbol']][0],'%Y-%m-%d').date()
      lastTradeType = latestTrades[e['symbol']][1]
    except Exception:
      lastTradeDate = a.o.dt.date.today()-a.o.dt.timedelta(1)
      lastTradeType = "NA"
    
    #TODO: check for change from day's open - not from the buyPrice (in case the stock falls a bunch since we bought it, then if it jumps the x%, it might not reach the x% gain from when we bought it, but that's the risk of the market
    if(lastTradeDate<a.o.dt.date.today() or lastTradeType=="sell" or float(e['current_price'])/float(e['avg_entry_price'])>=1.75): #prevent selling on the same day as a buy (only sell if only other trade today was a sell or price increased substantially)
      #openPrice = a.o.getOpen(e['symbol']
      buyPrice = float(e['avg_entry_price'])
      curPrice = float(e['current_price'])
      maxPrice = 0
      lastJump = a.o.dt.datetime.strptime(a.o.goodBuy(e['symbol'],260),"%Y-%m-%d").date()
      print(e['symbol']+"\t-\tInitial Jump Date: "+str(lastJump)+", predicted jump: "+str(lastJump+a.o.dt.timedelta(5*7))+" +/- 3wks\t-\tchange: "+str(round(curPrice/buyPrice,2))) #goodbuy() defaults to look at the last 25 days, but we can force it to look farther back (in this case ~260 trading days in a year)
      
      if(curPrice/buyPrice<=sellDn):
        print("Lost it on "+e['symbol'])
        print(a.createOrder("sell",e['qty'],e['symbol']))
        latestTrades[e['symbol']] = [str(a.o.dt.date.today()), "sell"]
        f = open("../stockStuff/latestTrades.json","w")
        f.write(a.o.json.dumps(latestTrades, indent=2))
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
    a.o.time.sleep(3)
  
  print(a.createOrder("sell",symbObj['qty'],symbObj['symbol']))
  latestTrades[symbObj['symbol']] = [str(a.o.dt.date.today()), "sell"]
  f = open("../stockStuff/latestTrades.json","w")
  f.write(a.o.json.dumps(latestTrades, indent=2))
  f.close()



#buy int(buyPow/10) # of individual stocks. If buyPow>minBuyPow*buyPowMargin, then usablebuyPow=buyPow-minBuyPow
def check2buy(latestTrades, minBuyPow, buyPowMargin, minDolPerStock):
  global gainers, gainerDates

  
  usableBuyPow = float(a.getAcct()['buying_power']) #init as the current buying power
  if(usableBuyPow>=minBuyPow*buyPowMargin): #if we have more buying power than the min plus some leeway, then reduce it to hold onto that buy pow
    print("Can withdrawl $"+str(round(minBuyPow,2))+" safely.")
    usableBuyPow = max(usableBuyPow-minBuyPow,0) #use max just in case buyPowMargin is accidentally set to <1
  
  try:
    dolPerStock = max(minDolPerStock, usableBuyPow/len(gainers)) #if buyPow>(minDolPerStock*len(gainers)) then divvy up buyPow over gainers
  except Exception:
    dolPerStock = minDolPerStock
    
  i=0 #index of gainers
  stocksBought = 0 #number of stocks bought
  stocks2buy = int(usableBuyPow/dolPerStock) #number of stocks to buy
  while(stocksBought<stocks2buy and i<len(gainers)):
    symb = gainers[i]
    if(symb not in [t.getName() for t in threading.enumerate()]): #make sure the stock isn't trying to be sold already
      try:
        lastTradeDate = a.o.dt.datetime.strptime(latestTrades[symb][0],'%Y-%m-%d').date()
        lastTradeType = latestTrades[symb][1]
      except Exception:
        lastTradeDate = a.o.dt.datetime.today().date()-a.o.dt.timedelta(1)
        lastTradeType = "NA"

      if(lastTradeDate < a.o.dt.datetime.today().date() or lastTradeType != "sell"):
        if(a.isAlpacaTradable(symb)): #first make sure we can actually buy it
          curPrice = a.getPrice(symb)
          if(curPrice>0):
            shares2buy = int(dolPerStock/curPrice)
            orderText = a.createOrder("buy",shares2buy,symb,"market","day")
            #make sure it actually executed the order, then increment
            if(orderText.endswith('accepted')):
              print(orderText)
              stocksBought += 1
              latestTrades[symb][0] = str(a.o.dt.date.today())
              latestTrades[symb][1] = "buy"
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
  gainerDates = a.o.getGainers(list(dict.fromkeys(a.o.getList()+[e['symbol'] for e in a.getPos()]))) #combine nasdaq list & my stocks & remove duplicates - order doesn't matter
  gainers = list(gainerDates) #list of just the stock symbols
  stocksUpdatedToday = True
  print("Done updating list")
