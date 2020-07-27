import requests, csv, os
from pandas import read_html

#get list of stocks from stocksUnder1 and marketWatch lists
def getList():
  #strt with this one. Will need to add logic to look at following pages
  #many of the options listed are optional and can be removed from the get request
  '''
https://www.marketwatch.com/tools/stockresearch/screener/results.asp 
TradesShareEnable=True 
TradesShareMax=5 
PriceDirEnable=False 
PriceDir=Up 
LastYearEnable=False 
TradeVolEnable=False 
BlockEnable=False
PERatioEnable=False 
MktCapEnable=False 
MovAvgEnable=False 
MovAvgType=Outperform 
MovAvgTime=FiftyDay 
MktIdxEnable=False 
MktIdxType=Outperform 
Exchange=NASDAQ 
IndustryEnable=False 
Industry=Accounting 
Symbol=True 
CompanyName=False 
Price=True 
Change=False 
ChangePct=False 
Volume=True 
LastTradeTime=False 
FiftyTwoWeekHigh=False 
FiftyTwoWeekLow=False 
PERatio=False 
MarketCap=False 
MoreInfo=True 
SortyBy=Symbol 
SortDirection=Ascending
ResultsPerPage=OneHundred
PagingIndex=800
  '''
  
  stockList = "test"
  return symbList



#get the history of a stock from the nasdaq api (date format is yyyy-mm-dd)
#returns as 2d array order of date,open,close,low,high,volume
def getHistory(symb, startDate, endDate): 
  url = f'https://www.nasdaq.com/api/v1/historical/{symb}/stocks/{startDate}/{endDate}/'
  #write to file after checking that the file doesn't already exist (we don't want to abuse the api)
  if(not os.isFile(symb+".csv")):
    csvTxt = requests.get(url, headers={"user-agent":"-"}).text
    f = open(symb+".csv","w")
    f.write(csvTxt)
  
  #read csv and convert to array

  return history


#checks whether something is a good buy or not (if not, return why - no initial jump or second jump already missed).
#if it is a good buy, return initial jump date
#same criteria as in getGainers() of other algo13sim
def goodBuy(history):


  if(<no jump>):
    return "no jump"
  elif(<second jump happened already>):
    return "missed it"
  else: #there was a jump, and the second jump hasn't happened yet
    return jumpDate



#just like in the other algo13sim, return a list of gainers and their initial jump date
def getGainers(symbList):

