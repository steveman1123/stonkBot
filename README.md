# stonkBot
The first go at a stock trading bot using Alpaca API

Additionally, it uses AlphaVantage and a few other external sites for simulating on past data.

Please be aware that this is a my first _real_ "software engineering" project, and a personal project at that, so the code is by no means pretty, organized well, optimized, etc. It's meant for non-day trading (i.e. having less than $25k to throw around).

There are a number of different algorithms that can be found in the alpacaalgos file. As of 2020-07-12, algo12 and algo13 are the most up-to-date and operable methods. Algo10 is fundamentally different than the previous ones, and algo13 is also fundamentally different than the previous ones



## API Keys
The apikeys file has the actual keys removed for the REST APIs - if you want to try it out, **you will need to get your own Alpaca and AlphaVantage keys** and populate the key file



## External Resources
[Alpaca](https://alpaca.markets/)

[AlphaVantage](https://alphavantage.com/)

[Stocks Under $1](https://stocksunder1.org/)

[NASDAQ API](https://api.nasdaq.com/api/quote/MSFT/info?assetclass=stocks)

[MarketWatch Stock Screener](https://www.marketwatch.com/tools/stockresearch/screener/)



Copyright 2020 Steven Williams

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.