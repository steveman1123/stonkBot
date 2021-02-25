#This module should be any function that doesn't require alpaca or keys to use

import json,requests,os,time,re,csv,sys,configparser
import datetime as dt
from bs4 import BeautifulSoup as bs
from math import floor, ceil

c = configparser.ConfigParser()
c.read('./stonkBot.config')

stockDir = c['File Locations']['stockDataDir']

def isTradable(symb):
  isTradable = False
  while True:
    try:
      r = requests.request("GET",f"https://api.nasdaq.com/api/quote/{symb}/info?assetclass=stocks", headers={"user-agent":"-"}, timeout=5).content
      break
    except Exception:
      print("No connection, or other error encountered in isTradable, trying again...")
      time.sleep(3)
      continue
  try:
    isTradable = bool(json.loads(r)['data']['isNasdaqListed'])
  except Exception:
    print(f"{symb} - Error in isTradable")

  return isTradable

#get list of stocks from stocksUnder1 and marketWatch lists
def getList():
  symbList = list()
  
  url = 'https://www.marketwatch.com/tools/stockresearch/screener/results.asp'
  #many of the options listed are optional and can be removed from the get request
  params = {
    "TradesShareEnable" : "True",
    "TradesShareMin" : str(c['Double Jump Params']['simMinPrice']),
    "TradesShareMax" : str(c['Double Jump Params']['simMaxPrice']),
    "PriceDirEnable" : "False",
    "PriceDir" : "Up",
    "LastYearEnable" : "False",
    "TradeVolEnable" : "true",
    "TradeVolMin" : str(c['Double Jump Params']['simMinVol']),
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

    try:
      table = bs(r,'html.parser').find_all('table')[0]
      for e in table.find_all('tr')[1::]:
        symbList.append(e.find_all('td')[0].get_text())
    except Exception:
      print("Error in MW website.")
  
  #now that we have the marketWatch list, let's get the stocksunder1 list - essentially the getPennies() fxn from other files
  print("Getting stocksunder1 data...")
  urlList = ['nasdaq','tech','biotech','marijuana','healthcare','energy']
  for e in urlList:  
    print(e+" stock list")
    url = f'https://stocksunder1.org/{e}-penny-stocks/'
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

#returns as 2d array order of Date, Close/Last, Volume, Open, High, Low sorted by dates newest to oldest (does not include today's info)
#get the history of a stock from the nasdaq api (date format is yyyy-mm-dd)
def getHistory(symb, startDate, endDate, maxTries=5):
  #try checking the modified date of the file, if it throws an error, just set it to yesterday

  try:
    modDate = dt.datetime.strptime(time.strftime("%Y-%m-%d",time.localtime(os.stat(stockDir+symb+'.csv').st_mtime)),"%Y-%m-%d").date() #if ANYONE knows of a better way to get the modified date into a date format, for the love of god please let me know
  except Exception:
    modDate = dt.date.today()-dt.timedelta(1)
  #write to file after checking that the file doesn't already exist (we don't want to abuse the api) or that it was edited more than a day ago
  if(not os.path.isfile(stockDir+symb+".csv") or modDate<dt.date.today()):
    
    getHistory2(symb, startDate, endDate)
    tries=maxTries
    while tries<maxTries: #only try getting history with this method a few times before trying the next method
      tries += 1
      try:
        url = f'https://www.nasdaq.com/api/v1/historical/{symb}/stocks/{startDate}/{endDate}' #old api url (depreciated?)
        r = requests.get(url, headers={"user-agent":"-"}, timeout=5).text #send request and store response - cannot have empty user-agent
        if(len(r)<10):
          startDate = str(dt.datetime.strptime(startDate,"%Y-%m-%d").date()-dt.timedelta(1)) #try scooting back a day if at first we don't succeed (sometimes it returns nothing for some reason?)
        if('html' in r or len(r)<10): #sometimes response returns invalid data. This ensures that it's correct (not html error or blank data)
          raise Exception('Returned invalid data') #sometimes the page will return html data that cannot be successfully parsed
        break
      except Exception:
        print(f"No connection, or other error encountered in getHistory for {symb}. Trying again...")
        time.sleep(3)
        continue
    
    with open(stockDir+symb+'.csv','w',newline='') as out: #write to file for later usage - old api used csv format
      if(tries>=maxTries):
        r = getHistory2(symb, startDate, endDate) #getHistory2 is slower/uses more requests, so not as good as getHistory, at least until we learn the api better
        r = [['Date','Close/Last','Volume','Open','High','Low']]+r
        csv.writer(out,delimiter=',').writerows(r)
      else:
        out.write(r)
  
  #read csv and convert to array
  #TODO: see if we can not have to save it to a file if possible due to high read/writes - can also eliminate csv library
  #     ^ or at least research where it should be saved to avoid writing to sdcard
  with open(stockDir+symb+".csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    out = [[ee.replace('$','').replace('N/A','0').strip() for ee in e] for e in csv_reader][1::] #trim first line to get rid of headers, also replace $'s and N/A volumes to calculable values
  return out


#use the new nasdaq api to return in the same format as getHistory
#this does NOT save the csv file
#TODO: shouldn't be an issue for this case, but here's some logic:
#   if(todate-fromdate<22 and todate>1 month ago): 0-1 days will be returned
def getHistory2(symb, startDate, endDate, maxTries=5):
  maxDays = 14 #max rows returned per request
  tries=1
  j = {}
  while tries<=maxTries: #get the first set of dates
    try:
      j = json.loads(requests.get(f'https://api.nasdaq.com/api/quote/{symb}/historical?assetclass=stocks&fromdate={startDate}&todate={endDate}',headers={'user-agent':'-'}).text)
      break
    except Exception:
      print(f"Error in getHistory2 for {symb}. Trying again ({tries}/{maxTries})...")
      time.sleep(3)
      pass
    tries += 1
  if(j['data'] is None or tries>=maxTries or j['data']['totalRecords']==0): #TODO: this could have a failure if the stock isn't found/returns nothing
    print("Failed to get history")
    return []
  else: #something's fucky with this api, jsyk
    if(j['data']['totalRecords']>maxDays): #get subsequent sets
      for i in range(1,floor(j['data']['totalRecords']/maxDays)):
        tries=1
        while tries<=maxTries: #magc number. This could be larger, but the larger it is, the longer it'll take to fail out of a process if it doesn't work
          #r = json.loads(requests.get(f'https://api.nasdaq.com/api/quote/{symb}/historical?assetclass=stocks&fromdate={startDate}&todate={endDate}&offset={i*maxDays+i}',headers={'user-agent':'-'}).text)
          #print(f"{symb}|{i}/{floor(j['data']['totalRecords']/maxDays)} - {len(j['data']['tradesTable']['rows'])}")
          #print(r['data']['tradesTable']['rows'])
          #j['data']['tradesTable']['rows'] += r['data']['tradesTable']['rows'] #append the sets together
          

          try:
            r = json.loads(requests.get(f'https://api.nasdaq.com/api/quote/{symb}/historical?assetclass=stocks&fromdate={startDate}&todate={endDate}&offset={i*maxDays+i}',headers={'user-agent':'-'}).text)
            j['data']['tradesTable']['rows'] += r['data']['tradesTable']['rows'] #append the sets together
            break
          except Exception:
            print(f"Error in getHistory2 for {symb} index {i}. Trying again ({tries}/{maxTries})...")
            time.sleep(3)
            pass
          tries += 1
    
    #format the data to return the same as getHistory
    #2d array order of Date, Close/Last, Volume, Open, High, Low sorted by dates newest to oldest
    try:
      out = [[e['date'],e['close'],e['volume'].replace(',',''),e['open'],e['high'],e['low']] for e in j['data']['tradesTable']['rows']]
    except Exception:
      out = []
      print("Failed to get history")
    return out

#return if the stock jumped today some %
def jumpedToday(symb,jump):
  url = f'https://api.nasdaq.com/api/quote/{symb}/summary?assetclass=stocks'
  tries=0
  maxTries = 3 #sometimes this one really hangs but it's not terribly important, so we set a max limit and just assume it didn't jump today if it fails
  while tries<maxTries:
    try:
      j = json.loads(requests.get(url,headers={'user-agent':'-'}).text)
      close = float(j['data']['summaryData']['PreviousClose']['value'].replace('$','').replace(',','')) #previous day close
      high = float(j['data']['summaryData']['TodayHighLow']['value'].replace('$','').replace(',','').split('/')[0]) #today's high, today's low is index [1]
      out = high/close>=jump
      break
    except Exception:
      print(f"Error in jumpedToday. Trying again ({tries+1}/{maxTries} - {symb})...")
      time.sleep(3)
      out=False
      pass
    tries+=1
  return out


#checks whether something is a good buy or not (if not, return why - no initial jump or second jump already missed).
#if it is a good buy, return initial jump date
#this is where the magic really happens
#TODO: separate this out into separate functions (should also end up going into a different file with the other functions relating only to the double jump algo)
def goodBuy(symb,days2look = int(c['Double Jump Params']['simDays2look'])): #days2look=how far back to look for a jump
  validBuy = "NA" #set to the jump date if it's valid
  if isTradable(symb):
    #calc price % diff over past 20 days (current price/price of day n) - current must be >= 80% for any
    #calc volume % diff over average past some days (~60 days?) - must be sufficiently higher (~300% higher?)
    
    days2wait4fall = int(c['Double Jump Params']['simWait4fall']) #wait for stock price to fall for this many days
    startDate = days2wait4fall + int(c['Double Jump Params']['simStartDateDiff']) #add 1 to account for the jump day itself
    firstJumpAmt = float(c['Double Jump Params']['simFirstJumpAmt']) #stock first must jump by this amount (1.3=130% over 1 day)
    sellUp = float(c['Double Jump Params']['simSellUp']) #% to sell up at
    sellDn = float(c['Double Jump Params']['simSellDn']) #% to sell dn at
    
    #make sure that the jump happened in the  frame rather than too long ago
    volAvgDays = int(c['Double Jump Params']['simVolAvgDays']) #arbitrary number to avg volumes over
    checkPriceDays = int(c['Double Jump Params']['simChkPriceDays']) #check if the price jumped substantially over the last __ trade days
    checkPriceAmt = float(c['Double Jump Params']['simChkPriceAmt']) #check if the price jumped by this amount in the above days (% - i.e 1.5 = 150%)
    volGain = float(c['Double Jump Params']['simVolGain']) #check if the volume increased by this amount during the jump (i.e. 3 = 300% or 3x, 0.5 = 50% or 0.5x)
    volLoss = float(c['Double Jump Params']['simVolLoss']) #check if the volume decreases by this amount during the price drop
    priceDrop = float(c['Double Jump Params']['simPriceDrop']) #price should drop this far when the volume drops
    
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
                if(not jumpedToday(symb, sellUp)): #history grabs from previous day and before, it does not grab today's info. Check that it hasn't jumped today too
                  for e in range(0,startDate):
                    # print(str(dateData[e])+" - "+str(float(dateData[e][4])/float(dateData[e+1][1])) +" - "+ str(sellUp))
                    if(float(dateData[e][4])/float(dateData[e+1][1]) >= sellUp): #compare the high vs previous close
                      missedJump = True
                  if(not missedJump):
                    validBuy = dateData[startDate][0] #return the date the stock initially jumped
    
  return validBuy
  

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
      r = requests.request(url = c['masterAddress])
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

#return stocks going through a reverse split (this list also includes ETFs)
def reverseSplitters():
  while True: #get page of upcoming stock splits
    try:
      r = json.loads(requests.get("https://api.nasdaq.com/api/calendar/splits", headers={"user-agent":"-"}, timeout=5).text)['data']['rows']
      break
    except Exception:
      print("No connection, or other error encountered in reverseSplitters. trying again...")
      time.sleep(3)
      continue
  out = []
  for e in r:
    try: #normally the data is formatted as # : # as the ratio, but sometimes it's a %
      ratio = e['ratio'].split(" : ")
      ratio = float(ratio[0])/float(ratio[1])
    except Exception: #this is where it'd go if it were a %
      ratio = float(e['ratio'][:-1])/100+1 #trim the % symbol and convert to a number
    
    out.append([e['symbol'],ratio])
  
  
  return [e[0] for e in out if e[1]<1]
  
  
  
