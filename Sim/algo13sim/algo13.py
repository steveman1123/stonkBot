'''
look at week to week patterns after major jumps
i.e. we know a major jump happened, what happens over the next week? (~5 trading days)

'''
import json, requests,os,time,re
from pandas import read_html
from matplotlib import pyplot as plt
import datetime as dt

keyFile = open("apikeys.key","r")
apiKeys = json.loads(keyFile.read())
keyFile.close()

settingsFile = open("algo13.json","r")
someSettings = json.loads(settingsFile.read())
settingsFile.close()


#get list of common penny stocks under $price and sorted by gainers (up) or losers (down)
def getPennies(price=1,updown="up"):
  #another nasdaq only url: https://stocksunder1.org/nasdaq-stocks-under-1/
  url = 'https://stocksunder1.org/nasdaq-penny-stocks/'
  html = requests.post(url, params={"price":price,"volume":0,"updown":updown}).content
  tableList = read_html(html)
  # print(tableList)
  # symList = tableList[5][0:]['Symbol']
  symList = tableList[5][1:][0] #this keeps changing (possibly intentionally)
  symList = [re.sub(r'\W+','',e.replace(' predictions','')) for e in symList] #strip "predictions" and any non alphanumerics
#  print(tableList[5][0:]['Symbol'])
  return symList

#gets a list of volatile stocks using criteria outlined here: https://stocksunder1.org/how-to-trade-penny-stocks/
def getVolatile(lbound=0.8, ubound=5,minPercChange=30, minVol=8000000):
  url = 'https://www.marketwatch.com/tools/stockresearch/screener/results.asp'
  params = {"submit":"Screen",
            "Symbol":"true",
            "ChangePct":"true",
            "CompanyName":"false",
            "Volume":"true",
            "Price":"true",
            "Change":"true",
            "SortyBy":"Symbol",
            "SortDirection":"Ascending",
            "ResultsPerPage":"OneHundred",
            "TradesShareEnable":"true",
            "TradesShareMin":str(lbound),
            "TradesShareMax":str(ubound),
            "PriceDirEnable":"true",
            "PriceDir":"Up",
            "PriceDirPct":str(minPercChange),
            "TradeVolEnable":"true",
            "TradeVolMin":str(minVol),
            "TradeVolMax":"",
            "Exchange":"NASDAQ",
            "IndustryEnable":"false",
            "MoreInfo":"false"}
  html = requests.post(url, params=params).content
  tableList = read_html(html)
  symList = tableList[0]['Symbol'].tolist()
  return symList


#function to sim stocks that have already peaked and return the good ones
def simPast(symList):
  '''
  the idea is to look at what happens in the following days after a big jump and trade accordingly
  '''
  #generate data files for each stock
  print("Getting stock data...")
  winners = {}
  for i,symb in enumerate(symList):
    print("("+str(i+1)+"/"+str(len(symList))+") "+symb)
    if(not os.path.isfile(someSettings['pastStockPath']+symb+".txt")):
      url = apiKeys["ALPHAVANTAGEURL"]
      params= { # NOTE: the information is also available as CSV which would be more efficient
        'apikey' : apiKeys["ALPHAVANTAGEKEY"],
        'function' : 'TIME_SERIES_DAILY', #daily resolution (open, high, low, close, volume)
        'symbol' : symb, #ticker symbol
        'outputsize' : 'full' #up to 20yrs of data
      }
      response = requests.request('GET', url, params=params).text #send request and store response
      time.sleep(19) #max requests of 5 per minute for free alphavantage account, delay to stay under that limit
  
      out = open(someSettings['pastStockPath']+symb+'.txt','w') #write to file for later usage
      out.write(response)
      out.close()
      
    
    #gather info about single stock
    stonkFile = open(someSettings['pastStockPath']+symb+'.txt','r') #open the file containing stonk data
    stonkData = json.loads(stonkFile.read()) #read in as json data
    stonkFile.close()
  
    dateData = stonkData[list(stonkData.keys())[1]] #time series (daily) - index 0=meta data, 1=stock data
    period = min(someSettings['periodLength'],len(dateData)-1) #how long for period
    
    dates = [e for e in dateData]
    lows = [max(float(dateData[e]['3. low']),0.0000001) for e in dateData] #must not be 0 due to being a devisor
    highs = [float(dateData[e]['2. high']) for e in dateData]
    opens = [max(float(dateData[e]['1. open']),0.0000001) for e in dateData] #must not be 0 due to being a devisor
    closes = [float(dateData[e]['4. close']) for e in dateData]
    volumes = [float(dateData[e]['5. volume']) for e in dateData]
    volatility = [(highs[i]-lows[i])/(lows[i]) for i in range(len(lows))] #this isn't the real volatility measurement, but it's good enough for me - vol = 1 means price doubled, 0 = no change
    delDayRatio = [(closes[i]-opens[i])/(closes[i+1]) for i in range(len(closes)-1)] #this is the change over the day normalized to the opening price
    
    #start sim here
    
    startDate = someSettings['periodLength']-1 #here we're looking for the most recent big jump - init at least 1 period length ago
    '''
    the following conditions should be true when asking if the date should be skipped (in order as they appear in the while statement):
    make sure we're in range
    arbirary volatility of the day - higher= more volatility in a given day (volImpulse is minimum volatility to have)
    look only for positive daily changes
    the difference between today's (startDate-1) change and yesterdays must be sufficiently large (and negative) to constitute underdamped oscilation - at least 1/2 of original
    '''
    while startDate<len(volatility)-2 and\
          (volatility[startDate]<someSettings['volImpulse'] or\
           (delDayRatio[startDate]<.25 or\
            (delDayRatio[startDate-1]-delDayRatio[startDate])>-.75\
           )\
          ):
      startDate += 1
      
    # start data analysis here
    
    if(startDate<len(volatility)-2 and startDate<90 and closes[startDate-1]>closes[startDate]): #only show info if the jump happened in the past year/few months (ignore if it reaches the end)
      for i in range(startDate,startDate-someSettings['periodLength'],-1):
        print(dates[i]+" - "+str(round(volatility[i],2))+" - "+str(opens[i])+" - "+str(round(delDayRatio[i]-delDayRatio[i+1],2)))
        
      #symbols that show up in the graph/meet the conditions
      winners[symb] = {"volatility":volatility[startDate],
                       "startDelDayRatio":delDayRatio[startDate]-delDayRatio[startDate+1],
                       "nextDelDayRatio":delDayRatio[startDate-1]-delDayRatio[startDate],
                       "diff":(delDayRatio[startDate]-delDayRatio[startDate+1])-(delDayRatio[startDate-1]-delDayRatio[startDate])}
      
      # plt.figure(1)
      # plt.subplot(211)
      # plt.plot([delDayRatio[i]-delDayRatio[i+1] for i in range(startDate,startDate-someSettings['periodLength'],-1)], label=symb)
      # plt.title("today-yesterday delDayRatio ((close-open)/open)")
      # plt.legend(loc='right')
      # 
      # plt.subplot(212)
      # plt.plot([volatility[i] for i in range(startDate,startDate-someSettings['periodLength'],-1)], label=symb)
      # plt.title("volatility ((high-low)/low)")
      # plt.legend(loc='right')
      
      plt.figure(2)
      # plt.plot([delDayRatio[i]-delDayRatio[i+1] for i in range(startDate,startDate-someSettings['periodLength'],-1)], label=symb)
      plt.plot([closes[i]/closes[startDate] for i in range(startDate+80, startDate-someSettings['periodLength'],-1)], label=symb)
      # plt.title("today-yesterday delDayRatio ((close-open)/close-1)")
      plt.legend(loc='right')

  # print('\n\n')
  
  sortedSyms = sorted(list(winners.keys()), key=lambda k: float(winners[k]['diff']))[::-1]
  # print(sortedSyms)
  plt.show()
 
  return sortedSyms


#function to keep track of info of stocks (the volatility, day change, price, etc)
def presentList(symList):
  # for symb in symList:
    #TODO: check date, market last open date, etc - how many trading days since initial bump
    
    
    # f = open(symb+"--"+str(dt.date.today())+".txt","w")
    # f.write(
  return 0

# print(simPast(getPennies()))
print(getVolatile())