# Reverse Engineered Documentation for NASDAQ REST APIs

I haven't found any other documentation online, and have found this api by backtracking through other site's resources.

If you know of any other documentation, or have anything to add, please let me know! (this is far from complete)


endpoint urls:

```api.nasdaq.com/api```

```www.nasdaq.com/api/v1```


## api.nasdaq.com/api

1. ```/quote/{1}/{chart|historical|info|summary}``` where {1} is the symbol followed by the data to return  
    **Additional Parameters:**  
    ```?assetclass={mutualfunds|stocks}``` (**required for all**)  
    ```&fromdate={yyyy-mm-dd}``` (**required for historical**)  
    ```&todate={yyyy-mm-dd}``` (optional for historical)  
    I believe there are other parameters that would allow seeing more data in historical, this setup returns a max of 14 days worth

2. ```/company/{1}/{company-profile|financials}``` where {1} is the symbol  
    **Additional Parameters:**  
    ```?frequency={2}``` where {2} is 1 for period endings, and 2 for quarterly endings (optional for financials)

3. ```/market-info```

4. ```/calendar/{dividends|earnings|splits|upcoming}```


## ww<span>w.</span>nasdaq.com/api/v1

5. ```/historical/{1}/{2}/{3}/{4}``` where {1} is the symbol, {2} is the assetclass, and {3} and {4} are the start and end dates in yyyy-mm-dd format. **Returns a csv document.**

6. ```/quote-news/{1}/{2}``` where I don't know what {1} is, and {2} is number of headlines per request

---

## Examples:
1. quote  
    1. [chart](https://api.nasdaq.com/api/quote/MSFT/chart?assetclass=stocks)  
    2. [historical](https://api.nasdaq.com/api/quote/MSFT/historical?assetclass=stocks&fromdate=2020-10-15&todate=2020-10-30)  
    3. [info](https://api.nasdaq.com/api/quote/MSFT/info?assetclass=stocks)  
    4. [summary](https://api.nasdaq.com/api/quote/MSFT/summary?assetclass=stocks)  
2. company  
    1. [company profile](https://api.nasdaq.com/api/company/MSFT/company-profile)  
    2. [financials](https://api.nasdaq.com/api/company/MSFT/financials?frequency=1)  
3. [market info](https://api.nasdaq.com/api/market-info)  
4. calendar  
    1. [dividends](https://api.nasdaq.com/api/calendar/dividends)  
    2. [earnings](https://api.nasdaq.com/api/calendar/earnings)  
    3. [splits](https://api.nasdaq.com/api/calendar/splits)  
    4. [upcoming](https://api.nasdaq.com/api/calendar/upcoming)  
5. [historical](https://www.nasdaq.com/api/v1/historical/MSFT/stocks/2020-10-15/2020-10-30)  
6. [quote news](https://www.nasdaq.com/api/v1/quote-news/1/5)  


Python example:
```
import requests, json

url1 = "https://api.nasdaq.com/api/"
url2 = "https://www.nasdaq.com/api/v1/"

symb = "msft".upper()

infourl = f"{url1}quote/{symb}/info?assetclass=stocks"
newsurl = f"{url2}quote-news/1/2"

info = json.loads(requests.get(infourl,headers={'user-agent':"-"},timeout=5).text)
news = json.loads(requests.get(newsurl,headers={'user-agent':"-"},timeout=5).text)

print(f"{symb} INFO:")
print(json.dumps(info, indent=2))

print("\nSTOCK NEWS:")
print(json.dumps(news, indent=2))
```

**All requests must not have an empty user-agent header**