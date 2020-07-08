'''
look at week to week patterns after major jumps
i.e. we know a major jump happened, what happens over the next week? (~5 trading days)

'''
import json, requests
from pandas import read_html

keyFile = open("apikeys.key","r")
apiKeys = json.loads(keyFile.read())
keyFile.close()


#get list of common penny stocks under $price and sorted by gainers (up) or losers (down)
def getPennies(price=1,updown="up"):
  url = 'https://stocksunder1.org/most-volatile-stocks/'
  html = requests.post(url, params={"price":price,"volume":0,"updown":updown}).content
  tableList = read_html(html)
  # print(tableList)
  # symList = tableList[5][0:]['Symbol']
  
  symList = tableList[5][1:][0] #this keeps changing (possibly intentionally)
  symList = [e.replace(' predictions','') for e in symList]
  
#  print(tableList[5][0:]['Symbol'])
  return symList


#function to "buy" shares of stock
def buy(shares, price, bPow, equity):
  bPow = bPow - shares*price
  equity = equity + shares*price
  return [shares, bPow, equity, price]

#function to "sell" shares of stock
def sell(shares, price, bPow, equity):
  bPow = bPow + shares*price
  equity = equity - shares*price
  shares = 0
  return [shares, bPow, equity, price]


#function to sim the stocks and return the best 2 options
def simIt(symList):
	'''
  the idea is to look at what happens in the following days after a big jump
  '''
  #generate data files for each stock
  for symb in symList:
    print(symb)
    if(not os.path.isfile(symb+".txt")):
      # url = 'https://www.alphavantage.co/query'
      url = apiKeys["ALPHAVANTAGEURL"]
      params= { # NOTE: the information is also available as CSV which would be more efficient
        'apikey' : apiKeys["ALPHAVANTAGEKEY"],
        'function' : 'TIME_SERIES_DAILY', #daily resolution (open, high, low, close, volume)
        'symbol' : symb, #ticker symbol
        'outputsize' : 'full' #upt to 20yrs of data
      }
      response = requests.request('GET', url, params=params).text #send request and store response
      time.sleep(19) #max requests of 5 per minute for free alphavantage account, delay to stay under that limit
  
      out = open(symb+'.txt','w') #write to file for later usage
      out.write(response)
      out.close()
    
  return sortedSyms


