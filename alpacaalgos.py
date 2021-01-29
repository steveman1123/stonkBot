import random, threading
from workdays import networkdays as nwd
from glob import glob
import alpacafxns as a
# import newsScrape as ns

gainers = [] #global list of potential gaining stocks
gainerDates = {} #global list of gainers plus their initial jump date and predicted next jump date
gStocksUpdated = False

#used for coloring the displayed text
class bcolor:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


#TODO: add master/slave functionality to enable a backup to occur - that is if this is run on 2 computers, one can be set to master, the other to slave, and if the master dies, the slave can become the master
#TODO: make list of wins & loses and analyze why (improve algo as it goes)
#TODO: adjust sell %'s if > 1+(sellUp-1)/2 (e.g. if >1.1 if sellUp=1.2), then have a larger sellUpDn (e.g. 5%), then decrease if it reaches sellUp

#generates list of potential gainers, trades based off amount of cash
def mainAlgo():
  global gStocksUpdated #this only gets set once in this function - after market is closed
  isMaster = bool(a.o.c['Master Info']['isMaster']) #is the master or a slave program - a slave will relinquish control to a master if the master is running, but will take over if the master dies
  
  minBuyPow = float(a.o.c['Account Params']['minBuyPow']) #min buying power to hold onto if..
  buyPowMargin = float(a.o.c['Account Params']['buyPowMargin']) # actual buy pow > this*minBuyPow
  minDolPerStock = float(a.o.c['Account Params']['minDolPerStock']) #min $ to dedicate to an individual stock

  minPortVal = float(a.o.c['Account Params']['minPortVal']) #stop trading if portfolio reaches this amount

  sellUp = float(a.o.c['Sell Params']['sellUp']) #trigger point. Compare to when it was bought, additional logic to see if it goes higher
  sellDn = float(a.o.c['Sell Params']['sellDn']) #limit loss
  sellUpDn = float(a.o.c['Sell Params']['sellUpDn']) #sell if it triggers sellUp then drops sufficiently
  
  
  #init the stock list if we rereun during the week
  if(a.o.dt.date.today().weekday()<5): #not saturday or sunday
    with open(a.o.c['File Locations']['latestTradesFile'],"r") as f:
      latestTrades = a.o.json.loads(f.read())

  portVal = float(a.getAcct()['portfolio_value'])

  while portVal>minPortVal: #TODO: adjust minPortVal to be some % of max port val
    random.shuffle(gainers) #randomize list so when buying new ones, they won't always choose the top of the original list

    
    #TODO: if slave, check here to see if master is back online
    if(not isMaster and a.o.masterLives()):
      a.o.time.sleep(3600)
    else: #is the master or the master is dead
      
      if(a.marketIsOpen()):
        print("\nMarket is open")
        with open(a.o.c['File Locations']['latestTradesFile'],"r") as f:
          latestTrades = a.o.json.loads(f.read())
        
        acctInfo = a.getAcct()
        portVal = float(acctInfo['portfolio_value'])
        print(f"Portfolio val is ${round(portVal,2)}. Buying power is ${round(float(acctInfo['cash']),2)}, ${max(round(float(acctInfo['cash'])-minBuyPow*buyPowMargin,2),0)} available")
        
        #if the program is started while the market is open, update the stock list immediately (do not try to run it again if it's already running)
        if(not gStocksUpdated and 'markUpdate' not in [t.getName() for t in threading.enumerate()]):
          #mark stocks to be sold, then update the stock list
          markUpdateThread = threading.Thread(target=markAndUpdate) #init the thread
          markUpdateThread.setName('markUpdate') #set the name to the stock symb
          markUpdateThread.start() #start the thread 
        
        #only update the stock list and buy stocks if the gainers list is done being populated/updated and that we actually have enough money to buy things
        if('listUpdate' not in [t.getName() for t in threading.enumerate()] and float(acctInfo['cash'])>=minDolPerStock):
          #check here if the time is close to close - in the function, check that the requested stock didn't peak today
          if(a.timeTillClose()<=float(a.o.c['Time Params']['buyTime'])*60): #must be within some time before close to start buying and buying thread cannot be running already
            #Use this for non-threading:
            check2buy(latestTrades, minBuyPow, buyPowMargin, minDolPerStock)
            '''
            #use this for threading:
            if('buying' not in [t.getName() for t in threading.enumerate()] and a.timeTillClose()<=a.o.c['Time Params']['buyTime']*60): #must be within some time before close to start buying and buying thread cannot be running already
              buyThread = threading.Thread(target=check2buy, args=(latestTrades, minBuyPow, buyPowMargin, dolPerStock)) #init the thread
              buyThread.setName('buying') #set the name to the stock symb
              a.o.buyThread.start() #start the thread
            '''
        
        print("Tradable Stocks:")
        check2sell(a.getPos(), latestTrades, sellDn, sellUp, sellUpDn)
        '''
        with open(a.o.c['File Locations']['webDataFile'],'w') as f:
          f.write(a.o.json.dumps({"portVal":round(portVal,2),"updated":a.o.dt.datetime.utcnow().strftime("%Y-%m-%d, %H:%M")+" UTC"}))
        '''
        a.o.time.sleep(60)
        
      else:
        print("Market closed.")
        gStocksUpdated = False
        
        
       

        if(a.o.dt.date.today().weekday()==4): #if it's friday
          print("Removing saved csv files") #delete all csv files in stockDataDir
          for f in glob(a.o.c['File Locations']['stockDataDir']+"*.csv"):
            a.o.os.unlink(f)
        tto = a.timeTillOpen()
        print(f"Opening in {round(tto/3600,2)} hours")
        #at n minutes or later before market opens, update the stock list. If market is open, update immediately
        if(tto<=float(a.o.c['Time Params']['updateListTime'])*60):
          #mark stocks to be sold, then update the stock list
          markUpdateThread = threading.Thread(target=markAndUpdate) #init the thread
          markUpdateThread.setName('markUpdate') #set the name to the stock symb
          markUpdateThread.start() #start the thread
          
          a.o.time.sleep(tto) #we'll probably lose ~1 second of market time in the morning
        else:
          print(f"Updating list in {round((tto-float(a.o.c['Time Params']['updateListTime'])*60)/3600,2)} hours")
          a.o.time.sleep(tto-float(a.o.c['Time Params']['updateListTime'])*60) #sleep until time to update
  
  print(f"Portfolio value of ${portVal} is less than minimum value of ${round(minPortVal,2)}")
  a.sellAll()

#check to sell a list of stocks - symlist is the output of a.getPos()
def check2sell(symList, latestTrades, mainSellDn, mainSellUp, sellUpDn):
  print("symb\tinit jump\tpred jump (+/- 3wks)\tchg from buy\tchg from close\tsell points")
  print("----\t---------\t--------------------\t------------\t--------------\t-----------")
  for e in symList:
    #if(a.isAlpacaTradable(e['symbol'])): #just skip it if it can't be traded - skipping this for slower connections & to save a query
    try:
      lastTradeDate = a.o.dt.datetime.strptime(latestTrades[e['symbol']]['tradeDate'],'%Y-%m-%d').date()
      lastTradeType = latestTrades[e['symbol']]['tradeType']
      avgBuyPrice = float(e['avg_entry_price']) #if it doesn't exist, default to the avg buy price over all time - it's important to keep a separate record to reset after a sell rather than over all time
    except Exception:
      lastTradeDate = a.o.dt.date.today()-a.o.dt.timedelta(1)
      lastTradeType = "NA"
      avgBuyPrice = float(e['avg_entry_price'])

    try:
      shouldSell = latestTrades[e['symbol']]['shouldSell']
    except Exception: #in the event it doesn't exist, don't worry about it
      shouldSell = False

    #if marked to sell, sell regardless of price immediately
    if(shouldSell):
      print(e['symbol']+" marked for immediate sale.")
      print(a.createOrder("sell",e['qty'],e['symbol']))
      latestTrades[e['symbol']] = {
                                   "tradeDate": str(a.o.dt.date.today()),
                                   "tradeType": "sell",
                                   "buyPrice":0,
                                   "shouldSell": False
                                  }
      with open(a.o.c['File Locations']['latestTradesFile'],"w") as f:
        f.write(a.o.json.dumps(latestTrades, indent=2))
    
    elif(lastTradeDate<a.o.dt.date.today() or lastTradeType=="sell" or float(a.getPrice(e['symbol']))/avgBuyPrice>=1.75): #prevent selling on the same day as a buy (only sell if only other trade today was a sell or price increased substantially)
      buyPrice = avgBuyPrice
      closePrice = float(e['lastday_price'])
      #curPrice = float(e['current_price'])
      curPrice = a.getPrice(e['symbol'])
      maxPrice = 0
      buyInfo = a.o.goodBuy(e['symbol'],260)
      
      try:
        lastJump = a.o.dt.datetime.strptime(buyInfo,"%m/%d/%Y").date()
        #adjust selling targets based on date to add a time limit

        #TODO: change these to change on a daily basis rather than on a weekly basis and scale to both reach 1 at the same time
        #      after 6 weeks since the initial jump, the sell values should reach 1 after 4 weeks (20 work days)
        #sellUp change of 0 if <=5 weeks after initial jump, -.05 for every week after 6 weeks for a min of 1
        sellUp = round(max(1,mainSellUp-.05*max(0,int((a.o.dt.date.today()-(lastJump+a.o.dt.timedelta(6*7))).days/7))),2)
        #sellDn change of 0 if <=5 weeks after initial jump, +.05 for every week after 6 weeks for a max of 1
        sellDn = round(min(1,mainSellDn+.05*max(0,int((a.o.dt.date.today()-(lastJump+a.o.dt.timedelta(6*7))).days/7))),2)

        totalChange = round(curPrice/buyPrice,2)
        dayChange = round(curPrice/closePrice,2)
        print(f"{e['symbol']}\t{lastJump}\t{lastJump+a.o.dt.timedelta(5*7)}\t\t{bcolor.FAIL if totalChange<1 else bcolor.OKGREEN}{totalChange}{bcolor.ENDC}\t\t{bcolor.FAIL if dayChange<1 else bcolor.OKGREEN}{dayChange}{bcolor.ENDC}\t\t{sellUp} & {sellDn}")
      except Exception:
        print(e['symbol']+" - "+buyInfo)
        sellUp = mainSellUp
        sellDn = mainSellDn



      #cut the losses if we missed the jump or if the price dropped too much
      if(buyPrice==0 or curPrice/buyPrice<=sellDn or buyInfo=="Missed jump"):
        print("Lost it on "+e['symbol'])
        print(a.createOrder("sell",e['qty'],e['symbol']))
        latestTrades[e['symbol']] = {
                                     "tradeDate": str(a.o.dt.date.today()),
                                     "tradeType": "sell",
                                     "buyPrice":0,
                                     "shouldSell": False
                                    }
        with open(a.o.c['File Locations']['latestTradesFile'],"w") as f:
          f.write(a.o.json.dumps(latestTrades, indent=2))
      
      #use e['lastday_price'] to get previous close amount ... or curPrice/float(e['lastday_price'])>=sellUpFromYesterday
      elif(curPrice/buyPrice>=sellUp or curPrice/closePrice>=sellUp):
        if(not e['symbol'] in [t.getName() for t in threading.enumerate()]): #if the thread is not found in names of the running threads, then start it (this stops multiple instances of the same stock thread)
          print("Trigger point reached on "+e['symbol']+". Seeing if it will go up...")
          triggerThread = threading.Thread(target=triggeredUp, args=(e, curPrice, buyPrice, closePrice, maxPrice, sellUpDn, latestTrades)) #init the thread
          triggerThread.setName(e['symbol']) #set the name to the stock symb
          triggerThread.start() #start the thread

#triggered selling-up - this is the one that gets multithreaded
def triggeredUp(symbObj, curPrice, buyPrice, closePrice, maxPrice, sellUpDn, latestTrades):
  global gainers
  print("Starting thread for "+symbObj['symbol'])
  
  while((curPrice/buyPrice>=maxPrice/buyPrice*sellUpDn or curPrice/closePrice>=maxPrice/closePrice*sellUpDn) and a.timeTillClose()>=30):
    curPrice = a.getPrice(symbObj['symbol'])
    maxPrice = max(maxPrice, curPrice)
    print(symbObj['symbol']+" - "+str(round(curPrice/buyPrice,2))+":"+str(round(maxPrice/buyPrice*sellUpDn,2))+" - "+str(round(curPrice/closePrice,2))+":"+str(round(maxPrice/closePrice,2)))
    a.o.time.sleep(3)
  
  print(a.createOrder("sell",symbObj['qty'],symbObj['symbol']))
  latestTrades[symbObj['symbol']] = {
                                     "tradeDate": str(a.o.dt.date.today()),
                                     "tradeType": "sell",
                                     "buyPrice": 0, #reset the avgBuyPrice to 0 after a sell
                                     "shouldSell": False
                                    }
  with open(a.o.c['File Locations']['latestTradesFile'],"w") as f:
    f.write(a.o.json.dumps(latestTrades, indent=2))
  #remove from gainers in case it sells after updateStockList has run
  if(symbObj['symbol'] in gainers):
    gainers.remove(symbObj['symbol'])


#buy int(buyPow/10) # of individual stocks. If buyPow>minBuyPow*buyPowMargin, then usablebuyPow=buyPow-minBuyPow
def check2buy(latestTrades, minBuyPow, buyPowMargin, minDolPerStock):
  usableBuyPow = float(a.getAcct()['cash']) #init as the current buying power
  if(buyPowMargin<1): #buyPowMargin MUST BE GREATER THAN 1 in order for it to work correctly
    raise("Error: withdrawlable funds margin is less than 1. Multiplier must be >=1")
  
  if(usableBuyPow>=minBuyPow*buyPowMargin): #if we have more buying power than the min plus some leeway, then reduce it to hold onto that buy pow
    print(f"Can safely withdrawl ${round(minBuyPow,2)}")
    usableBuyPow = usableBuyPow-minBuyPow*buyPowMargin #subtract the minBuyPow plus the margin
  elif(usableBuyPow>minBuyPow and usableBuyPow<minBuyPow*buyPowMargin):
    usableBuyPow = 0 #stop trading if we've started to eat into the margin, that way we don't overshoot
    
  if(len(gainers)>0):
    dolPerStock = max(minDolPerStock, usableBuyPow/len(gainers)) #if buyPow>(minDolPerStock*len(gainers)) then divvy up buyPow over gainers
  else:
    dolPerStock = minDolPerStock
    
  i=0 #index of gainers
  stocksBought = 0 #number of stocks bought
  
  stocks2buy = int(usableBuyPow/dolPerStock) #number of stocks to buy
  
  while(stocksBought<stocks2buy and i<len(gainers)):
    symb = gainers[i] #candidate stock to buy
    #TODO: in this conditional, also check that the gain isn't greater than ~75% of sellUp (e.g. must be <1.15 if sellUp=1.2)
    if(symb not in [t.getName() for t in threading.enumerate()]): #make sure the stock isn't trying to be sold already
      try: #check when it was traded last
        lastTradeDate = a.o.dt.datetime.strptime(latestTrades[symb]['tradeDate'],'%Y-%m-%d').date()
        lastTradeType = latestTrades[symb]['tradeType']
        try:
          avgBuyPrice = latestTrades[symb]['buyPrice']
        except Exception:
          avgBuyPrice = 0
      except Exception:
        lastTradeDate = a.o.dt.datetime.today().date()-a.o.dt.timedelta(1)
        lastTradeType = "NA"
        avgBuyPrice = 0
        
      #for some reason this check was being bypassed. This should be resolved in the updateStockList function where it removes any prospective stock to be bought from the list if it was sold today
      if(lastTradeType != "sell" or lastTradeDate < a.o.dt.datetime.today().date()): #make sure we didn't sell it today already
        if(a.isAlpacaTradable(symb)): #make sure it's tradable on the market
          curPrice = a.getPrice(symb)
          if(curPrice>0):
            shares2buy = int(dolPerStock/curPrice)
            orderText = a.createOrder("buy",shares2buy,symb,"market","day")
            #make sure it actually executed the order, then increment
            if(orderText.endswith('accepted')):
              print(orderText)
              #record the transaction
              latestTrades[symb] = { #set the avgBuyPrice to the average of the currentPrice and the previous avg (unless the prev avg<=0)
                                    "tradeDate": str(a.o.dt.date.today()),
                                    "tradeType": "buy",
                                    "buyPrice": (curPrice+avgBuyPrice)/(1+avgBuyPrice>0),
                                    "shouldSell": False
                                    }
              with open(a.o.c['File Locations']['latestTradesFile'],"w") as f:
                f.write(a.o.json.dumps(latestTrades, indent=2))
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
  gainers = [] #clear the gainer list
  #list of stocks that may gain in the near future as well as currently held stocks and their last gain date
  gainerDates = a.o.getGainers(list(dict.fromkeys(a.o.getList()+[e['symbol'] for e in a.getPos()]))) #combine nasdaq list & my stocks & remove duplicates - order doesn't matter
  #only add gainers who are not slated for a reverse stock split and have not already been traded today
  todaysTrades = a.getTrades(str(a.o.dt.date.today()))
  soldToday = [e['symbol'] for e in todaysTrades if e['side']=='sell']
  splitters = a.o.reverseSplitters()
  for e in list(gainerDates):
    # news = str(ns.scrape(e)).lower()
    # if(not ("reverse stock split" in news or "reverse-stock-split" in news) and (e not in soldToday)):
    if(e not in splitters and (e not in soldToday)):
      gainers.append(e)
  print(f"Done updating list - {len(gainers)} potential gainers")
  gStocksUpdated = True

def mark2sell():
  p = a.getPos()
  splitters = a.o.reverseSplitters()
  for e in p:
    print(f"{e['symbol']}\tmarked to sell? ",end="")
    # news = str(ns.scrape(e['symbol'])).lower()
    
    # shouldSell = "reverse stock split" in news or "reverse-stock-split" in news or "bankrupt" in news #sell before a reverse stock split or bankruptcy
    shouldSell = e in splitters
    print(shouldSell)
    with open(a.o.c['File Locations']['latestTradesFile'],"r") as f:
      latestTrades = a.o.json.loads(f.read())
    try:  
      latestTrades[e['symbol']]['shouldSell'] = shouldSell
    except Exception:
      latestTrades[e['symbol']] = {'shouldSell' : shouldSell}
    with open(a.o.c['File Locations']['latestTradesFile'],"w") as f:
      f.write(a.o.json.dumps(latestTrades, indent=2))

#mark stocks to be sold, then update the stock list (only meant to be run as a thread while market is closed)
def markAndUpdate():
  mark2sell()
  updateStockList()
