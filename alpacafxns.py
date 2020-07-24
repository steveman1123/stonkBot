import requests, json, random, re, time
from pandas import read_html
from datetime import datetime as dt
from datetime import date
from datetime import timedelta

isPaper = 0 #set up as paper trading (testing), or actual trading

keyFile = open("../stockStuff/apikeys.key","r")
apiKeys = json.loads(keyFile.read())
keyFile.close()

if(isPaper):
  APIKEY = apiKeys["ALPACAPAPERKEY"]
  SECRETKEY = apiKeys["ALPACAPAPERSECRETKEY"]
  ENDPOINTURL = apiKeys["ALPACAPAPERURL"]
else:
  APIKEY = apiKeys["ALPACAKEY"]
  SECRETKEY = apiKeys["ALPACASECRETKEY"]
  ENDPOINTURL = apiKeys["ALPACAURL"]
  
HEADERS = {"APCA-API-KEY-ID":APIKEY,"APCA-API-SECRET-KEY":SECRETKEY} #headers for data

#alpaca = alpacaapi.REST(APIKEY,SECRETKEY,ENDPOINTURL,api_version="v2")
ACCTURL = "{}/v2/account".format(ENDPOINTURL) #account url
ORDERSURL = "{}/v2/orders".format(ENDPOINTURL) #orders url
POSURL = "{}/v2/positions".format(ENDPOINTURL) #positions url
CLKURL = "{}/v2/clock".format(ENDPOINTURL) #clock url
CALURL = "{}/v2/calendar".format(ENDPOINTURL) #calendar url

#get list of common penny stocks under $price and sorted by gainers (up) or losers (down)
def getPennies(price=1,updown="up"):
  url = 'https://stocksunder1.org/nasdaq-penny-stocks/'

  while True:
    try:
      html = requests.post(url, params={"price":price,"volume":0,"updown":updown}).content
      break
    except Exception:
      print("No connection, or other error encountered. Trying again...")
      time.sleep(3)
      continue

  tableList = read_html(html)
  try:
    symList = tableList[5][1:][0]
    symList = [e.replace(' predictions','') for e in symList]
    return symList
  except Exception:
    return ["Error"]

#get list of volatile penny stocks under $price and sorted by gainers (up) or losers (down)
def getVolatilePennies(price=1,updown="up"):
  url = 'https://stocksunder1.org/most-volatile-stocks/'
  while True:
    try:
      html = requests.post(url, params={"price":price,"volume":0,"updown":updown}).content
      break
    except Exception:
      print("No connection, or other error encountered. Trying again...")
      time.sleep(3)
      continue

  tableList = read_html(html)
  symList = tableList[2][0][5:]
  symList = [e.replace(' predictions','') for e in symList]
  return symList



# return string of account info
def getAcct():
  while True:
    try:
      html = requests.get(ACCTURL, headers=HEADERS).content
      break
    except Exception:
      print("No connection, or other error encountered. Trying again...")
      time.sleep(3)
      continue

  return json.loads(html)

# return currently held positions/stocks/whatever
def getPos():
  while True:
    try:
      html = requests.get(POSURL, headers=HEADERS).content
      break
    except Exception:
      print("No connection, or other error encountered. Trying again...")
      time.sleep(3)
      continue

  return json.loads(html)

# return currently held positions/stocks/whatever
def getOrders():
  while True:
    try:
      html = requests.get(ORDERSURL, headers=HEADERS).content
      break
    except Exception:
      print("No connection, or other error encountered. Trying again...")
      time.sleep(3)
      continue

  return json.loads(html)


def createOrder(side, qty, sym, orderType="market", time_in_force="day", limPrice=0):
  order = {
    "symbol":sym,
    "qty":qty,
    "type":orderType,
    "side":side,
    "time_in_force":time_in_force
  }
  if(orderType=="limit"):
    order['take_profit'] = {'limit_price':str(limPrice)}
  while True:
    try:
      r = requests.post(ORDERSURL, json=order, headers=HEADERS)
      break
    except Exception:
      print("No connection, or other error encountered. Trying again...")
      time.sleep(3)
      continue

  r = json.loads(r.content.decode("utf-8"))
  # print(r)
  try:
    return "Order to "+r["side"]+" "+r["qty"]+" share(s) of "+r["symbol"]+" at "+r["updated_at"]+" - "+r["status"]
  except Exception:
    return "Error: "+json.dumps(r)

#buy numToBuy different stocks from the symlist, sharesOfEach of each stock (e.g. buy 25 stocks from this list, and 10 of each)
def buyRandom(numToBuy, symList, sharesOfEach):
  for i in range(numToBuy):
    symbol = symList[random.randint(0,len(symList)-1)]
    print(symbol)
    print(createOrder("buy",str(sharesOfEach),symbol,"market","day"))
  print("Done Buying.")

#buy the topmost symbols from the list
def buyFromTop(numToBuy, symList, sharesOfEach):
  for i in range(numToBuy):
    symbol = symList[min(i,len(symList)-1)]
    print(symbol)
    print(createOrder("buy",str(sharesOfEach),symbol,"market","day"))
  print("Done Buying.")

#can prompt the user to consent to removing all orders and positions (starting over from scratch)
#returns 1 if trades were made, 0 if no trades made
def sellAll(isManual=1):
  pos = getPos()
  orders = getOrders()
  if(len(pos)+len(orders)>0):
    if(isManual):
      doit = input('Sell and cancel all positions and orders (y/n)? ')
    else:
      doit="y"

    if(doit=="y"): #user consents
      print("Removing Orders...")
      while True:
        try:
          r = requests.delete(ORDERSURL, headers=HEADERS)
          break
        except Exception:
          print("No connection, or other error encountered. Trying again...")
          time.sleep(3)
          continue
      r = json.loads(r.content.decode("utf-8"))
      for e in r:
        print(e["body"]["symbol"])
      print("Orders Cancelled.")
      #sell positions
      for p in pos:
        print("Selling "+p["qty"]+" share(s) of "+p["symbol"])
        createOrder("sell",p["qty"],p["symbol"],"market","day")
      print("Done Selling.")
      return 1
    else:
      print("Selling cancelled.")
      return 0
  else:
    print("No shares held")
    return 0


def marketIsOpen():
  while True:
    try:
      r = json.loads(requests.get(CLKURL, headers=HEADERS).content)
      break
    except Exception:
      print("No connection, or other error encountered. Trying again...")
      time.sleep(3)
      continue
  # return r
  return r["is_open"]

def marketTime():
  while True:
    try:
      ts = json.loads(requests.get(CLKURL, headers=HEADERS).content)["timestamp"]
      break
    except Exception:
      print("No connection, or other error encountered. Trying again...")
      time.sleep(3)
      continue

  ts = re.split('[-:T.]',ts[:-2])[:-3]
  ts = [int(ts[0]), int(ts[1]), int(ts[2]), int(ts[3])*3600+int(ts[4])*60+int(ts[5])]
  return ts


#time until next market close - in seconds
def timeTillClose():
  while True:
    try:
      cl = json.loads(requests.get(CLKURL, headers=HEADERS).content)["next_close"]
      break
    except Exception:
      print("No connection, or other error encountered. Trying again...")
      time.sleep(3)
      continue

  cl = re.split('[-:T.]',cl[:-2])
  cl = dt(int(cl[0]),int(cl[1]),int(cl[2]),int(cl[3]),int(cl[4]))
  now = marketTime()
  now = dt(int(now[0]),int(now[1]),int(now[2]),int(now[3]/3600),int(now[3]%3600/60),int(now[3]%60))
  return (cl - now).seconds

#time until next market open - in seconds
def timeTillOpen():
  while True:
    try:
      op = json.loads(requests.get(CLKURL, headers=HEADERS).content)["next_open"]
      break
    except Exception:
      print("No connection, or other error encountered. Trying again...")
      time.sleep(3)
      continue

  op = re.split('[-:T.]',op[:-2])
  op = dt(int(op[0]),int(op[1]),int(op[2]),int(op[3]),int(op[4]))
  now = marketTime()
  now = dt(int(now[0]),int(now[1]),int(now[2]),int(now[3]/3600),int(now[3]%3600/60),int(now[3]%60))
  return (op - now).seconds

# return the current price of the indicated stock
def getPrice(symb):
  #url = 'https://api.nasdaq.com/api/quote/{}/info?assetclass=stocks'.format(symb) #use this URL to avoid alpaca (doesn't seem to work sometimes though)
  url = 'https://data.alpaca.markets/v1/last/stocks/{}'.format(symb)
  while True:
    try:
      response = requests.get(url,headers=HEADERS).text #send request and store response
      break
    except Exception:
      print("No connection, or other error encountered. Trying again...")
      time.sleep(3)
      continue

  try:
    #latestPrice = float(json.loads(response)["data"]["primaryData"]["lastSalePrice"][1:]) #use this line for the alt. URL
    latestPrice = float(json.loads(response)['last']['price'])
    return latestPrice
  except Exception:
    print("Invalid Stock")
    return 0
    
#return the number of shares held of a given stock
def getShares(symb):
  while True:
    try:
      s = json.loads(requests.get(POSURL+"/"+symb.upper(), headers=HEADERS).content)
      break
    except Exception:
      print("No connection, or other error encountered. Trying again...")
      time.sleep(3)
      continue
  try:
    return float(s['qty'])
  except Exception:
    return 0

#return the average price per share of a held stock
def getBuyPrice(symb):
  shareHeaders = HEADERS
  shareHeaders["symbol"] = symb
  while True:
    try:
      s = json.loads(requests.get(POSURL, headers=shareHeaders).content)
      break
    except Exception:
      print("No connection, or other error encountered. Trying again...")
      time.sleep(3)
      continue
  return float(s[0]["avg_entry_price"]) if len(s) and s[0]["symbol"].lower()==symb.lower() else 0


#return the % cahnge of the portfolio given we know the starting amount
def getPortfolioChange(startVal):
  return round((float(getAcct()['portfolio_value'])-startVal)/startVal*100,2)


#return the open and close times of a given day (EST)
def openCloseTimes(checkDate): #checkdate of format yyyy-mm-dd
  calParams = {}
  calParams["start"] = checkDate
  calParams["end"] = checkDate
  while True:
    try:
      d = json.loads(requests.get(CALURL, headers=HEADERS, params=calParams).content)[0]
      break
    except Exception:
      print("No connection, or other error encountered. Trying again...")
      a.time.sleep(3)
      continue
  
  #subtract 1 from hours to convert from EST (NYSE time), to CST (my time)
  d["open"] = str(int(d["open"].split(":")[0])-1)+":"+d["open"].split(":")[1]
  d["close"] = str(int(d["close"].split(":")[0])-1)+":"+d["close"].split(":")[1]
  return [dt.strptime(d["date"]+d["open"],"%Y-%m-%d%H:%M"), dt.strptime(d["date"]+d["close"],"%Y-%m-%d%H:%M")]


#return the (integer) number of shares of a given stock able to be bought with the available cash
def sharesPurchasable(symb):
  price = getPrice(symb)
  if(price):
    return int(float(getAcct()['buying_power'])/price)
  else:
    return 0
