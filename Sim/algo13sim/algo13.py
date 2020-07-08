'''
look at week to week patterns after major jumps
i.e. we know a major jump happened, what happens over the next week? (~5 trading days)

'''
import json, requests,os,time
from pandas import read_html
from matplotlib import pyplot as plt

keyFile = open("apikeys.key","r")
apiKeys = json.loads(keyFile.read())
keyFile.close()

settingsFile = open("algo13.json","r")
someSettings = json.loads(settingsFile.read())
settingsFile.close()


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


#function to sim the stocks and return the top 5
def simIt(symList):
  '''
  the idea is to look at what happens in the following days after a big jump
  '''
  #generate data files for each stock
  print("Getting stock data...")
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
      
    
    #gather info about single stock
    stonkFile = open(symb+'.txt','r') #open the file containing stonk data
    stonkData = json.loads(stonkFile.read()) #read in as json data
    stonkFile.close()
  
    dateData = stonkData[list(stonkData.keys())[1]] #time series (daily) - index 0=meta data, 1=stock data
    period = min(someSettings['periodLength'],len(dateData)-1) #how long for period
    
    dates = [e for e in dateData]
    lows = [float(dateData[e]['3. low']) for e in dateData]
    highs = [float(dateData[e]['2. high']) for e in dateData]
    opens = [float(dateData[e]['1. open']) for e in dateData]
    closes = [float(dateData[e]['4. close']) for e in dateData]
    volumes = [float(dateData[e]['5. volume']) for e in dateData]
    volatility = [(highs[i]-lows[i])/lows[i] for i in range(len(lows))] #this isn't the real volatility measurement, but it's good enough for me - vol = 1 means price doubled, 0 = no change
    
    
    #start sim here
    
    startDate = someSettings['periodLength'] #here we're looking for the most recent big jump - init at least 1 period length ago
    while startDate<len(volatility)-1 and volatility[startDate]<1: #arbirary jump cutoff, and make sure we don't go out of bounds
      startDate += 1
      
    # print(startDate)
    if(startDate<365): #only show info if the jump happened in the past year
      for i in range(startDate,startDate-someSettings['periodLength'],-1):
        print(dates[i]+" - "+str(round(volatility[i],2))+" - "+str(opens[i])+" - "+str(round(opens[i]-opens[i-1],2)))
        
      # plt.plot(volatility[startDate-someSettings['periodLength']:startDate][::-1]) #see what the volatility looks like after the jump - needs to be reversed because the original list is reverse (i.e. 0 is most recent)
      
      plt.subplot(211)
      plt.plot([(closes[i]-opens[i])/opens[i] for i in range(startDate+1,startDate-someSettings['periodLength'],-1)], label=symb)
      plt.title("(close-open)/open")
      plt.legend(loc='right')
      plt.subplot(212)
      plt.plot(volatility[startDate-someSettings['periodLength']:startDate+1][::-1], label=symb)
      plt.title("volatility")
      plt.legend(loc='right')
    
  plt.show()


  #start analysis and comparison here
  
  
  return sortedSyms


simIt(getPennies())