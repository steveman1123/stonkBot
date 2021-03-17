# Reverse Engineered Documentation for NASDAQ REST APIs

I haven't found any other documentation online, and have found this api by backtracking through other site's resources.

If you know of any other documentation, or have anything to add, please let me know! (this is far from complete)


endpoint urls:

```api.nasdaq.com/api```

```www.nasdaq.com/api/v1```


## api.nasdaq.com/api

1. ```/quote/{1}/{chart|historical|info|summary}``` where {1} is the symbol followed by the data to return  
    **Additional Parameters:**  
    ```?assetclass={mutualfunds|stocks|currencies|commodities}``` (**required for all**)  
    ```&fromdate={yyyy-mm-dd}``` (**required for historical**)  
    ```&todate={yyyy-mm-dd}``` (optional for historical)  
    ```&offset={#}``` (optional for historical)
    I believe there are other parameters that would allow seeing more data in historical, this setup returns a max of 14 days worth. There also seems to be an issue that if todate is specified and is more than one month ago from today, and the difference between todate and fromdate is less than one month, then nothing will be returned. This can be worked around using offset, however this is not ideal.

2. ```/company/{1}/{company-profile|financials}``` where {1} is the symbol  
    **Additional Parameters:**  
    ```?frequency={2}``` where {2} is 1 for period endings, and 2 for quarterly endings (optional for financials)

3. ```/market-info```

4. ```/marketmovers```

5. ```/calendar/{dividends|earnings|splits|upcoming|economicevents}```
    **additional Parameters:**
    ```?date={1}``` where {1} is the date in yyyy-mm-dd format

6. ```/ipo/calendar
    **additional Parameters:**
    ```?date={1}``` (optional) where {1} is the date in yyyy-mm format
    ```&type={spo}``` optional
    

## ww<span>w.</span>nasdaq.com/api/v1

7. ```/historical/{1}/{2}/{3}/{4}``` where {1} is the symbol, {2} is the assetclass, and {3} and {4} are the start and end dates in yyyy-mm-dd format. **Returns a csv document.** (this may have the same issue as the other historical data request). This also periodically goes offline

8. ```/{quote-news|recent-articles}/{1}/{2}``` where I don't know what {1} is, and {2} is number of headlines per request

---

## Examples:
1. quote  
    1. [chart](https://api.nasdaq.com/api/quote/MSFT/chart?assetclass=stocks)  
    2. [historical](https://api.nasdaq.com/api/quote/MSFT/historical?assetclass=stocks&fromdate=2020-10-15&offset=5)  
    3. [info (stocks)](https://api.nasdaq.com/api/quote/MSFT/info?assetclass=stocks)  
    3. [info (mutual funds)](https://api.nasdaq.com/api/quote/TRBCX/info?assetclass=stocks)  
    3. [info (currencies)](https://api.nasdaq.com/api/quote/EURUSD/info?assetclass=stocks)  
    4. [summary](https://api.nasdaq.com/api/quote/MSFT/summary?assetclass=stocks)  
2. company  
    1. [company profile](https://api.nasdaq.com/api/company/MSFT/company-profile)  
    2. [financials](https://api.nasdaq.com/api/company/MSFT/financials?frequency=1)  
3. [market info](https://api.nasdaq.com/api/market-info)  
4. [market movers](https://api.nasdaq.com/api/marketmovers)  
5. calendar  
    1. [dividends](https://api.nasdaq.com/api/calendar/dividends)  
    2. [earnings](https://api.nasdaq.com/api/calendar/earnings)  
    3. [splits](https://api.nasdaq.com/api/calendar/splits)  
    4. [upcoming](https://api.nasdaq.com/api/calendar/upcoming)  
6. [ipo calendar](https://api.nasdaq.com/api/ipo/calendar?date=2021-03&type=spo)  
7. [historical](https://www.nasdaq.com/api/v1/historical/MSFT/stocks/2020-10-15/2020-10-30)  
8. [quote news](https://www.nasdaq.com/api/v1/quote-news/1/5)  


Python example:
```
import requests, json

url1 = "https://api.nasdaq.com/api"
url2 = "https://www.nasdaq.com/api/v1"

symb = "MSFT"

infourl = "{}/quote/{}/info?assetclass=stocks".format(url1,symb)
newsurl = "{}/quote-news/1/2".format(url2)

info = json.loads(requests.get(infourl,headers={'user-agent':"-"},timeout=5).text)
news = json.loads(requests.get(newsurl,headers={'user-agent':"-"},timeout=5).text)

print("{} INFO:".format(symb))
print(json.dumps(info, indent=2))

print("\nSTOCK NEWS:")
print(json.dumps(news, indent=2))
```

**All requests must not have an empty user-agent header**
