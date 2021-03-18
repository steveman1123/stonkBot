
# stonkBot
The first go at a stock trading bot using Alpaca API

This is also my first proper software project, so the code is by no means pretty, organized well, optimized, etc. because I'm still learning a bunch of stuff (and git too)

This is meant for relatively low speed, non-day trading with stocks (i.e. having less than $25k to throw around). No options, mutual funds or anything more complicated than individual companies using [this algorithm](https://stocksunder1.org/penny-stocks/#strategy).

If you've got some misgivings about throwing real money into it, there's a paper trading option in Alpaca where you can pretend you're rich and try it out anyways (maybe you don't have to pretend. Idk, I'm not here to judge) - this option can be set in the settings.config file.

Don't be afraid to change things around (especially in the settings file): nothing you do can break it so bad that a new pull can't fix it.

## How To Run
### System Requirements
- [Python 3.7](https://www.python.org/) or greater

- A computer with internet that can be left running 24/7

- Some cash to throw at it (I started with $100, but got impatient and put more in over time)

*Note: Windows 10 may have an issue with time.sleep(). I didn't test much, but I would recommend [a linux system](https://www.raspberrypi.org/) over Windows for this application

### Setup

I use a raspberry pi connected directly to the router via ethernet cable, but any system will do provided that it runs nearly 24/7

1. Download the repo
2. Move the stockStuff folder outside the repo to create the folder structure as seen below
3. Create an Alpaca account, populate keys in the apikeys.txt, and set the desired isPaper value in stonkbot.config (isPaper=0 is live trading, isPaper=1 is paper trading)
4. Install any missing python modules (suggest also installing "screen" or "tmux" package if running on raspberry pi)
5. Run continuously and wait (it works best if left alone other than to check for errors and provide some masochism)
6. ???
7. Profit


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

*The root folder name does not matter. The stockStuff folder needs to be moved from the repo to the location shown above

## File Description
stonkBot.py - The main file to run - this was more useful when testing a number of functions all located in alpacaalgos.py, however it now serevrs as a clean/simple file to run everything. Run ```sudo python3 stonkbot.py```

alpacaalgos.py - Contains the logic and error checking for actually buying and selling stocks

alpacafxns.py - Functions that require an Alpaca API query

otherfxns.py - Other functions that do not require an Alpaca API query (i.e. functions that query the NASDAQ API, or provide the logic to determine which stocks to buy)

stonkBot.config - config file for settings in the files listed above.

stockStuff/ - contains data that won't be synced with the repo (api keys, latest trades, and stock histories (these are cleared every Friday evening)) - **the folder and its contents needs to be moved to the location shown above for the program to work**

apikeys.txt - Contains the API keys used for Alpaca - the file in the repo should be filled in with your information

latestTrades.json - Contains the stock name and the latest trade date and type for the stock

Depreciated Functions, etc/ - Contains old functions and ideas for algorithms that are no longer in use (either tested to be not profitable, or determined to be too simplistic - in my opinion, good for research and ideas, and that's about it)

## Running and Output Interpretation

Depending on how you have your file permissions set, this may need to run as sudo in order to read/write the stockStuff files

The output should look something akin to this:

![Sample Output](https://github.com/steveman1123/stonkBot/blob/master/sampleOutput.jpg?raw=true)

This is designed to run 24/7/365 with no human interaction. It may appear to be in a useless loop if you don't have any shares held in anything. Please wait at least a full day of running before filing an issue. If you don't have shares held, then it may appear to be doing nothing for most of the day.

Generally it seems that it takes about 5 weeks (+/- 3 weeks) after the initial jump to jump a second time.

From running between 2020-07-14 to 2021-02-21, I have gotten an average growth rate of 1.06%/day with a standard deviation of 3.98% (accounting for bad data (reverse splits that weren't caught, and a power outage), the adjusted average and standard deviation are 1.17% and 2.92% respectively)

![Daily Returns](https://github.com/steveman1123/stonkBot/blob/master/dailyReturns.jpg?raw=true)

## Resources
[Alpaca](https://alpaca.markets/)

[MarketWatch Stock Screener](https://www.marketwatch.com/tools/stockresearch/screener/)

[Stocks Under $1](https://stocksunder1.org/)

[NASDAQ API Documentation](https://github.com/steveman1123/stonkBot/blob/master/NASDAQ_API_DOC.md)

## Issues
There are still issues. I've done my best to account for any failings, but if there's something that stops the program and is not caught by a TODO, then report it.

## Disclaimer
I do not claim to be a financial expert and cannot be held accountable for any losses you may incur as a result of using this software
