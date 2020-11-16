#This module should be any function that doesn't require alpaca or keys to use

import json,requests,os,time,re,csv
import datetime as dt
from bs4 import BeautifulSoup as bs
from math import ceil

settingsFile = './stonkBot.config'

with open(settingsFile,"r") as f:
  c = json.loads(f.read())
stockDir = c['stockDataDir']

def isTradable(symb):
  isTradable = False
  while True:
    try:
      r = requests.request("GET","https://api.nasdaq.com/api/quote/{}/info?assetclass=stocks".format(symb), headers={"user-agent":"-"}, timeout=5).content
      break
    except Exception:
      print("No connection, or other error encountered in isTradable, trying again...")
      time.sleep(3)
      continue
  try:
    isTradable = bool(json.loads(r)['data']['isNasdaqListed'])
  except Exception:
    print(symb+" - Error in isTradable")

  return isTradable

#get list of stocks from stocksUnder1 and marketWatch lists
def getList():
  symbList = list()
  
  url = 'https://www.marketwatch.com/tools/stockresearch/screener/results.asp'
  #many of the options listed are optional and can be removed from the get request
  params = {
    "TradesShareEnable" : "True", 
    "TradesShareMin" : str(c['simMinPrice']),
    "TradesShareMax" : str(c['simMaxPrice']),
    "PriceDirEnable" : "False",
    "PriceDir" : "Up",
    "LastYearEnable" : "False",
    "TradeVolEnable" : "true",
    "TradeVolMin" : str(c['simMinVol']),
    "TradeVolMax" : "",
    "BlockEnable" : "False",
    "PERatioEnable" : "False",
    "MktCapEnable" : "False",
    "MovAvgEnable" : "False",
    "MktIdxEnable" : "False",
    "Exchange" : "NASDAQ",
    "IndustryEnable" : "False",
    "Symbol" : "True",
    "CompanyName" : "False",
    "Price" : "False",
    "Change" : "False",
    "ChangePct" : "False",
    "Volume" : "False",
    "LastTradeTime" : "False",
    "FiftyTwoWeekHigh" : "False",
    "FiftyTwoWeekLow" : "False",
    "PERatio" : "False",
    "MarketCap" : "False",
    "MoreInfo" : "False",
    "SortyBy" : "Symbol",
    "SortDirection" : "Ascending",
    "ResultsPerPage" : "OneHundred"
  }
  params['PagingIndex'] = 0 #this will change to show us where in the list we should be - increment by 100 (see ResultsPerPage key)
  
  while True:
    try:
      r = requests.get(url, params=params, timeout=5).text
      totalStocks = int(r.split("matches")[0].split("floatleft results")[1].split("of ")[1]) #get the total number of stocks in the list - important because they're spread over multiple pages
      break
    except Exception:
      print("No connection or other error encountered in getList (MW). Trying again...")
      time.sleep(3)
      continue
      
      
  print("Getting MarketWatch data...")
  for i in range(0,totalStocks,100): #loop through the pages (100 because ResultsPerPage is OneHundred)
    print(f"page {int(i/100)+1} of {ceil(totalStocks/100)}")
    params['PagingIndex'] = i
    while True:
      try:
        r = requests.get(url, params=params, timeout=5).text
        break
      except Exception:
        print("No connection or other error encountered in getList (MW). Trying again...")
        time.sleep(3)
        continue

    table = bs(r,'html.parser').find_all('table')[0]
    for e in table.find_all('tr')[1::]:
      symbList.append(e.find_all('td')[0].get_text())

  
  #now that we have the marketWatch list, let's get the stocksunder1 list - essentially the getPennies() fxn from other files
  print("Getting stocksunder1 data...")
  urlList = ['nasdaq','tech','biotech','marijuana','healthcare','energy']
  for e in urlList:  
    print(e+" stock list")
    url = 'https://stocksunder1.org/{}-penny-stocks/'.format(e)
    while True:
      try:
        html = requests.post(url, params={"price":5,"volume":0,"updown":"up"}, timeout=5).content
        break
      except Exception:
        print("No connection, or other error encountered (SU1). Trying again...")
        time.sleep(3)
        continue
    table = bs(html,'html.parser').find_all('table')[6] #6th table in the webpage - this may change depending on the webpage
    for e in table.find_all('tr')[1::]: #skip the first element that's the header
      #print(re.sub(r'\W+','',e.find_all('td')[0].get_text().replace(' predictions','')))
      symbList.append(re.sub(r'\W+','',e.find_all('td')[0].get_text().replace(' predictions','')))
  
  
  print("Removing Duplicates...")
  symbList = list(dict.fromkeys(symbList)) #combine and remove duplicates
  
  print("Done getting stock lists")
  return symbList

#get the history of a stock from the nasdaq api (date format is yyyy-mm-dd)
#returns as 2d array order of Date, Close/Last, Volume, Open, High, Low sorted by dates newest to oldest
def getHistory(symb, startDate, endDate):
  #try checking the modified date of the file, if it throws an error, just set it to yesterday
  try:
    modDate = dt.datetime.strptime(time.strftime("%Y-%m-%d",time.localtime(os.stat(stockDir+symb+'.csv').st_mtime)),"%Y-%m-%d").date() #if ANYONE knows of a better way to get the mod date into a date format, for the love of god please let me know
  except Exception:
    modDate = dt.date.today()-dt.timedelta(1)
  #write to file after checking that the file doesn't already exist (we don't want to abuse the api) or that it was edited more than a day ago
  if(not os.path.isfile(stockDir+symb+".csv") or modDate<dt.date.today()):
    #url = f'https://api.nasdaq.com/api/quote/{symb}/historical?assetclass=stocks&fromdate={startDate}&todate={enddate}' #currently only returns 14 days
    
    while True:
      try:
        url = f'https://www.nasdaq.com/api/v1/historical/{symb}/stocks/{startDate}/{endDate}' #old api url (depreciated?)
        r = requests.get(url, headers={"user-agent":"-"}, timeout=5).text #send request and store response - cannot have empty user-agent
        if(len(r)<10):
          startDate = str(dt.datetime.strptime(startDate,"%Y-%m-%d").date()-dt.timedelta(1)) #try scooting back a day if at first we don't succeed (sometimes it returns nothing for some reason?)
        if('html' in r or len(r)<10): #sometimes response returns invalid data. This ensures that it's correct (not html error or blank data)
          raise Exception('Returned invalid data') #sometimes the page will return html data that cannot be successfully parsed
        break
      except Exception:
        print("No connection, or other error encountered in getHistory. Trying again...")
        time.sleep(3)
        continue
    
    # with open(stckDir+symb+".json",'w') as out: #new api uses json
    with open(stockDir+symb+'.csv','w') as out: #write to file for later usage - old api used csv format
      out.write(r)
  
  #read csv and convert to array
  #TODO: see if we can not have to save it to a file if possible due to high read/writes - can also eliminate csv library
  #     ^ or at least research where it should be saved to avoid writing to sdcard
  with open(stockDir+symb+".csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    out = [[ee.replace('$','').replace('N/A','0') for ee in e] for e in csv_reader][1::] #trim first line to get rid of headers, also replace $'s and N/A volumes to calculable values
  
  return out

#checks whether something is a good buy or not (if not, return why - no initial jump or second jump already missed).
#if it is a good buy, return initial jump date
#this is where the magic really happens

def goodBuy(symb,days2look=c['simDays2look']): #days2look=how far back to look for a jump
  validBuy = "NA" #set to the jump date if it's valid
  if isTradable(symb):
    #calc price % diff over past 20 days (current price/price of day n) - current must be >= 80% for any
    #calc volume % diff over average past some days (~60 days?) - must be sufficiently higher (~300% higher?)
    
    days2wait4fall = c['simWait4fall'] #wait for stock price to fall for this many days
    startDate = days2wait4fall+c['simStartDateDiff'] #add 1 to account for the jump day itself
    firstJumpAmt = c['simFirstJumpAmt'] #stock first must jump by this amount (1.3=130% over 1 day)
    sellUp = c['simSellUp'] #% to sell up at
    sellDn = c['simSellDn'] #% to sell dn at
    
    #make sure that the jump happened in the  frame rather than too long ago
    volAvgDays = c['simVolAvgDays'] #arbitrary number to avg volumes over
    checkPriceDays = c['simChkPriceDays'] #check if the price jumped substantially over the last __ trade days
    checkPriceAmt = c['simChkPriceAmt'] #check if the price jumped by this amount in the above days (% - i.e 1.5 = 150%)
    volGain = c['simVolGain'] #check if the volume increased by this amount during the jump (i.e. 3 = 300% or 3x, 0.5 = 50% or 0.5x)
    volLoss = c['simVolLoss'] #check if the volume decreases by this amount during the price drop
    priceDrop = c['simPriceDrop'] #price should drop this far when the volume drops
    
    start = str(dt.date.today()-dt.timedelta(days=(volAvgDays+days2look)))
    end = str(dt.date.today())
    dateData = getHistory(symb, start, end)
    
    if(startDate>=len(dateData)-2): #if a stock returns nothing or very few data pts
      validBuy = "Few data points available"
    else:
      validBuy = "initial jump not found"
      while(startDate<min(days2look, len(dateData)-2) and float(dateData[startDate][1])/float(dateData[startDate+1][1])<firstJumpAmt):
        startDate += 1
        
        #if the price has jumped sufficiently for the first time
        if(float(dateData[startDate][1])/float(dateData[startDate+1][1])>=firstJumpAmt):
          
          avgVol = sum([int(dateData[i][2]) for i in range(startDate,min(startDate+volAvgDays,len(dateData)))])/volAvgDays #avg of volumes over a few days
          
          lastVol = int(dateData[startDate][2]) #the latest volume
          lastPrice = float(dateData[startDate][4]) #the latest highest price
  
          if(lastVol/avgVol>volGain): #much larger than normal volume
            #volume had to have gained
            #if the next day's price has fallen significantly and the volume has also fallen
            if(float(dateData[startDate-days2wait4fall][4])/lastPrice-1<priceDrop and int(dateData[startDate-days2wait4fall][2])<=lastVol*volLoss):
              #the jump happened, the volume gained, the next day's price and volumes have fallen
              dayPrice = lastPrice
              i = 1 #increment through days looking for a jump - start with 1 day before startDate
              # check within the the last few days, check the price has risen compared to the past some days, and we're within the valid timeframe
              while(i<=checkPriceDays and lastPrice/dayPrice<checkPriceAmt and startDate+i<len(dateData)):
                dayPrice = float(dateData[startDate+i][4])
                i += 1
              
              if(lastPrice/dayPrice>=checkPriceAmt): #TODO: read through this logic some more to determine where exactly to put sellDn
                #the price jumped compared to both the previous day and to the past few days, the volume gained, and the price and the volume both fell
                #check to see if we missed the next jump (where we want to strike)
                missedJump = False
                validBuy = "Missed jump"
                for e in range(0,startDate):
                  # print(str(dateData[e])+" - "+str(float(dateData[e][4])/float(dateData[e+1][1])) +" - "+ str(sellUp))
                  if(float(dateData[e][4])/float(dateData[e+1][1]) >= sellUp): #compare the high vs previous close
                    missedJump = True
                if(not missedJump):
                  validBuy = dateData[startDate][0] #return the date the stock initially jumped
    
  return validBuy #return a dict of valid stocks and the date of their latest jump
  

#get the ticker symbol and exchange of a company or return "-" if not found
def getSymb(company):
  url = "https://www.marketwatch.com/tools/quotes/lookup.asp" #this one is a little slow, it'd be nice to find a faster site
  while True: #get the html page with the symbol
    try:
      r = requests.get(url, params={"Lookup":company}, timeout=5).text
      break
    except Exception:
      print("No connection, or other error encountered in getSymb. Trying again...")
      time.sleep(3)
      continue
  
  try: #parse throgh html to find the table, symbol data, symbol, and exchange for it
    table = bs(r,'html.parser').find_all('table')[0]
    symbData = table.find_all('tr')[1].find_all('td')
    symb = str(symbData[0]).split('">')[2].split("<")[0]
    exch = str(symbData[2]).split('">')[1].split("<")[0]
  except Exception: #return blanks if invalid
    [symb, exch] = ["-","-"]
  return [symb, exch]


#get list of stocks pending FDA approvals
def getDrugList():
  while True: #get page of pending stocks
    try:
      r = requests.get("https://www.drugs.com/new-drug-applications.html", timeout=5).text
      break
    except Exception:
      print("No connection, or other error encountered in getDrugList. trying again...")
      time.sleep(3)
      continue
  
  try:
    arr = r.split("Company:</b>") #go down to stock list
    arr = [e.split("<br>")[0].strip() for e in arr][1::] #get list of companies
    arr = [getSymb(e) for e in arr] #get the symbols and exchanges of the companies
    arr = [e[0] for e in arr if e[1]=="NAS"] #get the nasdaq only ones
  except Exception:
    print("Bad data")
    arr = []
    
  #TODO: like in stonk2, set max price, but also check for price changes in the past few days/weeks to see if it's worth investing in

  return arr


#the new version of the getGainers function - uses the new functions getList, getHistory, and goodBuy
def getGainers(symblist):
  gainers = {}
  
  for i,e in enumerate(symblist):
    b = goodBuy(e)
    try:
      gainers[e] = [b, (dt.datetime.strptime(b,"%m/%d/%Y")+dt.timedelta(days=(7*5))).strftime("%m/%d/%Y")]
      print(f"({i+1}/{len(symblist)}) {e} - {b} - {gainers[e][1]}")
    except Exception:
      pass
  #TODO: once getDrugList() is finished, append the returned list to gainers
  return gainers

#TODO: add slave functionality
#check if the master is alive
def masterLives():
  '''
  i=0
  while i<3: #try reaching the master 3 times
    try:
      r = requests.request(url=c['masterAddress])
      if(r is something good): #if it does reach the master and returns good signal
        return True
      else: #if it does reach the master but returns bad signal (computer is on, but script isn't running)
        break
    except Exception:
      i+=1
  return False
  '''
  
  #TODO: may have to install flask or something to get it online seperately from the web server
  print("No slave functionality yet")
  return True



