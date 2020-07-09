import requests
from datetime import date
symb = "XSPA"
a = requests.get("https://www.alphavantage.co/query",params={"function":"TIME_SERIES_INTRADAY","symbol":symb,"interval":"1min","outputsize":"full","apikey":"","datatype":"csv"}).content
f = open(symb+"_"+str(date.today())+".csv","w")
f.write(str(a).replace("\\r\\n","\n"))
f.close()
