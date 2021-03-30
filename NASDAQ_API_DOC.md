# Reverse Engineered Documentation for NASDAQ REST APIs

I haven't found any other documentation online, and have found this api by backtracking through other site's resources.

If you know of any other documentation, or have anything to add, please let me know! (this is far from complete)


endpoint urls:

```api.nasdaq.com/api```

```www.nasdaq.com/api/v1```


## api.nasdaq.com/api

1. ```/quote```
    1. ```/{1}/{chart|dividends|eps|extended-trading|historical|info|option-chain|realtime-trades|short-interest|summary}``` where {1} is the symbol followed by the data to return.  
        **Additional Parameters:**  
        ```?assetclass={commodities|crypto|currencies|fixedincome|futures|index|mutualfunds|stocks}``` (**required for all**)  
        ```&fromdate={yyyy-mm-dd}``` (**required for historical**)  
        ```&todate={yyyy-mm-dd}``` (optional for historical)  
        ```&offset={#}``` (optional for historical)  
        ```&charttype={real}``` (optional for chart)  
        ```&limit={#}``` (optional)  
        ```&markettype={pre|post}``` required for extended-trading  
        Historical defaults limit=15. There seems to be an issue that if todate is specified and is more than one month ago from today, and the difference between todate and fromdate is less than one month, then nothing will be returned. This can be worked around using offset and/or limit.
    2. ```/watchlist/```  
        **Additional Parameters:**  
        ```?symbol={1}``` where symbol is an array, and {1} is formatted as "symb|assetclass". DYOR on how to pass arrays through get requests (see also the link example below for a simple url format)  
        ```&type={1}``` (optional) where {1} can be Rv (which may mean row/value?)  
    3. ```/indices```  
        **Additional Parameters:**  
        ```?chartfor={1}``` (optional) where chartfor is an array (similar to symbol in /quote/watchlist), {1} is an index symbol  
        ```&symbol={2}``` (optional) where this is an array (similar to symbol in /quote/watchlist), {2} is an index symbol  
        Note: leave off all params for a list of all indices

2. ```/company/{1}/{company-profile|earnings-surprise|financials|historical-nocp|insider-trades|institutional-holdings|revenue|sec-filings}``` where {1} is the symbol  
    **Additional Parameters:**  
    ```?frequency={2}``` where {2} is 1 for period endings, and 2 for quarterly endings (optional)  
    ```&timeframe={d5|M1||M3|M6|Y1}``` (optional for historical-nocp)  
    ```&limit={#}``` (optional)  
    ```&type={TOTAL|NEW|INCREASED|DECREASED|ACTIVITY|SOLDOUT}``` (optional for institutional-holdings)  
    ```&sortColumn={marketValue|sharesChangePCT|sharesChange|sharesHeld|date|ownerName}``` (optional for institutional-holdings)  
    ```&type={ALL|buys|sells}``` (optional for insider-trades)  
    ```&sortColumn={lastDate|insider|relation|transactionType|ownType|sharesTraded}``` (optional for insider-trades)  
    ```&sortColumn={filed|}``` (optional for sec-filing)  
    ```&sortOrder={DESC|ASC}``` (optional)  
    ```&tableOnly={true|false}``` (optional)  

3. ```/market-info```

4. ```/marketmovers```

5. ```/calendar/{dividends|earnings|economicevents|splits|upcoming}```  
    **Additional Parameters:**  
    ```?date={1}``` where {1} is the date in yyyy-mm-dd format  

6. ```/ipo/calendar```  
    **Additional Parameters:**  
    ```?date={1}``` (optional) where {1} is the date in yyyy-mm format  
    ```&type={2}``` (optional) where {2} is the type (can be set to 'spo')  
    
7. ```/screener/{etf|index|mutualfunds|stocks}```  
    **Additional Parameters:**  
    ```?tableonly={true|false}``` return only the table or additional filter info (defaults to true)  
    ```&offset={1}``` where 1 is the amount to offset the table by (returns only 50 entries by default)   
    **Further parameters depend on which screener is being used** and can be found in the 'filters' section when tableonly=false  
8. ```/analyst```  
    ```/{1}/{earnings-date|earnings-forcast|estimate-momentum|peg-ratio|ratings|targetprice}``` where 1 is a stock symbol

## ww<span>w.</span>nasdaq.com/api/v1

1. ```/historical/{1}/{2}/{3}/{4}``` where {1} is the symbol, {2} is the assetclass, and {3} and {4} are the start and end dates in yyyy-mm-dd format. **Returns a csv document.** (this may have the same issue as the other historical data request). This also periodically goes offline

2. ```/{quote-news|recent-articles}/{1}/{2}``` where I don't know what {1} is, and {2} is number of headlines per request

3. ```/search``` used to get search results  
    **Additional Parameters:**  
    ```?q={1}``` where {1} is the search string  
    ```&offset={2}``` where 2 is likely the offset of results  
    ```&langcode={3}``` where 3 is the language being used (e.g. en, de, fr, etc)
---

## Examples:
1. quote  
    1. symbol  
        1. [chart](https://api.nasdaq.com/api/quote/MSFT/chart?assetclass=stocks)  
        2. [dividends](https://api.nasdaq.com/api/quote/MSFT/dividends?assetclass=stocks)  
        3. [eps](https://api.nasdaq.com/api/quote/MSFT/eps?assetclass=stocks)  
        4. [extended trading](https://api.nasdaq.com/api/quote/MSFT/extended-trading?assetclass=stocks&markettype=post)  
        5. [option chain](https://api.nasdaq.com/api/quote/MSFT/option-chain?assetclass=stocks)  
        7. [realtime trades](https://api.nasdaq.com/api/quote/MSFT/realtime-trades?assetclass=stocks)  
        8. [short interest](https://api.nasdaq.com/api/quote/MSFT/short-interest?assetclass=stocks)  
        9. [historical](https://api.nasdaq.com/api/quote/MSFT/historical?assetclass=stocks&fromdate=2020-10-15&offset=5)  
        10. [info (stocks)](https://api.nasdaq.com/api/quote/MSFT/info?assetclass=stocks)  
        11. [info (mutual funds)](https://api.nasdaq.com/api/quote/TRBCX/info?assetclass=mutualfunds)  
        12. [info (currencies)](https://api.nasdaq.com/api/quote/EURUSD/info?assetclass=currencies)  
        12. [info (crypto)](https://api.nasdaq.com/api/quote/BTC/info?assetclass=crypto)  
        13. [summary](https://api.nasdaq.com/api/quote/MSFT/summary?assetclass=stocks)  
    2. [watchlist](https://api.nasdaq.com/api/quote/watchlist?symbol[0]=btc|crypto&symbol[1]=msft|stocks)  
    3. [indices](https://api.nasdaq.com/api/quote/indices?symbol=ndx&chartfor=ndx)
  
2. company  
    1. [company profile](https://api.nasdaq.com/api/company/MSFT/company-profile)  
    2. [financials](https://api.nasdaq.com/api/company/MSFT/financials?frequency=1)  
    3. [insider trades](https://api.nasdaq.com/api/company/MSFT/insider-trades)  
    4. [institutional holdings](https://api.nasdaq.com/api/company/MSFT/institutional-holdings)  
    5. [revenue](https://api.nasdaq.com/api/company/MSFT/revenue)  
    6. [sec-filings](https://api.nasdaq.com/api/company/MSFT/sec-filings)  
    7. [earnings surprise](https://api.nasdaq.com/api/company/MSFT/earnings-surprise)  
    8. [historical NOCP](https://api.nasdaq.com/api/company/MSFT/historical-nocp)  
3. [market info](https://api.nasdaq.com/api/market-info)  
4. [market movers](https://api.nasdaq.com/api/marketmovers)  
5. calendar  
    1. [dividends](https://api.nasdaq.com/api/calendar/dividends)  
    2. [earnings](https://api.nasdaq.com/api/calendar/earnings)  
    3. [splits](https://api.nasdaq.com/api/calendar/splits)  
    4. [upcoming](https://api.nasdaq.com/api/calendar/upcoming)  
    5. [economic events](https://api.nasdaq.com/api/calendar/economicevents)  
6. [ipo calendar](https://api.nasdaq.com/api/ipo/calendar?date=2021-03&type=spo)  
7. [stock screener](https://api.nasdaq.com/api/screener/stocks?tableonly=false&region=north_america&country=united_states&exchange=NASDAQ)  
8. analyst
    1. [earnings date](https://api.nasdaq.com/api/analyst/MSFT/earnings-date)  
    2. [earnings forecast](https://api.nasdaq.com/api/analyst/MSFT/earnings-forcast)  
    3. [estimate momentum](https://api.nasdaq.com/api/analyst/MSFT/estimate-momentum)  
    4. [p/e growth ratio](https://api.nasdaq.com/api/analyst/MSFT/peg-ratio)  
    5. [ratings](https://api.nasdaq.com/api/analyst/MSFT/ratings)  
    6. [target price](https://api.nasdaq.com/api/analyst/MSFT/targetprice)  
---
1. [historical](https://www.nasdaq.com/api/v1/historical/MSFT/stocks/2020-10-15/2020-11-23)  
2. [quote news](https://www.nasdaq.com/api/v1/quote-news/31867/5)  
3. [search](https://www.nasdaq.com/api/v1/search?q=microsoft&offset=0&langcode=en)  


Python example:
```
import requests, json

url1 = "https://api.nasdaq.com/api"
url2 = "https://www.nasdaq.com/api/v1"

symb = "MSFT"

infourl = "{}/quote/{}/info?assetclass=stocks".format(url1,symb)
newsurl = "{}/quote-news/31867/2".format(url2)

info = json.loads(requests.get(infourl,headers={'user-agent':"-"},timeout=5).text)
news = json.loads(requests.get(newsurl,headers={'user-agent':"-"},timeout=5).text)

print("{} INFO:".format(symb))
print(json.dumps(info, indent=2))

print("\nSTOCK NEWS:")
print(json.dumps(news, indent=2))
```

**All requests must not have an empty user-agent header**
