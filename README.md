# stonkBot
The first go at a stock trading bot using Alpaca API

This is also my first proper software project, so the code is by no means pretty, organized well, optimized, etc. because I'm still learning a bunch of stuff (and git too)

This is meant for relatively low speed, non-day trading with stocks (i.e. having less than $25k to throw around). No options, mutual funds or anything more complicated than individual companies. If you've got some misgivings about throwing real money into it, there's a paper trading optioon where you can pretend you're rich and try it out anyways (maybe you don't have to pretend. Idk, I'm not here to judge).

## How To Run
### System Requirements
- [Python 3.7](https://www.python.org/) or greater

- [Linux OS](https://www.raspberrypi.org/) (mostly tested on Rasbian, had issues with Windows for some reason*)

- [Internet connection](https://2018.bloomca.me/en) (if the power goes out for a while while using this (like mine did), I'd suggest finding a way to sell everything before the portfolio value starts dropping (like mine did))

*may potentially be issues with the time.sleep() function operating off the system clock which may change depending if the computer is active or not

### Setup
1. Download the repo
2. Move the stockStuff folder outside the repo to create the folder structure as seen below
3. Install any missing python modules
4. Run continuously (it works best if left alone other than to check for errors and provide some masochism)
5. ???
6. Profit


## API Keys and Folder Structure
The apikeys file has the actual keys removed for the REST APIs - if you want to try it out, **you will need to get your own Alpaca keys** and populate the key file - The alphaVantage keys are no longer necessary due to updates to use the nasdaq api.

The overall folder structure should look something like this*:
```
./
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

*The root folder name does not matter. The stockStuff folder should be moved from the repo to the location shown above

Currently, the stockData folder will grow unbounded (but reaasonably slowly) over time, so it may be smart to clean it out ~1/week or month until that part of the code gets fixed

## File Description
stonkBot.py - The main file to run - this was more useful when testing a number of functions all located in alpacaalgos.py, however it now serevrs as a clean/simple file to run everything

alpacaalgos.py - Contains the logic and error checking for actually buying and selling stocks

alpacafxns.py - Functions that require an Alpaca API query

otherfxns.py - Other functions that do not require an Alpaca API query (i.e. functions that query the NASDAQ API, or provide the logic to determine which stocks to buy)

stockStuff/ - contains data that won't be synced with the repo (api keys, latest trades, and stock histories) - **the folder and its contents should be moved to the location shown above for the program to work**

apikeys.key - Contains the API keys used for Alpaca and AlphaVantage - the file in the repo should be filled in with your information

latestTrades.json - Contains the stock name and the latest trade date and type for the stock

Depreciated Functions, etc/ - Contains old functions and ideas for algorithms that are no longer in use (either tested to be not profitable, or determined to be too simplistic - in my opinion, good for research, and coming up with some ideas, and that's about it)

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
