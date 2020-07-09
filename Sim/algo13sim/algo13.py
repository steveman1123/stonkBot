'''
look at week to week patterns after major jumps
i.e. we know a major jump happened, what happens over the next week? (~5 trading days)

'''
import json, requests,os,time,re
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
  the idea is to look at what happens in the following days after a big jump and trade accordingly
  '''
  #generate data files for each stock
  print("Getting stock data...")
  winners = {}
  for symb in symList:
    print(symb)
    if(not os.path.isfile(symb+".txt")):
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
    lows = [max(float(dateData[e]['3. low']),0.0000001) for e in dateData] #must not be 0 due to being a devisor
    highs = [float(dateData[e]['2. high']) for e in dateData]
    opens = [max(float(dateData[e]['1. open']),0.0000001) for e in dateData] #must not be 0 due to being a devisor
    closes = [float(dateData[e]['4. close']) for e in dateData]
    volumes = [float(dateData[e]['5. volume']) for e in dateData]
    volatility = [(highs[i]-lows[i])/(lows[i]) for i in range(len(lows))] #this isn't the real volatility measurement, but it's good enough for me - vol = 1 means price doubled, 0 = no change
    delDayRatio = [(closes[i]-opens[i])/(opens[i]) for i in range(len(opens))] #this is the change over the day normalized to the opening price
    
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
           (delDayRatio[startDate]<0 or\
            (delDayRatio[startDate-1]-delDayRatio[startDate])>-someSettings['volImpulse']/2\
           )\
          ):
      startDate += 1
      
    # this section is for experimenting and preliminary data analysis 

    if(startDate<len(volatility)-2 and startDate<90): #only show info if the jump happened in the past year/few months (ignore if it reaches the end)
      # for i in range(startDate,startDate-someSettings['periodLength'],-1):
      #   print(dates[i]+" - "+str(round(volatility[i],2))+" - "+str(opens[i])+" - "+str(round(delDayRatio[i]-delDayRatio[i+1],2)))
        
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
      plt.plot([delDayRatio[i]-delDayRatio[i+1] for i in range(startDate,startDate-someSettings['periodLength'],-1)], label=symb)
      plt.title("today-yesterday delDayRatio ((close-open)/open)")
      plt.legend(loc='right')

  #start analysis and comparison here
  
  print('\n\n')
  for e in winners:
    print(e+" - "+str(round(winners[e]['volatility'],2))+" - "+str(round(winners[e]['startDelDayRatio'],2))+" - "+str(round(winners[e]['nextDelDayRatio'],2)))
  print('\n\n')
  
  sortedSyms = sorted(list(winners.keys()), key=lambda k: float(winners[k]['diff']))[::-1]
  print(sortedSyms)
  plt.show()
 
  return sortedSyms


simIt(getPennies())
