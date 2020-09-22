import random, threading
from workdays import networkdays as nwd
from glob import glob
import alpacafxns as a


gainers = [] #global list of potential gaining stocks
gainerDates = {} #global list of gainers plus their initial jump date and predicted next jump date
gStocksUpdated = False

#TODO: add master/slave functionality to enable a backup to occur - that is if this is run on 2 computers, one can be set to master, the other to slave, and if the master dies, the slave can become the master
#TODO: make list of wins & loses and analyze why (improve algo as it goes)

#generates list of potential gainers, trades based off amount of cash
def mainAlgo():
  '''
  buy/sell logic:
   - limit gain to at least 20%, sell if it drops by 2% or is close to close
   - buy $minDolPerStock ($5) worth of stocks until usableBuyPow>(minDolPerStock*len(gainers)) - then increase dolPerStock
   - stop loss at ~70%
  '''
  
  global gStocksUpdated #this only gets set once in this function - after market is closed
  isMaster = a.o.c['isMaster'] #is the master or a slave program - a slave will relinquish control to a master if the master is running, but will take over if the master dies
  
  minBuyPow = a.o.c['minBuyPow'] #min buying power to hold onto if..
  buyPowMargin = a.o.c['buyPowMargin'] # actual buy pow > this*minBuyPow
  minDolPerStock = a.o.c['minDolPerStock'] #min $ to dedicate to an individual stock

  minPortVal = a.o.c['minPortVal'] #stop trading if portfolio reaches this amount

  sellUp = a.o.c['sellUp'] #trigger point. Compare to when it was bought, additional logic to see if it goes higher
  sellUpFromClose = a.o.c['sellUpFromClose'] #secondary trigger point. Compare to previous day's close
  sellDn = a.o.c['sellDn'] #limit loss
  sellUpDn = a.o.c['sellUpDn'] #sell if it triggers sellUp or sellUpFromClose then drops sufficiently
  
  
  #init the stock list if we rereun during the week
  if(a.o.dt.date.today().weekday()<5): #not saturday or sunday
    f = open(a.o.c['latestTradesFile'],"r")
    latestTrades = a.o.json.loads(f.read())
    f.close()

  portVal = float(a.getAcct()['portfolio_value'])

  while portVal>minPortVal:
    random.shuffle(gainers) #randomize list so when buying new ones, they won't always choose the top of the original list

    
    #TODO: if slave, check here to see if master is back online
    if(not isMaster and a.o.masterLives()):
      a.o.time.sleep(3600)
    else: #is the master or the master is dead
      
      if(a.marketIsOpen()):
        print("\nMarket is open")
        f = open(a.o.c['latestTradesFile'],"r")
        latestTrades = a.o.json.loads(f.read())
        f.close()
        
        acctInfo = a.getAcct()
        stocksUpdated = gStocksUpdated #set the local value to the global value        
        portVal = float(acctInfo['portfolio_value'])
        print("Portfolio val is $"+str(portVal)+". Buying power is $"+acctInfo['buying_power'])
        
        #only update the stock list and buy stocks if the gainers list is done being populated/updated and that we actually have enough money to buy things
        if('listUpdate' not in [t.getName() for t in threading.enumerate()] and float(acctInfo['buying_power'])>=minDolPerStock):
          #update the stock list 20 minutes before close, if it's not already updated
          if((not stocksUpdated) and a.timeTillClose()<=a.o.c['updateListTime']*60):
            updateThread = threading.Thread(target=updateStockList) #init the thread
            updateThread.setName('listUpdate') #set the name to the stock symb
            updateThread.start() #start the thread
        
          #check here if the time is close to close - in the function, check that the requested stock didn't peak today
          if('buying' not in [t.getName() for t in threading.enumerate()] and a.timeTillClose()<=a.o.c['buyTime']*60): #must be within 10 minutes of close to start buying and buying thread cannot be running already
            #Use this for the non-threading option
            check2buy(latestTrades, minBuyPow, buyPowMargin, minDolPerStock)
            #use this for the threading option
            #buyThread = threading.Thread(target=check2buy, args=(latestTrades, minBuyPow, buyPowMargin, dolPerStock)) #init the thread
            #buyThread.setName('buying') #set the name to the stock symb
            #a.o.buyThread.start() #start the thread
            
        
        print("Tradable Stocks:")
        check2sell(a.getPos(), latestTrades, sellDn, sellUp, sellUpFromClose, sellUpDn)
  
        f = open(a.o.c['webDataFile'],'w')
        f.write(a.o.json.dumps({"portVal":round(portVal,2),"updated":a.o.dt.datetime.utcnow().strftime("%Y-%m-%d, %H:%M")+" UTC"}))
        f.close()
        a.o.time.sleep(60)
        
      else:
        print("Market closed.")
        gStocksUpdated = False
        if(a.o.dt.date.today().weekday()==4): #if it's friday
          print("Removing saved csv files") #delete all csv files in stockDataDir
          for f in glob(a.o.c['stockDataDir']+"*.csv"):
            a.o.os.unlink(f)
        tto = a.timeTillOpen()
        print("Opening in "+str(round(tto/3600,2))+" hours")
        a.o.time.sleep(tto)
        
#check to sell a list of stocks - symlist is the output of a.getPos()
def check2sell(symList, latestTrades, mainSellDn, mainSellUp, sellUpFromClose, sellUpDn):
  print("symb\tinitial jump\tpredicted jump (+/- 3wks)\tchange from buy\tchange from close\tsell points")
  print("----\t------------\t-------------------------\t---------------\t-----------------\t-----------")
  for e in symList:
    #if(a.isAlpacaTradable(e['symbol'])): #just skip it if it can't be traded - skipping this for slower connections & to save a query
    try:
      lastTradeDate = a.o.dt.datetime.strptime(latestTrades[e['symbol']][0],'%Y-%m-%d').date()
      lastTradeType = latestTrades[e['symbol']][1]
    except Exception:
      lastTradeDate = a.o.dt.date.today()-a.o.dt.timedelta(1)
      lastTradeType = "NA"

    
    if(lastTradeDate<a.o.dt.date.today() or lastTradeType=="sell" or float(e['current_price'])/float(e['avg_entry_price'])>=1.75): #prevent selling on the same day as a buy (only sell if only other trade today was a sell or price increased substantially)
      buyPrice = float(e['avg_entry_price'])
      closePrice = float(e['lastday_price'])
      curPrice = float(e['current_price'])
      maxPrice = 0
      buyInfo = a.o.goodBuy(e['symbol'],260)
      
      try:
        lastJump = a.o.dt.datetime.strptime(buyInfo,"%m/%d/%Y").date()
        #adjust selling targets based on date to add a time limit

        #sellUp change of 0 if <=5 weeks after initial jump, -.05 for every week after 6 weeks for a min of 1
        sellUp = round(max(1,mainSellUp-.05*max(0,int((a.o.dt.date.today()-(lastJump+a.o.dt.timedelta(6*7))).days/7))),2)
        #sellDn change of 0 if <=5 weeks after initial jump, +.05 for every week after 6 weeks for a max of 1
        sellDn = round(min(1,mainSellDn+.05*max(0,int((a.o.dt.date.today()-(lastJump+a.o.dt.timedelta(6*7))).days/7))),2)

        print(e['symbol']+"\t"+str(lastJump)+"\t"+str(lastJump+a.o.dt.timedelta(5*7))+"\t\t\t"+str(round(curPrice/buyPrice,2))+"\t\t"+str(round(curPrice/closePrice,2))+"\t\t\t"+str(sellUp)+" & "+str(sellDn)) #goodbuy() defaults to look at the last 25 days, but we can force it to look farther back (in this case ~260 trading days in a year)
      except Exception:
        print(e['symbol']+" - "+buyInfo)
        sellUp = mainSellUp
        sellDn = mainSellDn

      #cut the losses if we missed the jump or if the price dropped too much
      if(curPrice/buyPrice<=sellDn or buyInfo=="Missed jump"):
        print("Lost it on "+e['symbol'])
        print(a.createOrder("sell",e['qty'],e['symbol']))
        latestTrades[e['symbol']] = [str(a.o.dt.date.today()), "sell"]
        f = open(a.o.c['latestTradesFile'],"w")
        f.write(a.o.json.dumps(latestTrades, indent=2))
        f.close()
      
      #use e['lastday_price'] to get previous close amount ... or curPrice/float(e['lastday_price'])>=sellUpFromYesterday
      elif(curPrice/buyPrice>=sellUp or curPrice/closePrice>=sellUpFromClose):
        print("Trigger point reached on "+e['symbol']+". Seeing if it will go up...")
        if(not e['symbol'] in [t.getName() for t in threading.enumerate()]): #if the thread is not found in names of the running threads, then start it (this stops multiple instances of the same stock thread)
          triggerThread = threading.Thread(target=triggeredUp, args=(e, curPrice, buyPrice, closePrice, maxPrice, sellUpDn, latestTrades)) #init the thread
          triggerThread.setName(e['symbol']) #set the name to the stock symb
          triggerThread.start() #start the thread

#triggered selling-up - this is the one that gets multithreaded
def triggeredUp(symbObj, curPrice, buyPrice, closePrice, maxPrice, sellUpDn, latestTrades):
  print("Starting thread for "+symbObj['symbol'])
  while((curPrice/buyPrice>=maxPrice/buyPrice*sellUpDn or curPrice/closePrice>=maxPrice/closePrice*sellUpDn) and a.timeTillClose()>=30):
    curPrice = a.getPrice(symbObj['symbol'])
    maxPrice = max(maxPrice, curPrice)
    print(symbObj['symbol']+" - "+str(round(curPrice/buyPrice,2))+":"+str(round(maxPrice/buyPrice*sellUpDn,2))+" - "+str(round(curPrice/closePrice,2))+":"+str(round(maxPrice/closePrice,2)))
    a.o.time.sleep(3)
  
  print(a.createOrder("sell",symbObj['qty'],symbObj['symbol']))
  latestTrades[symbObj['symbol']] = [str(a.o.dt.date.today()), "sell"]
  f = open(a.o.c['latestTradesFile'],"w")
  f.write(a.o.json.dumps(latestTrades, indent=2))
  f.close()



#buy int(buyPow/10) # of individual stocks. If buyPow>minBuyPow*buyPowMargin, then usablebuyPow=buyPow-minBuyPow
def check2buy(latestTrades, minBuyPow, buyPowMargin, minDolPerStock):
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
    symb = gainers[i] #candidate stock to buy
    if(symb not in [t.getName() for t in threading.enumerate()]): #make sure the stock isn't trying to be sold already
      try: #check when it was traded last
        lastTradeDate = a.o.dt.datetime.strptime(latestTrades[symb][0],'%Y-%m-%d').date()
        lastTradeType = latestTrades[symb][1]
      except Exception:
        lastTradeDate = a.o.dt.datetime.today().date()-a.o.dt.timedelta(1)
        lastTradeType = "NA"

      if(lastTradeDate < a.o.dt.datetime.today().date() or lastTradeType != "sell"): #make sure we didn't sell it today already
        if(a.isAlpacaTradable(symb)): #make sure it's tradable on the market
          curPrice = a.getPrice(symb)
          if(curPrice>0):
            shares2buy = int(dolPerStock/curPrice)
            orderText = a.createOrder("buy",shares2buy,symb,"market","day")
            #make sure it actually executed the order, then increment
            if(orderText.endswith('accepted')):
              print(orderText)
              latestTrades[symb] = [str(a.o.dt.date.today()),"buy"]
              f = open(a.o.c['latestTradesFile'],"w")
              f.write(a.o.json.dumps(latestTrades, indent=2))
              f.close()
              stocksBought += 1
            i += 1 #try the next stock
          else:
            i += 1 #try the next stock
        else:
          i += 1 #try the next stock
      else:
        i += 1 #try the next stock
    else:
      i += 1 #try the next stock

  print("Done buying")



#update the stock list - takes ~5 minutes to process 400 stocks
def updateStockList():
  global gainers, gainerDates, gStocksUpdated
  print("Updating stock list")
  #list of stocks that may gain in the near future as well as currently held stocks and their last gain date
  gainerDates = a.o.getGainers(list(dict.fromkeys(a.o.getList()+[e['symbol'] for e in a.getPos()]))) #combine nasdaq list & my stocks & remove duplicates - order doesn't matter
  gainers = list(gainerDates) #list of just the stock symbols
  print(f"Done updating list - {len(gainers)} potential gainers")
  gStocksUpdated = True
