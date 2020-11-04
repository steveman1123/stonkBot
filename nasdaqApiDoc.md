# This is my reverse engineering documentation for the NASDAQ REST APIs

I haven't found any documentation online or anywhere, and have found this api by backtracking through other site's resources.

If you know of any other documentation, or have anything to add, please let me know! (this is far from complete)


endpoint urls:

```api.nasdaq.com/api/```

```www.nasdaq.com/api/v1```


## api.nasdaq.com/api/

```/quote/{1}/{summary|info|historical|chart}``` where {1} is the symbol followed by the data to return

Additional parameters:

```?assetclass={stocks|mutualfunds}``` (**required for all**)

```&fromdate={yyyy-mm-dd}``` (**required for historical**)

```&todate={yyyy-mm-dd}``` (optional for historical)

I believe there are other parameters that would allow seeing more data in historical, this setup returns a max of 14 days worth


```/company/{1}/{financials|company-profile}``` where {1} is the symbol

Additional parameters:

```?frequency={2}``` where {2} is 1 for period endings, and 2 for quarterly endings (optional for financials)


```/market-info```

```/calendar/{upcoming|splits|earnings|dividends}```




## www.nasdaq.com/api/v1

```/quote-news/{1}/{2}``` where I don't know what {1} is, and {2} is number of headlines per request

```/historical/{1}/{2}/{3}/{4}``` where {1} is the symbol, {2} is the assetclass, and {3} and {4} are the start and end dates in yyyy-mm-dd format. Returns a csv document




**Often these must not have an empty user-agent header**


