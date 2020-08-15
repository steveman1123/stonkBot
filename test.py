from bs4 import BeautifulSoup as bs
import requests, re, math, time
'''
html_string = requests.get("https://stocksunder1.org/nasdaq-penny-stocks/").text

table = BeautifulSoup(html_string, 'html.parser').find_all('table')[6]

slist = list()
for e in table.find_all('tr')[1::]:
  slist.append(re.sub(r'\W+','',e.find_all('td')[0].get_text().replace(' predictions','')))

print(slist)
'''


 
url = 'https://www.marketwatch.com/tools/stockresearch/screener/results.asp'
  #many of the options listed are optional and can be removed from the get request
params = {
    "TradesShareEnable" : "True", 
    "TradesShareMin" : "0.8",
    "TradesShareMax" : "5",
    "PriceDirEnable" : "False",
    "PriceDir" : "Up",
    "LastYearEnable" : "False",
    "TradeVolEnable" : "true",
    "TradeVolMin" : "300000",
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
    r = requests.get(url, params=params).text
    totalStocks = int(r.split("matches")[0].split("floatleft results")[1].split("of ")[1]) #get the total number of stocks in the list - important because they're spread over multiple pages
    break
  except Exception:
    print("No connection or other error encountered. Trying again...")
    time.sleep(3)
    continue
      
symbList = list()      
print("Getting MarketWatch data...")
for i in range(0,totalStocks,100): #loop through the pages (100 because ResultsPerPage is OneHundred)
  print(f"page {int(i/100)+1} of {math.ceil(totalStocks/100)}")
  params['PagingIndex'] = i
  while True:
    try:
      r = requests.get(url, params=params).text
      break
    except Exception:
      print("No connection or other error encountered. Trying again...")
      time.sleep(3)
      continue

  #symbList += read_html(r)[0]['Symbol'].values.tolist()
  table = bs(r,'html.parser').find_all('table')[0]

  for e in table.find_all('tr')[1::]:
    symbList.append(e.find_all('td')[0].get_text())

print(symbList)
print(len(symbList))