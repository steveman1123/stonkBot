import requests, csv, os, time, re
from pandas import read_html

#get list of stocks from stocksUnder1 and marketWatch lists
def getList():
  #strt with this one. Will need to add logic to look at following pages
  #many of the options listed are optional and can be removed from the get request
  url = 'https://www.marketwatch.com/tools/stockresearch/screener/results.asp'
  params = {
    "TradesShareEnable" : "True", 
    "TradesShareMin" : "0.8",
    "TradesShareMax" : "5",
    "PriceDirEnable" : "False",
    "PriceDir" : "Up",
    "LastYearEnable" : "False",
    "TradeVolEnable" : "False",
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
  

  r = requests.get(url, params=params).text
  totalStocks = int(r.split("matches")[0].split("floatleft results")[1].split("of ")[1]) #get the total number of stocks in the list - important because they're spread over multiple pages
  symbList = []
  for i in range(0,totalStocks,100): #loop through the pages
    params['PagingIndex'] = i
    while True:
      try:
        r = requests.get(url, params=params).text
        break
      except Exception:
        print("No connection or other error encountered. Trying again...")
        time.sleep(3)
        continue
    symbList += read_html(r)[0]['Symbol'].values.tolist()


  #now that we have the marketWatch list, let's get the stocksunder1 list - essentially the getPennies() fxn from other files
  url = 'https://stocksunder1.org/nasdaq-penny-stocks/'
  while True:
    try:
      html = requests.post(url, params={"price":5,"volume":0,"updown":"up"}).content
      break
    except Exception:
      print("No connection, or other error encountered. Trying again...")
      time.sleep(3)
      continue

  tableList = read_html(html)
  try:
    symList = tableList[5][0:]['Symbol']
  except Exception:
    symList = tableList[5][1:][0] #this keeps changing (possibly intentionally - possibly due to switching btw windows and linux?)

  symList = [re.sub(r'\W+','',e.replace(' predictions','')) for e in symList] #strip "predictions" and any non alphanumerics

  symbList = list(set(symbList+symList)) #combine and remove duplicates
  return symbList





#get the history of a stock from the nasdaq api (date format is yyyy-mm-dd)
#returns as 2d array order of Date, Close/Last, Volume, Open, High, Low
def getHistory(symb, startDate, endDate): 
  #write to file after checking that the file doesn't already exist (we don't want to abuse the api)
  url = f'https://www.nasdaq.com/api/v1/historical/{symb}/stocks/{startDate}/{endDate}/'
  while True:
    try:
      r = requests.get(url, headers={"user-agent":"-"}).text #send request and store response
      break
    except Exception:
      print("No connection, or other error encountered. Trying again...")
      time.sleep(3)
      continue
  out = open(symb+'.csv','w') #write to file for later usage
  out.write(r)
  out.close()

  #read csv and convert to array
  with open(symb+".csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    out = [e for e in csv_reader]

  return out


#checks whether something is a good buy or not (if not, return why - no initial jump or second jump already missed).
#if it is a good buy, return initial jump date
#same criteria as in getGainers() of other algo13sim
def goodBuy(history):

  '''
  if(<no jump>):
    return "no jump"
  elif(<second jump happened already>):
    return "missed it"
  else: #there was a jump, and the second jump hasn't happened yet
    return jumpDate
  '''


#just like in the other algo13sim, return a list of gainers and their initial jump date
#def getGainers(symbList):

