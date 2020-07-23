import requests
symb = 'MSFT'
url = 'https://api.nasdaq.com/api/quote/{}/info?assetclass=stocks'.format(symb)

print(requests.request('GET',url).text)
