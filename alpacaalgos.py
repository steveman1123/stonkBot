import alpacafxns as a
import time, random, sys, json, threading
from datetime import date
import datetime as dt
from workdays import networkdays as nwd
sys.path.append('./Sim/algo13sim')
import algo13 as a13
# import alpaca_trade_api as tradeapi


#ALGO 1
def algo1():
  print("algo 1:\nbuy at market open\nif return >= X%, sell\nif return <= Y%, sell, rebuy a different stock\nsell at market close\nrepeat")
  if(a.marketIsOpen()):

    cashOnHand = float(a.getAcct()["cash"]) #avaiable cash to buy with
    maxPrice = 5 #should be 1,2, or 5 usually

    symbols = a.getVolatilePennies(maxPrice,'up')
    uniqueAvailable = len(symbols)

    num2Buy = int(uniqueAvailable*3/4) # of unique stocks to buy - don't do all of them, this should avoid too many repeats
    numShares = int(cashOnHand/maxPrice/num2Buy) # of shares of each stock to buy

    # symbols = a.getPennies(1,'up')
    min2hold = min(num2Buy, 5) #minnumber to go down to before selling all and restarting
    waitTime = 5 #time to wait (s) between checking again

    perc2sellup = 12 # sell at this % gain
    perc2selldn = 20 # sell at this % loss
    #TODO: add second perc to sell at based on some other factors (i.e. it hasn't changed much or something)

    while (timeTillClose()>=300): #go until ~5 min before market closes
      pos = a.getPos()
      if(len(pos)>=min2hold):
        for e in pos:
          diff = float(e["current_price"])-float(e["avg_entry_price"])
          # print(e)
          perc = diff/float(e["avg_entry_price"])*100
          if(diff>0 or perc <= -3/4*perc2selldn): #show the info when it gets close to failing
            print(e["symbol"]+" - " + str(perc)+"%")
          if((perc >= perc2sellup or perc <= -perc2selldn)): #if it meets the criteria to sell
            print(a.createOrder("sell",e["qty"],e["symbol"],"market","day"))
            if(perc<= -perc2selldn): #if it failed, rebuy a random stock
              a.buyRandom(1,symbols,numShares)
      else:
        a.sellAll(0)
        a.buyRandom(num2Buy,symbols,numShares)
      print("\n"+str(len(pos)) + " stocks remaining...\n")
      time.sleep(waitTime)

  a.sellAll(0)
  print("Market is Closed.")


#ALGO 2
def algo2():
  print("algo 2:\nbuy on the hour\nsell on the half hour\nrepeat")
  if(a.marketIsOpen()):
    num2Buy = 20 # of unique stocks to buy
    numShares = 10 # of shares of each stock to buy
    symbols = a.getVolatilePennies(5,'up')
    # symbols = a.getPennies(1,'up')

    thisMin = int(a.marketTime()[4]) #get market minute
    if(thisMin == 0): #buy on the hour
      print("Buying Random...")
      a.buyRandom(num2Buy,symbols,numShares)
    elif(thisMin == 30): #sell on half hour
      print("Selling All...")
      a.sellAll(0)
  else:
    print("Market is Closed")

#ALGO 3
def algo3():
  print("algo 3:\nrandomly buy/sell every x minutes")
  if(a.marketIsOpen()):
    num2Buy = 20 # of unique stocks to buy
    numShares = 10 # of shares of each stock to buy
    symbols = a.getVolatilePennies(5,'up')
    pos = a.getPos()
    # symbols = a.getPennies(1,'up')

    min2wait = 5

    if(int(a.marketTime()[4])%min2wait == 0):
      if(random.randint(0,1)):
        #buy from symbols list
        a.createOrder("buy",random.randint(1,numShares),symbols[random.randint(0,len(symbols)-1)],"market", "day")
      else:
        #sell from positions list
        rndStk = pos[random.randint(0,len(pos)-1)] #get a random stock that's held
        a.createOrder("sell",random.randint(1,int(rndStk["qty"])),rndStk["symbol"],"market", "day")

#ALGO 4
def algo4():
  print("algo 4:\nbuy  on market close\nhold or sell if return >=x%\nsell after 2 days")

  #if time till close <=x minutes, start buying
  #if return >x% or time since bought> 2days, sell


#ALGO 5
def algo5():
  print("algo 5:\nbuy monday\nsell friday")
  #if monday morning, buy
  #if friday afternoon, sell
  #if current price >x%, sell, rebuy something else

#ALGO 6
def algo6():
  print("algo 6:\nbuy every hour/half hour/x minutes, sell at end of day")

  #if time to buy, buy
  #if time till close <=x minutes, sell

#ALGO 7
def algo7():
  print("algo 7:\nbuy a bunch of volatile stocks\nif total portfolio value increased by X%, sell and hold there\nif total value decreased by Y%, sell aand hold there\nrepeat daily")
  #if it doesn't reach that by a certain time, then have secondary (and tertiary?) % to get to
  #if it's mostly negative by a certain time, then cut losses

  openTime = int(a.marketTime()[3]) #this assumes the script is running before market is open
  startPortVal = a.getAcct()["last_equity"]

  primaryPerc = 2 #sell everything if the porfolio reaches this gain
  time1 = openTime+3600*2 #by this time (2hrs after open)
  secondaryPerc = primaryPerc/2 #in case portfolio gain doesn't reach the primary percent
  time2 = openTime+int(3600*3.5) #by this time (3.5 hrs after open)
  tertiaryPerc = secondaryPerc/2
  time3 = openTime+3600*4 #break even time
  downPerc = 1 #sell if the portfolio drops below this percent after a certain time
  timeDn = openTime+3600*5 #currently not used - time2 is used in its place
  absMinPerc = 5 #biggest loss amount that we want at any point during the day

  wait2start = 60*15 #wait this long (s) after open to start trading
  #wait for market to settle to start trading
  # while(a.marketTime()[3]<(openTime+wait2start)):
  #   print("Market is open. Trading in "+str(round((wait2start-(a.marketTime()[3]-openTime))/60,2))+" minutes.")
  #   time.sleep(60)

  if(a.marketIsOpen()):
    cashOnHand = float(a.getAcct()["cash"]) #avaiable cash to buy with
    maxPrice = 1 #should be 1,2, or 5 usually
    symbols = a.getVolatilePennies(maxPrice,'up')
    uniqueAvailable = len(symbols)
    num2Buy = int(uniqueAvailable*3/4) # of unique stocks to buy - don't grab all from list, this should avoid too many repeats
    numShares = int(cashOnHand/maxPrice/num2Buy) # of shares of each stock to buy
    min2hold = min(num2Buy, 15) #minnumber to go down to before selling all and restarting
    waitTime = 5 #time to wait (s) between checking again
    perc2sellup = 12 # sell at this % gain
    perc2selldn = 20 # sell at this % loss

    while (timeTillClose()>=60): #go until ~2 min before market closes
      pos = a.getPos() #get held positions
      if(len(pos)>=min2hold): #as long as we havee more than the minimum
        for e in pos:
          diff = float(e["current_price"])-float(e["avg_entry_price"]) #check the gain/loss
          perc = diff/float(e["avg_entry_price"])*100 #get % change
          if(diff>0 or perc <= -3/4*perc2selldn): #show the info when it gets close to failing
            print(e["symbol"]+" - " + str(round(perc,2))+"%")
          if((perc >= perc2sellup or perc <= -perc2selldn)): #if it meets the criteria to sell
            print(a.createOrder("sell",e["qty"],e["symbol"],"market","day")) #sell that bitch
            if(perc<= -perc2selldn): #if it failed, rebuy a random stock
              a.buyRandom(1,symbols,numShares)
      else: #if we fall below minimum
        a.sellAll(0) #throw it all away
        a.buyFromTop(num2Buy,symbols,numShares) #and buy from the top again
      portPerc = (float(a.getAcct()["equity"])/float(startPortVal)-1)*100
      print("\n"+str(len(pos)) + " stocks held - Portfolio change: "+str(round(portPerc,2))+"% - "+str(timeTillClose())+" seconds till close\n")
      if(portPerc>=primaryPerc):
        a.sellAll(0)
        print("Done trading for the day! We reached the mark.")
        break
      elif(portPerc>=secondaryPerc and int(a.marketTime()[3])>=time1):
        a.sellAll(0)
        print("Done trading for the day! We got second best.")
        break
      elif(portPerc>=tertiaryPerc and int(a.marketTime()[3])>=time2):
        a.sellAll(0)
        print("Done trading for the day! We did okay, better than nothing.")
        break
      elif(round(portPerc,2)==0 and int(a.marketTime()[3])>=time3):
        a.sellAll(0)
        print("Done trading for the day! We broke even.")
        break
      elif((portPerc <= -downPerc) and int(a.marketTime()[3])>=timeDn):
        print()
        a.sellAll(0)
        print("Done trading for the day. We lost some today.")
        break
      elif(portPerc <= -absMinPerc):
        a.sellAll(0)
        print("Done trading for the day. We lost a fair amount today.")
        break

      time.sleep(waitTime)

  a.sellAll(0)
  print("Market is Closed.")




  '''
  if portfolio reaches primaryPerc by time1, sell all
  elif portfolio reaches secondaryPerc by time2, sell all
  elif portfolio reaches tertiaryPerc by time3, sell all
  elif portfolio breaks even by time 4, sell all
  elif
  '''


#ALGO 8
def algo8():
  print("algo 8:\nbuy a bunch of volatile stocks\nif stock return > portfolio return + some %, sell the stock, buy a new random one\nif portfolio return >= 2x target %, sellAll & stop for the day\nif portfolio return reached target %, but has since gone down, sellAll & stop for the day\nif portfolio return <= max allowed loss, then sellAll & stop for the day")

  openTime = int(a.marketTime()[3]) #this assumes the script is running before market is open
  startPortVal = a.getAcct()["last_equity"]

  maxPrice = 1
  symbols = a.getVolatilePennies(maxPrice,'up')

  percDiff = 2 #only sell if stock's return is this % higher than portfolio current gain/loss %
  targetPerc = 2 #shoot for this portfolio gain/day
  absMinPerc = 5 #biggest loss amount that we want at any point during the day (avoids major crashes)

  wait2start = 60*5 #wait this long (s) after open to start trading
  #wait for market to settle to start trading
  # while(a.marketTime()[3]<(openTime+wait2start)):
  #   print("Market is open. Trading in "+str(round((wait2start-(a.marketTime()[3]-openTime))/60,2))+" minutes.")
  #   time.sleep(60)

  if(a.marketIsOpen()):
    maxPrice = 1 #should be 1,2, or 5 usually
    symbols = a.getVolatilePennies(maxPrice,'up')
    uniqueAvailable = len(symbols)
    num2Buy = int(uniqueAvailable*3/4) # of unique stocks to buy - don't grab all from list, this should avoid too many repeats
    min2hold = 15 #minnumber to go down to before selling all and restarting
    waitTime = 5 #time to wait (s) between checking again
    perc2selldn = 20 # sell at this % loss
    targetPercMet = 0 # set flag if the target % has been met

    while (timeTillClose()>=60): #go until ~1 min before market closes
      cashOnHand = float(a.getAcct()["cash"])*0.5 #avaiable cash to buy with
      numShares = int(cashOnHand/maxPrice/num2Buy) # of shares of each stock to buy
      pos = a.getPos() #get held positions
      portPerc = (float(a.getAcct()["equity"])/float(startPortVal)-1)*100 #get % change of portfolio

      if(len(pos) >= min2hold): #as long as we have more than the minimum
        for e in pos:
          diff = float(e["current_price"])-float(e["avg_entry_price"]) #check the gain/loss
          perc = diff/float(e["avg_entry_price"])*100 #get % change

          if(perc >= 3/4*(portPerc+percDiff) or perc <= -3/4*perc2selldn): #show the info when it gets close to sell time
            print(e["symbol"]+" - " + str(round(perc,2))+"%")

          if((perc >= (portPerc+percDiff) or perc <= -perc2selldn)): #if it meets the criteria to sell
            print(a.createOrder("sell",e["qty"],e["symbol"],"market","day")) #sell that bitch
            a.buyRandom(1,symbols,numShares) #and buy a new random one
      else: #if we fall below minimum
        a.sellAll(0) #throw it all away
        a.buyFromTop(num2Buy,symbols,numShares) #and buy from the top again

      print("\n"+str(len(pos)) + " stocks held - Portfolio change: "+str(round(portPerc,2))+"% - "+str(timeTillClose())+" seconds till close\n")

      if(portPerc>=2*targetPerc): #if twice target % is reached, stop for the day
        a.sellAll()
        print("Target met x2! We done good. Done for the day.")
        break
      elif(portPerc>=targetPerc): #if target % is met, set the flag
        print("Target gain met! Seeing if we can go higher...")
        targetPercMet = 1
      elif(targetPercMet and portPerc<targetPerc): #if the flag is set, but the portfolio % is now less, stop for the day
        a.sellAll()
        print("We did well, but we done lost it. Done trading for the day.")
        break
      elif(portPerc <= -absMinPerc): #if portfolio % is sucking balls, just give up for the day
        a.sellAll()
        print("We lost it today. Calling it quits before too much is gone.")
        break
  else:
    print("Market is closed.")
  print("Done trading for the day. See you tomorrow!")


#ALGO 9
def algo9():
  print("algo 9:\nbuy a bunch of volatile\nif portfolio return<x% (close to 0) & stock return >= abs(portfolio return), sell stock\nif portfolio return >=x% & stock return >= y%, sell stock. If portfolio return >= min return or >= target return, sell all for the day")


#ALGO 10
def algo10():

  symb = 'SD' #ticker symbol
  length = 10 #days to hold out for
  sellUp = 9 #sell if the stock is up this far
  sellDn = 19 #sell if the stock falls this far

  # startPortfolio = float(a.getAcct()["portfolio_value"]) #portfolio balance at the beginning
  startPortfolio = 100.0

  portfolioGain = 20 #if portfolio value gains by this %, sell and wait till end of period
  portfolioLoss = 50 #if portfolio value falls by this %, sell and wait till end of period
  buyPrice = a.getBuyPrice(symb) #init last buy price
  sellPrice = 0 #init last sell price

  sharesHeld = a.getShares(symb) #get current held shares of the stock

  # startDate = date(2020,4,27)
  marketTime = a.marketTime() #do this to reduce number of API calls
  startDate = date(marketTime[0],marketTime[1],marketTime[2]) #date of initial investments
  today = date(marketTime[0],marketTime[1],marketTime[2]) #date to be contiuously updated
  # filename = "/srv/http/portfolio.json" #used on the serve to display public data

  while((today-startDate).days<=length): #while within the period
    # marketTime = a.marketTime()
    # today = date(marketTime[0],marketTime[1],marketTime[2]) #set today
    print("Day "+str((today-startDate).days)+" of "+str(length)) #show the current day
    # f = open(filename,'w') #open the json file to write to
    # f.write(a.json.dumps({"portfolioIncrease":float(a.getAcct()["portfolio_value"])/startPortfolio, "period":length,"daysIn":(today-startDate).days})) #write the json data for the server
    # f.close()  #close the json file
    tradeMade = 0 #reset daily trade counter
    if(a.marketIsOpen()):

      #check portfolio value
      if(float(a.getAcct()["portfolio_value"])>=((1+portfolioGain/100)*startPortfolio)):
        sellPrice = a.getPrice(symb)
        a.sellAll(0)
        tradeMade = 1
        print("Win Time: "+str(today-startDate)+" days")
        sharesHeld = a.getShares(symb)
        break
      elif((float(a.getAcct()["portfolio_value"])<=(1-portfolioLoss/100)) and (sharesHeld>0)):
        print("Portfolio Failed at "+str(a.marketTime())+" - Current Value: "+a.getAcct()["portfolio_value"]) #let me know what happened
        sellPrice = a.getPrice(symb)
        a.sellAll(0)
        tradeMade = 1
        sharesHeld = a.getShares(symb)

      #check stock value
      sharesHeld = a.getShares(symb) #get currently held shares
      stockVal = a.getPrice(symb) # get the stock's current value
      if(a.getShares(symb)==0 and stockVal>=sellPrice): #if we don't have shares, and and the price has increased since the last sale, buy
        buyPrice = int(float(a.getAcct()['buying_power'])/stockVal) #set "buy price", this is actually shares to buy
        print(a.createOrder("buy",buyPrice,symb,"market","day")) #may have to make a limit buy
        buyPrice = float(a.getBuyPrice(symb)) #get actual price bought at
      elif(sharesHeld>0 and (stockVal>=(1+sellUp/100)*buyPrice or stockVal<=(1-sellDn/100)*buyPrice)): #if shares are held and their value is sufficiently different to sell
        if(not tradeMade): #if a trade hasn't been made yet today
          if(today==startDate): #on the first day we buy
            #buy as much as we can afford
            if(sharesHeld==0): #if no shares held, buy some
              sharesHeld = int(float(a.getAcct()['buying_power'])/a.getPrice(symb)) #set # of shares to purchase based on price and current buying power
              print(a.createOrder("buy",sharesHeld,symb,"market","day")) #may have to make a limit buy
              buyPrice = float(a.getBuyPrice(symb)) #get actual price bought at
              sharesHeld = a.getShares(symb) #get actual shares held
              tradeMade = 1 #indicate that a trade has been made today
          else: #it's not the first day anymore
            #check portfolio value
            if(float(a.getAcct()["portfolio_value"])>=((1+portfolioGain/100)*startPortfolio)): #if portfolio reached target gain
              sellPrice = a.getPrice(symb) #get appx sell price
              a.sellAll(0) #sell everything
              tradeMade = 1 #set the flag
              print("Win Time: "+str(today-startDate)+" days")
              sharesHeld = a.getShares(symb) #update to actual shares held (should be 0)
              break #stop the loop
            elif((float(a.getAcct()["portfolio_value"])<=(1-portfolioLoss/100)) and (sharesHeld>0)): #if portfolio lost :(
              print("Portfolio lost too much. Selling out until we recover.")
              sellPrice = a.getPrice(symb) #get appx sell price
              a.sellAll(0) #sell everything
              sharesHeld = a.getShares(symb) #get the shares held
              tradeMade = 1 #set the flag

            #check stock value
            stockVal = a.getPrice(symb) # get the stock's current value
            sharesHeld = a.getShares(symb) #update shares held
            if(sharesHeld==0 and stockVal>=sellPrice): # if we don't have shares and the price has increased from the last sale (i.e. has recovered from a slide)
              buyPrice = int(float(a.getAcct()['buying_power'])/stockVal) #this is actually shares to buy
              print(a.createOrder("buy",buyPrice,symb,"market","day")) #may have to make a limit buy
              buyPrice = float(a.getBuyPrice(symb)) #get actual price bought at
            elif(sharesHeld>0 and (stockVal>=(1+sellUp/100)*buyPrice or stockVal<=(1-sellDn/100)*buyPrice)): #if we have shares and it's greater or less than our initial buying price
              print("Lost the stock :/") if stockVal<=(1-sellDn/100)*buyPrice else print("Won the stock :)")
              a.sellAll(0) #sell everything
      else: #market closed
        print("Done trading for the day.")

      time.sleep(60*15)
      print(str(a.marketTime())+" - portfolio Value: "+a.getAcct()["portfolio_value"])
    print(str(round(timeTillOpen()/60,2))+" minutes till open.")

    time.sleep(60*30) if timeTillOpen()>(60*30) else time.sleep(60*5)


#ALGO11 (improvement of algo10)
def algo11():

  #initial conditions
  symb = 'xspa' #symbol to work with
  timeLimit = 10 #trading days since start to stop
  startDate = date(2020,5,6) #day first started investing
  startPortVal = float(a.getAcct()['portfolio_value']) #starting portfolio value

  #selling constants (%)
  portSellUp = 20
  portSellDn = 25
  stockSellDn = 16
  stockSellUp = 2
  stockSellUpDn = 1

  #timing constants (s)
  countdown = 10
  longwait = 60*10
  shortWait = 30

  #variables
  tradeMadeToday = False #flag if a trade has been made today
  currentPortVal = 0
  currentStockVal = 0
  sellPrice = 0 #price stocks sold at - $/share
  shares2buy = 0 #number of shares to buy in a given order



  #this assumes that shares are held of the stock 'symb', or no shares are held at all
  while(True):
    maxStockVal = 0 #additional variable to set/reset after the time limit/period
    #additional functionailty to choose new stocks on some cirteria should go here

#at this point, all of the money should be in buying power

    #make sure that the shares are held in the correct stock, if not, prompt to sell
    if(a.getShares(symb)==0 and not tradeMadeToday):
      if(len(a.getPos())): #this shouldn't ever happen, but just in case, we error check
        print(str(a.getPos()).replace(',','\n')+"\n")
        print("Error: Shares already held other than "+symb)
        if(not a.sellAll(1)): #prompt user to sell all - returns 0 if cancelled, 1 if finished selling
          sys.exit("Only shares of '"+symb+"' are valid. Please sell all to proceed.") #restart if cancelled - program probably won't work otherwise
      else: #this should happen the most often - if we're sure no stocks are held, then we can buy some
        if(not a.marketIsOpen()): #wait until open, if it's not already
          print("Waiting till open to buy.")
          time.sleep(a.timeTillOpen())
        shares2buy = int(float(acctInfo['buying_power'])/a.getPrice(symb))
        print(a.createOrder("buy",shares2buy,symb,"market","day"))
        tradeMadeToday = True
        startDate = date.today()

#at this point, we should have as many shares as we can afford

    while(nwd(startDate,date.today())<=timeLimit): #as long as we're in the time limit
      if(not tradeMadeToday and a.marketIsOpen()):
        currentStockVal = a.getPrice(symb) # if(a.getShares(symb)) else currentStockVal = 0 #
        if(currentStockVal<(a.getBuyPrice(symb)*(1-stockSellDn/100))):
          print("Lost the stock")
          a.sellAll(0)
          sellPrice = a.getPrice(symb)
          tradeMadeToday = True

        elif(currentStockVal>=(a.getBuyPrice(symb)*(1+stockSellUp/100)) and a.getBuyPrice(symb)>0):
          print("Won the stock")
          while(currentStockVal>(maxStockVal*(1-stockSellUpDn/100))):
            time.sleep(shortwait)
            currentStockVal = a.getPrice(symb)
            maxStockVal = max(maxStockVal, currentStockVal)
            print("Current Stock Value: "+str(currentStockVal)+", Sell price:"+str(maxStockVal*(1-stockSellUpDn/100)))
          a.sellAll(0)
          tradeMadeToday = True


        acctInfo = a.getAcct()
        currentPortVal = float(acctInfo['portfolio_value'])
        if(currentPortVal<=startPortVal*(1-portSellDn/100)):
          print("Lost the portfolio")
          a.sellAll(0)
          sellPrice = a.getPrice(symb)
          # tradeMadeToday = True
          break

        elif(currentPortVal>=startPortVal*(1+portSellUp/100)):
          print("Won the portfolio!")
          a.sellAll(0)
          sellPrice = a.getPrice(symb)
          # tradeMadeToday = True
          break


      if(not tradeMadeToday and a.getShares(symb)==0):
        print("No trades today, and no shares held, so we're buying.")
        shares2buy = int(float(acctInfo['buying_power'])/a.getPrice(symb))
        print(a.createOrder('buy',shares2buy,symb,'market','day'))


      if(a.marketIsOpen() and not tradeMadeToday): #this enforces 1 trade per day only during market open
        print("Market is open, and no trades made today - Current Portfolio Value Change: "+str(a.getPortfolioChange(startPortVal))+"%")
        time.sleep(longwait)
      else:
        print(str(timeTillOpen())+" seconds till open. Be patient.")
        time.sleep(timeTillOpen()-countdown)
        tradeMadeToday = False #reset for the start of a new day
        for i in range(countdown,0,-1):
          print(i)
          time.sleep(1)
        print("Welcome to day "+str(nwd(startDate,date.today()))+" of "+str(timeLimit)+" - Current Portfolio Value: "+a.getAcct()['portfolio_value']+" | "+str(a.getPortfolioChange(startPortVal))+"% from start of period.")

    print("End of Period. Selling all and starting over.")
    a.sellAll(0)
    tradeMadeToday = True
    startPortVal = float(a.getAcct()['portfolio_value'])
    startDate = date.today()


#ALGO 12 - based on Algo 11, only buy near market close
def algo12():
#TODO: fix sellAll instances so that it will only record in the event that we actually made trades
  f = open("algo12.txt","r") #contains json info regarding trading
  j = a.json.loads(f.read())
  f.close()
  
  symb = j['symb']
  d = j["periodDateStart"].split("-")
  periodStartDate = date(int(d[0]),int(d[1]),int(d[2]))
  periodStartVal = float(j["periodPortStart"])

  d = j["lastTradeDate"].split("-")
  lastTradeDate = date(int(d[0]),int(d[1]),int(d[2]))
  lastSellPrice = float(j["lastSellPrice"])
  maxPrice = 0
  # minPrice = 100000 #may be used later in trying to get the best buy
  currentPrice = 0
  shares2buy = 0
  buyPrice = 0

  
  period = 10 #length of period (d)
  sellUp = 5
  sellUpDn = 3
  sellDn = 16
  # buyDnUp = 1
  portGain = 20
  portLoss = 25
  
  timeFromClose = 300 #seconds from close to start analyzing to buy
  timeSinceStart = 300 #seconds from start to analyze to sell (before infrequent checking)
  
  shortTime = 2
  medTime = 20
  longTime = 60*10
  
  while True:
    #while the market is still alive
    print("\nMarket is alive")
    print("Today is "+str(date.today())+", the period start date is "+str(periodStartDate))
    print("Day "+str(nwd(periodStartDate,date.today())-1)+" of "+str(period))
    while (nwd(periodStartDate,date.today())-1<period):
      #while within the period
      print("We're within the period.")

      [openTime, closeTime] = a.openCloseTimes(str(date.today())) #get the open and close times of today

      while (a.marketIsOpen() and date.today()>lastTradeDate):
        #while the market is open on a given day (that we haven't traded yet)
        print("\nMarket is open, and no trades made yet")
        print("Time is: "+str(a.dt.now()))
        
        
        if(a.getShares(symb)>0): #only check to sell if we have shares in the first place
          print("We have shares")
          buyPrice = a.getBuyPrice(symb) #set var to avoid lots of redundant calls
          while((a.dt.now()-openTime).seconds<timeSinceStart):
            #while we're near the open time
            currentPrice = a.getPrice(symb) #set var to avoid lots of redundant calls
            print(str((a.dt.now()-openTime).seconds)+"s since open | stock change "+str(round((currentPrice/buyPrice-1)*100,2))+"%")
            #check frequently to sell
            if(currentPrice>buyPrice*(1+sellUp/100)):
              #if the stock price has reached the sell limit
              print("Stock has reached limit - up "+str(round(100*(currentPrice/buyPrice-1),2)+"%"))
              maxPrice = max(maxPrice, currentPrice)
              if(currentPrice<=maxPrice*(1-sellUpDn/100)):
                print("Sell up conditions met.")
                if(a.sellAll(0)):
                  #set trade flag
                  lastTradeDate = date.today()
                  lastSellPrice = currentPrice
                  j['lastTradeDate'] = str(lastTradeDate)
                  j['lastSellPrice'] = lastSellPrice
              time.sleep(shortTime) #we're excited, so check often
            else:
              time.sleep(medTime) #only check every so often
          
        if(lastTradeDate<date.today()):
          portVal = float(a.getAcct()['portfolio_value'])
          print("Checking portfolio status")
          if(portVal>periodStartVal*(1+portGain/100) or portVal<periodStartVal*(1-portLoss/100)):
            print("Portfolio won or lost - "+str(round(portVal/periodStartVal,2))+"%")
            if(a.sellAll(0)):
              periodStartDate = a.date.today()
              periodStartVal = portVal
              lastTradeDate = a.date.today()
              lastSellPrice = a.getPrice(symb)
              j['lastTradeDate'] = str(lastTradeDate)
              j['lastSellPrice'] = lastSellPrice
              j['periodStartDate'] = periodStartDate
              j['poeriodPortStart'] = periodStartVal

              #record the end of the period data
              portVal = float(a.getAcct()['portfolio_value'])
              print("Portfolio Value: $"+str(round(portVal,2)))
              f = open("alpacaPortValues.txt","a")
              f.write("\n"+str(date.today())+","+str(portVal))
              f.close()

              print("Starting period over.")
            break
          else:
            print("Portfolio change: "+str(round((portVal/periodStartVal-1)*100,2))+"%")
        else:
          break
          
        if(lastTradeDate<date.today()):
          print("No trades made yet today.")
          while(a.timeTillClose()<=timeFromClose):
            #while we're close to the end of the day
            print("Close to closing | "+str(a.dt.now())+" / "+str(closeTime))
            #buy if no shares held, or sell if it reaches the sellUp % method
            currentPrice = a.getPrice(symb)
            maxPrice = 0
            
            if(a.getShares(symb)==0):
              print("No shares held. Buying.")
#include buyDnUp & minPrice here
              shares2buy = int(float(a.getAcct()['buying_power'])/currentPrice)
              print(a.createOrder("buy",shares2buy,symb,"market","day"))
              lastTradeDate = a.date.today()
              j['lastTradeDate'] = str(lastTradeDate)
              break
            elif(currentPrice>=a.getBuyPrice(symb)*(1+sellUp/100)):
              print("Shares still held, and price is going up")
              while(currentPrice>=maxPrice*(1-sellUpDn) and a.timeTillClose()>shortTime*2):
                print("Time left: "+str(a.timeTillClose())+"s | Stock change: "+str(round(currentPrice/a.getBuyPrice(symb),2)-1)+"%")
                currentPrice = a.getPrice(symb)
                maxPrice = max(maxPrice,currentPrice)
                time.sleep(shortTime)
              if(currentPrice>=maxPrice*(1-sellUpDn)): #if the price is still up (hasn't started dropping yet), then wait till next morning to sell
                print("Price is still up, but market is closing. Will continue tomorrow.")
              else:
                if(a.sellAll(0)):
                  lastTradeDate = a.date.today()
                  lastSellPrice = currentPrice
                  j['lastTradeDate'] = str(lastTradeDate)
                  j['lastSellPrice'] = lastSellPrice
                break
            
            time.sleep(medTime)
          
          #if we're at any other time of the day
          #check slow - only sell
          if(lastTradeDate<a.date.today() and a.getShares(symb)>0):
            if(a.getPrice(symb)>=a.getBuyPrice(symb)*(1+sellUp/100)):
              print("Price going up")
              maxPrice = 0
              while(currentPrice>=maxPrice*(1-sellUpDn/100)):
                currentPrice = a.getPrice(symb)
                maxPrice = max(maxPrice,currentPrice)
                print("Current Price: "+str(currentPrice)+", Max Price: "+str(maxPrice))
                time.sleep(shortTime)
              if(a.sellAll(0)):
                lastSellPrice = currentPrice
                lastTradeDate = a.date.today()
                j['lastTradeDate'] = str(lastTradeDate)
                j['lastSellPrice'] = lastSellPrice
              break
          time.sleep(min(longTime,abs(a.timeTillClose()-timeFromClose))) #in case we're too close to the closing time, we don't want to overrun it
        else:
          break
        
        
        
      # set values and wait for the market to open again
      print("Done trading for the day.")
      f = open("algo12.txt","w")
      f.write(a.json.dumps(j))
      f.close()
      maxPrice = 0
      currentPrice = 0
      shares2buy = 0
      print("Current Time: "+str(a.marketTime()))
      print("Will resume in "+str(a.timeTillOpen())+" seconds")
      time.sleep(a.timeTillOpen())
      
    #sell all at end of period and reset values
    print("End of period. Selling all and resetting.")
    if(a.sellAll(0)): #sell everything at the end of the period
      #record the end of the period data
      portVal = float(a.getAcct()['portfolio_value'])
      print("Portfolio Value: $"+str(round(portVal,2)))
      f = open("alpacaPortValues.txt","a")
      f.write("\n"+str(date.today())+","+str(portVal))
      f.close()
      
      #record the trading info
      lastTradeDate = date.today()
      j['lastTradeDate'] = str(lastTradeDate)
      j['periodDateStart'] = str(date.today())
      j['periodPortStart'] = a.getAcct()['portfolio_value']
      maxPrice = 0
      currentPrice = 0
      shares2buy = 0
      f = open("algo12.txt","w")
      f.write(a.json.dumps(j))
      f.close()
    print("Current Time: "+str(a.marketTime()))
    print("Will resume in "+str(a.timeTillOpen())+" seconds")
    time.sleep(a.timeTillOpen())
    
    
  '''
  Algo12 outline (probably wrong now):
  
  only buy at/near close, and sell at open EXCEPT
  during the day:
    check the price slowly:
      if currentPrice > buyPrice:
        check faster:
          if price > sellup perc:
            check faster:
              if price drops sellUpDownPerc:
                sell
                if portfolio gain reached:
                  reset values
                  stop trading for period
                else:
                  set sellPrice
                  stop trading for the day
              else:
                keep checking
          else:
            keep checking
      else:
        if near open:
          if price drops sellDnPerc:
            sell
            set sellPrice
  
  near close:
    if sharesNotHeld:
      if currentPrice >= sellPrice:
        buy
        set buyPrice
    else:
      if stock gain reached:
        wait till triggered to sell or market closes:
          wait
        if market closed:
          wait till morning to trade
        else:
          sellAll
    '''



#generates list of potential gainers, trades based off amount of cash
#TODO: check if stock is up, then don't buy today, only look to sell - easier equiv solution: only buy near close
#TODO: check if currently held stock already peaked (i.e. we missed it while holding it) - if it did then lower expectations and try to sell at a profit still
#TODO: setup web interface to viewbaic stock/portfolio data without having to log in
#TODO: keep gainers date and estimate days until jump (appx 5 weeks after first jump date +/- 3 weeks)
def algo13():
  a13.init('../stockStuff/apikeys.key','./Sim/algo13sim/algo13.json', '../stockStuff/stockData/') #init settings and API keys, and stock data directory
  '''
  buy/sell logic:
  - if cash<some amt (reduced cash mode)
    - buy max of 10 unique from list
  - else (standard mode)
    buy as many as we can off the list generated by the sim
  - if cash<10 (low cash mode)
    - buy max of 5 unique from list
  - if portVal<5 (bottom out mode)
    - error, sell all and stop trading

  - stop loss at ~60%
  - limit gain at ~25%
  '''
  minPortVal = 5 #stop trading if portfolio reaches this amount
  reducedCash = 100 #enter reduced cash mode if portfolio reaches under this amount
  reducedBuy = 10 #buy this many unique stocks if in reduced cash mode
  lowCash = 10 #enter low cash mode if portfolio reaches under this amount
  lowBuy = 5 #buy this many unique stocks if in low cash mode
  minCash = 1 #buy until this amt is left in buying power/cash balance

  sellUp = 1+.2 #trigger point. Additional logic to see if it goes higher
  sellDn = 1-.3 #limit loss
  sellUpDn = 1-.02 #sell if it triggers sellUp then drops sufficiently
  
  gainers = []
  
  if(date.today().weekday()<5): #not saturday or sunday
    gainers = list(a13.getGainers(a13.getPennies())) #list of stocks that may gain in the near future
    f = open("../stockStuff/latestTrades13.json","r")
    latestTrades = json.loads(f.read())
    f.close()

  portVal = float(a.getAcct()['portfolio_value'])

  #TODO (optional): change last tradedate stuff - https://alpaca.markets/docs/api-documentation/api-v2/account-activities/
  while portVal>minPortVal:
    random.shuffle(gainers) #randomize list so when buying new ones, they won't always choose the top of the original list
    
    if(a.marketIsOpen()):
      print("\nMarket is open")
      f = open("../stockStuff/latestTrades13.json","r")
      latestTrades = json.loads(f.read())
      f.close()
      
      portVal = float(a.getAcct()['portfolio_value'])
      print("Portfolio val is $"+str(portVal)+". Sell targets are "+str(sellUp)+" or "+str(sellDn))
      
      #check here if the time is close to close - in the function, check that the requested stock didn't peak today
      check2buy(gainers, latestTrades, minPortVal,reducedCash,reducedBuy,lowCash,lowBuy,minCash)
              
      
      print("Tradable Stocks:")
      check2sell(a.getPos(), latestTrades, sellDn, sellUp, sellUpDn)
      time.sleep(60)
      
    else:
      print("Market closed. Will update stock list 1 hour before next open.")
      if(dt.date.today().weekday()<4): #mon-thurs
        tto = a.timeTillOpen()
      else: #fri-sun
        tto = (a.openCloseTimes(str(dt.date.today()+dt.timedelta(days=7-dt.date.today().weekday())))[0]-dt.datetime.now()).seconds
      
      print("Opening in "+str(int(tto/60))+" minutes")
      time.sleep(tto-3600) if(tto-3600>0) else time.sleep(tto)
      print("Updating stock list")
      gainers = list(a13.getGainers(a13.getPennies())) #list of stocks that may gain in the near future
      tto = a.timeTillOpen()
      print("Market will open in "+str(int(tto/60))+" minutes.")
      time.sleep(tto)





#for algo13 - check to sell a list of stocks
def check2sell(symList, latestTrades, sellDn, sellUp, sellUpDn):
  for e in symList:
    try:
      lastTradeDate = dt.datetime.strptime(latestTrades[e['symbol']][0],'%Y-%m-%d').date()
      lastTradeType = latestTrades[e['symbol']][1]
    except Exception:
      lastTradeDate = date.today()-dt.timedelta(1)
      lastTradeType = "NA"
    
    #TODO: move this into its own function and make it its own thread
    if(lastTradeDate<date.today() or lastTradeType=="sell" or float(e['current_price'])/float(e['avg_entry_price'])>=1.75): #prevent selling on the same day as a buy (only sell if only other trade today was a sell or price increased substantially)
      buyPrice = float(e['avg_entry_price'])
      curPrice = float(e['current_price'])
      maxPrice = 0
      print(e['symbol']+"\t-\tqty: "+e['qty']+"\t-\tchange: "+str(round(curPrice/buyPrice,2)))
  
      if(curPrice/buyPrice<=sellDn):
        print("Lost it on "+e['symbol'])
        print(a.createOrder("sell",e['qty'],e['symbol']))
        latestTrades[e['symbol']] = [str(date.today()), "sell"]
        f = open("../stockStuff/latestTrades13.json","w")
        f.write(json.dumps(latestTrades, indent=2))
        f.close()
      elif(curPrice/buyPrice>=sellUp):
        print("Trigger point reached on "+e['symbol']+". Seeing if it will go up...")
        # triggeredUp(e, curPrice, buyPrice maxPrice, sellUpDn, latestTrades)
        triggerThread = threading.Thread(target=triggeredUp, args=(e, curPrice, buyPrice, maxPrice, sellUpDn, latestTrades))
        triggerThread.start()



#for aglo13 - triggered selling-up - this is the one that gets multithreaded
def triggeredUp(symbObj, curPrice, buyPrice, maxPrice, sellUpDn, latestTrades):
  while(curPrice/buyPrice>=maxPrice/buyPrice*sellUpDn and a.timeTillClose()>=30):
    curPrice = a.getPrice(symbObj['symbol'])
    maxPrice = max(maxPrice, curPrice)
    print(symbObj['symbol']+" - "+str(round(curPrice/buyPrice,2))+" - "+str(round(maxPrice/buyPrice*sellUpDn,2)))
    time.sleep(3)
  
  print(a.createOrder("sell",e['qty'],e['symbol']))
  latestTrades[e['symbol']] = [str(date.today()), "sell"]
  f = open("../stockStuff/latestTrades13.json","w")
  f.write(json.dumps(latestTrades, indent=2))
  f.close()


#for algo13 - whether to buy a stock or not
def check2buy(gainers, latestTrades, minPortVal, reducedCash, reducedBuy, lowCash, lowBuy, minCash):
  acct = a.getAcct()
  portVal = float(acct['portfolio_value'])
  buyPow = float(acct['buying_power'])
  #TODO: check here for if close to close and if max of today was sufficiently high to trigger a sell (second bump) - if triggered, don't buy, just skip it
  if(buyPow>reducedCash): #in normal operating mode
    print("Normal Operation Mode. Available Buying Power: $"+str(buyPow))
    #div cash over all gainers
    for e in gainers:
      shares2buy = int((buyPow/len(gainers))/a.getPrice(e))
      try:
        lastTradeDate = dt.datetime.strptime(latestTrades[gainers[i]][0],'%Y-%m-%d').date()
        lastTradeType = latestTrades[gainers[i]][1]
      except Exception:
        lastTradeDate = date.today()-dt.timedelta(1)
        lastTradeType = "NA"
        
      if(shares2buy>0 and (lastTradeDate<date.today() or lastTradeType=="NA" or lastTradeType=="buy")):
        print(a.createOrder("buy",shares2buy,e,"market","day"))
        latestTrades[e] = [str(date.today()), "buy"]
        f = open("../stockStuff/latestTrades13.json","w")
        f.write(json.dumps(latestTrades, indent=2))
        f.close()
  else:
    if(buyPow>lowCash): #in reduced cash mode
      print("Reduced Cash Mode. Available Buying Power: $"+str(buyPow))
      #div cash over $reducedBuy stocks
      for i in range(min(reducedBuy,len(gainers))):
        shares2buy = int((buyPow/reducedBuy)/a.getPrice(gainers[i]))
        try:
          lastTradeDate = dt.datetime.strptime(latestTrades[gainers[i]][0],'%Y-%m-%d').date()
          lastTradeType = latestTrades[gainers[i]][1]
        except Exception:
          lastTradeDate = date.today()-dt.timedelta(1)
          lastTradeType = "NA"
          
        if(shares2buy>0 and (lastTradeDate<date.today() or lastTradeType=="NA" or lastTradeType=="buy")):
          print(a.createOrder("buy",shares2buy,gainers[i],"market","day"))
          latestTrades[gainers[i]] = [str(date.today()), "buy"]
          f = open("../stockStuff/latestTrades13.json","w")
          f.write(json.dumps(latestTrades, indent=2))
          f.close()
    else:
      if(buyPow>minCash): #in low cash mode
        print("Low Cash Mode. Available Buying Power: $"+str(buyPow))
        #div cash over $lowBuy cheapest stocks in list
        for i in range(min(lowBuy,len(gainers))):
          shares2buy = int((buyPow/lowBuy)/a.getPrice(gainers[i]))
          try:
            lastTradeDate = dt.datetime.strptime(latestTrades[gainers[i]][0],'%Y-%m-%d').date()
            lastTradeType = latestTrades[gainers[i]][1]
          except Exception:
            lastTradeDate = date.today()-dt.timedelta(1)
            lastTradeType = "NA"
            
          if(shares2buy>0 and (lastTradeDate<date.today() or lastTradeType=="NA" or lastTradeType=="buy")):
            print(a.createOrder("buy",shares2buy,gainers[i],"market","day"))
            latestTrades[gainers[i]] = [str(date.today()), "buy"]
            f = open("../stockStuff/latestTrades13.json","w")
            f.write(json.dumps(latestTrades, indent=2))
            f.close()
      else:
        if(buyPow>minCash):
          print("Buying power is greater than minCash, and less than lowCash - TODO")
          #TODO: if remaining cash>minCash but <lowCash, find the cheapest one in gainers list, & invest the rest there
          
        if(portVal<=minPortVal): #bottom out mode
          a.sellAll(0) #TODO: replace this with a loop to avoid buying/selling on same day
          for e in latestTrades:
            latestTrades[e] = [str(date.today()),"sell"]
          f = open("../stockStuff/latestTrades13.json","w")
          f.write(json.dumps(latestTrades, indent=2))
          f.close()
          print("Bottom Out Mode. Available Buying Power: $"+str(buyPow))
          # break
        else: #low cash but high portfolio means all is invested
          print("Portfolio Value: $"+str(portVal)+", Available Buying Power: $"+str(buyPow))
          
