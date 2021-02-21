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


#return the (integer) number of shares of a given stock able to be bought with the available cash
def sharesPurchasable(symb):
  price = getPrice(symb)
  if(price):
    return int(float(getAcct()['buying_power'])/price)
  else:
    return 0
