
# stonkBot
The first go at a stock trading bot using Alpaca API

This is also my first proper software project, so the code is by no means pretty, organized well, optimized, etc. because I'm still learning a bunch of stuff (and git too)

This is meant for relatively low speed, non-day trading with stocks (i.e. having less than $25k to throw around). No options, mutual funds or anything more complicated than individual companies using [this algorithm](https://stocksunder1.org/penny-stocks/).

If you've got some misgivings about throwing real money into it, there's a paper trading option in Alpaca where you can pretend you're rich and try it out anyways (maybe you don't have to pretend. Idk, I'm not here to judge) - this option can be set in the alpacafxns.py file.

Don't be afraid to change things around: nothing you do can break it so bad that a new pull can't fix it.

## How To Run
### System Requirements
- [Python 3.7](https://www.python.org/) or greater

- [Linux OS](https://www.raspberrypi.org/) (mostly tested on Rasbian, had issues with Windows for some reason*)

- [Internet connection](https://2018.bloomca.me/en)

*may potentially be issues with the time.sleep() function operating off the system clock which may change depending if the computer is active or not

### Setup
1. Download the repo
2. Move the stockStuff folder outside the repo to create the folder structure as seen below
3. Install any missing python modules (suggest also installing "screen" or "tmux" package if running on raspberry pi)
4. Create Alpaca account, populate keys in apikeys.txt, and set the desired isPaper value in alpacafxns.py (isPaper=0 is live trading, isPaper=1 is paper trading)
4. Run continuously (it works best if left alone other than to check for errors and provide some masochism)
5. ???
6. Profit


## API Keys and Folder Structure
The apikeys file has the actual keys removed for the REST APIs - if you want to try it out, **you will need to get your own Alpaca keys** and populate the key file - The alphaVantage keys are no longer necessary due to updates to use the nasdaq api (however, if you decide to poke through the Depreciated Functions, you will need it there).

The overall folder structure should look something like this*:
```
./
|
+-stockStuff/
| |
| +-stockData/
| +-apikeys.txt
| +-latestTrades.json
|
+-stonkBot/ (this repo)
  |
  +-etc...
```

*The root folder name does not matter. The stockStuff folder should be moved from the repo to the location shown above

## File Description
stonkBot.py - The main file to run - this was more useful when testing a number of functions all located in alpacaalgos.py, however it now serevrs as a clean/simple file to run everything

alpacaalgos.py - Contains the logic and error checking for actually buying and selling stocks

alpacafxns.py - Functions that require an Alpaca API query

otherfxns.py - Other functions that do not require an Alpaca API query (i.e. functions that query the NASDAQ API, or provide the logic to determine which stocks to buy)

stonkBot.config - config file for settings in the files listed above. Formatted as json, double spaces indicate which file it's mostly used in in the heirarchy (order specific to the files listed above)

stockStuff/ - contains data that won't be synced with the repo (api keys, latest trades, and stock histories (these are cleared every Friday evening)) - **the folder and its contents should be moved to the location shown above for the program to work**

apikeys.txt - Contains the API keys used for Alpaca and AlphaVantage - the file in the repo should be filled in with your information

latestTrades.json - Contains the stock name and the latest trade date and type for the stock

Depreciated Functions, etc/ - Contains old functions and ideas for algorithms that are no longer in use (either tested to be not profitable, or determined to be too simplistic - in my opinion, good for research, and coming up with some ideas, and that's about it)

## Running and Output Interpretation

Depending on how you have your file permissions set, this may need to run as sudo in order to read/write the stockStuff files

The output should look something akin to this:

![Sample Output](https://github.com/steveman1123/stonkBot/blob/master/sampleOutput.jpg?raw=true)

On the first day, there will be no tradable stocks, 20 minutes before market close, a thread to start getting stocks to buy will run (if you have sufficient buying power), then 10 minutes before market close, it will start to buy stocks

After the first day, assuming you have stocks held, it will show something similar to above, and will check to sell the listed stocks throughout the day if they reach one of the trigger points.

Generally it seems that it takes about 5 weeks (+/- 3 weeks) after the initial jump to jump a second time.

From testing between 2020-07-14 to 2020-09-16, I have gotten an average growth rate of 0.44%/day with a standard deviation of 3.62% (including 1 week of no trading due to a power outage)

![Daily Returns](https://github.com/steveman1123/stonkBot/blob/master/dailyReturns.jpg?raw=true)

## External Resources
[Alpaca](https://alpaca.markets/)

[AlphaVantage](https://www.alphavantage.co/)

[Stocks Under $1](https://stocksunder1.org/)

[NASDAQ Quote API](https://api.nasdaq.com/api/quote/MSFT/info?assetclass=stocks)

[NASDAQ Historical API](https://www.nasdaq.com/api/v1/historical/MSFT/stocks/2019-04-20/2020-04-20/)

[MarketWatch Stock Screener](https://www.marketwatch.com/tools/stockresearch/screener/)

## Issues & Enhancements

If you are encountering some issues, make sure to pull the latest version, it is under active delopment, so things change quickly.

if the power goes out for a while while using this (like mine did), I'd suggest finding a way to sell everything before the portfolio value starts dropping (like mine did)

### Shortterm resolutions (next few weeks):
* Change some selling logic (to add a time limit)

### Midterm resolutions (next few months):
* Add master/slave relationship to allow it to run on multiple computers in the event of the primary program going down (add redundancy)
* Make config file more readable (not json)

### Longterm resolutions (next few years):
* Record trade history and give performance analytics
* Add some basic machine learning to improve trades over time

## Disclaimer
I do not claim to be a financial expert and cannot be held accountable for any losses you may incur as a result of using this software
