# stonkBot
The first go at a stock trading bot using Alpaca API

Please be aware that this is my first _real_ "software engineering" project, and a personal project at that, so the code is by no means pretty, organized well, optimized, etc. It's meant for non-day trading (i.e. having less than $25k to throw around).

# How To Run
## Pre-reqs
Python 3.7 or greater
Linux OS (mostly tested on Rasbian, had issues with Windows for some reason)
Internet connection (if the power goes out for a while while using this (like mine did), I'd suggest finding a way to sell everything before the portfolio value starts dropping (like mine did))


1. Download the repo
2. Create the folder structure as seen in the next section (move the apikeys-template and latestTrades-template files to the stockStuff folder)
3. Install any missing python modules
4. Run continuously (it works best if left alone completely)
5. Profit


## API Keys and Folder Structure
The apikeys file has the actual keys removed for the REST APIs - if you want to try it out, **you will need to get your own Alpaca keys** and populate the key file - The alphaVantage keys are no longer necessary due to new updates using the nasdaq api.
The overall folder structure should look something like this:
```
stocks/
|
+-stockStuff/
| |
| +-stockData/
| +-apikeys.key
| +-latestTrades.json
|
+-stonkBot/ (this repo)
  |
  +-etc...
```

## External Resources
[Alpaca](https://alpaca.markets/)

[AlphaVantage](https://alphavantage.com/)

[Stocks Under $1](https://stocksunder1.org/)

[NASDAQ Quote API](https://api.nasdaq.com/api/quote/MSFT/info?assetclass=stocks)

[NASDAQ Historical API](https://www.nasdaq.com/api/v1/historical/MSFT/stocks/2019-04-20/2020-04-20/)

[MarketWatch Stock Screener](https://www.marketwatch.com/tools/stockresearch/screener/)


## Disclaimer
I do not claim to be a financial expert and cannot be held accountable for any losses you may incur as a result of using this software

Copyright 2020 Steven Williams

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
