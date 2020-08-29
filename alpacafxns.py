import otherfxns as o

isPaper = 0 #set up as paper trading (testing), or actual trading

keyFile = open("../stockStuff/apikeys.txt","r")
apiKeys = o.json.loads(keyFile.read())
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
ASSETURL = "{}/v2/assets".format(ENDPOINTURL) #asset url


# return string of account info
def getAcct():
  while True:
    try:
      html = o.requests.get(ACCTURL, headers=HEADERS).content
      break
    except Exception:
      print("No connection, or other error encountered. Trying again...")
      o.time.sleep(3)
      continue

  return o.json.loads(html)

# return currently held positions/stocks/whatever
def getPos():
  while True:
    try:
      html = o.requests.get(POSURL, headers=HEADERS).content
      break
    except Exception:
      print("No connection, or other error encountered. Trying again...")
      o.time.sleep(3)
      continue
  return o.json.loads(html)

# return currently held positions/stocks/whatever
def getOrders():
  while True:
    try:
      html = o.requests.get(ORDERSURL, headers=HEADERS).content
      break
    except Exception:
      print("No connection, or other error encountered. Trying again...")
      o.time.sleep(3)
      continue

  return o.json.loads(html)

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
          r = o.requests.delete(ORDERSURL, headers=HEADERS)
          break
        except Exception:
          print("No connection, or other error encountered. Trying again...")
          o.time.sleep(3)
          continue
      r = o.json.loads(r.content.decode("utf-8"))
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


#look to buy/sell a position
def createOrder(side, qty, sym, orderType="market", time_in_force="day", limPrice=0):
  if(o.isTradable(sym)):
    order = {
      "symbol":sym,
      "qty":qty,
      "type":orderType,
      "side":side,
      "time_in_force":time_in_force
    }
    if(orderType=="limit"): #TODO: this returns an error if used. Fix
      order['take_profit'] = {'limit_price':str(limPrice)}
    while True:
      try:
        r = o.requests.post(ORDERSURL, json=order, headers=HEADERS)
        break
      except Exception:
        print("No connection, or other error encountered. Trying again...")
        o.time.sleep(3)
        continue
  
    r = o.json.loads(r.content.decode("utf-8"))
    # print(r)
    try:
      return "Order to "+r["side"]+" "+r["qty"]+" share(s) of "+r["symbol"]+" at "+r["updated_at"]+" - "+r["status"]
    except Exception:
      return "Error: "+o.json.dumps(r)
  else:
    return sym+" is not tradable"

#check if the market is open
def marketIsOpen():
  while True:
    try:
      r = o.json.loads(o.requests.get(CLKURL, headers=HEADERS).content)
      break
    except Exception:
      print("No connection, or other error encountered. Trying again...")
      o.time.sleep(3)
      continue
  return r["is_open"]

#current market time in seconds since midnight
def marketTime():
  while True:
    try:
      ts = o.json.loads(o.requests.get(CLKURL, headers=HEADERS).content)["timestamp"]
      break
    except Exception:
      print("No connection, or other error encountered. Trying again...")
      o.time.sleep(3)
      continue

  ts = o.re.split('[-:T.]',ts[:-2])[:-3]
  ts = [int(ts[0]), int(ts[1]), int(ts[2]), int(ts[3])*3600+int(ts[4])*60+int(ts[5])]
  return ts

#time until next market close - in seconds
def timeTillClose():
  while True:
    try:
      cl = o.json.loads(o.requests.get(CLKURL, headers=HEADERS).content)["next_close"]
      break
    except Exception:
      print("No connection, or other error encountered. Trying again...")
      o.time.sleep(3)
      continue

  cl = o.re.split('[-:T.]',cl[:-2])
  cl = o.dt.datetime(int(cl[0]),int(cl[1]),int(cl[2]),int(cl[3]),int(cl[4]))
  now = marketTime()
  now = o.dt.datetime(int(now[0]),int(now[1]),int(now[2]),int(now[3]/3600),int(now[3]%3600/60),int(now[3]%60))
  return (cl - now).seconds

#time until next market open - in seconds
def timeTillOpen():
  while True:
    try:
      op = o.json.loads(o.requests.get(CLKURL, headers=HEADERS).content)["next_open"]
      break
    except Exception:
      print("No connection, or other error encountered. Trying again...")
      o.time.sleep(3)
      continue

  op = o.re.split('[-:T.]',op[:-2])
  op = o.dt.datetime(int(op[0]),int(op[1]),int(op[2]),int(op[3]),int(op[4]))
  now = marketTime()
  now = o.dt.datetime(int(now[0]),int(now[1]),int(now[2]),int(now[3]/3600),int(now[3]%3600/60),int(now[3]%60))
  return (op - now).seconds

#return the open and close times of a given day (EST)
def openCloseTimes(checkDate): #checkdate of format yyyy-mm-dd
  calParams = {}
  calParams["start"] = checkDate
  calParams["end"] = checkDate
  while True:
    try:
      d = o.json.loads(o.requests.get(CALURL, headers=HEADERS, params=calParams).content)[0]
      break
    except Exception:
      print("No connection, or other error encountered. Trying again...")
      o.time.sleep(3)
      continue
  
  #subtract 1 from hours to convert from EST (NYSE time), to CST (my time)
  d["open"] = str(int(d["open"].split(":")[0])-1)+":"+d["open"].split(":")[1]
  d["close"] = str(int(d["close"].split(":")[0])-1)+":"+d["close"].split(":")[1]
  return [o.dt.datetime.strptime(d["date"]+d["open"],"%Y-%m-%d%H:%M"), o.dt.datetime.strptime(d["date"]+d["close"],"%Y-%m-%d%H:%M")]

# return the current price of the indicated stock
def getPrice(symb):
  #url = 'https://api.nasdaq.com/api/quote/{}/info?assetclass=stocks'.format(symb) #use this URL to avoid alpaca
  url = 'https://data.alpaca.markets/v1/last/stocks/{}'.format(symb)
  while True:
    try:
      response = o.requests.get(url,headers=HEADERS).text #send request and store response
      # response = o.requests.get(url,headers={"User-Agent": "-"}).text #nasdaq url requires a non-empty user-agent string
      break
    except Exception:
      print("No connection, or other error encountered. Trying again...")
      o.time.sleep(3)
      continue

  try:
    #latestPrice = float(o.json.loads(response)["data"]["primaryData"]["lastSalePrice"][1:]) #use this line for the alt. URL
    latestPrice = float(o.json.loads(response)['last']['price'])
    return latestPrice
  except Exception:
    print("Invalid Stock - "+symb)
    return 0

#make sure that we can trade it on alpaca too
def isAlpacaTradable(symb):
  while True:
    try:
      tradable = o.requests.get(ASSETURL+"/"+symb, headers=HEADERS).content
      break
    except Exception:
      print("No connection, or other error encountered. Trying again...")
      o.time.sleep(3)
      continue
  try:
    return o.json.loads(tradable)['tradable']
  except Exception:
    return False


def checkValidKeys():
  while True:
    try:
      test = getAcct()
      break
    except Exception:
      print("No connection, or other error encountered. Trying again...")
      o.time.sleep(3)
      continue
  try:
    test = test["status"]
    if(test=="ACTIVE"):
      print("Valid keys - active account")
    else:
      print("Valid keys - inactive account")
  except Exception:
    try:
      test = test['message']
      print("Invalid keys")
    except Exception:
      print("Unknown issue encountered.")
    o.sys.exit()