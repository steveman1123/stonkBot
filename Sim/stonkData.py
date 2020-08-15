import requests, os.path, json
from matplotlib import pyplot as plt

keyFile = open("apikeys.key","r")
apiKeys = json.loads(keyFile.read())
keyFile.close()

symb = 'XSPA'

# if file exists, use that data, else make the file
if(not os.path.isfile(symb+".txt")):
  url = 'https://www.alphavantage.co/query'
  params= {
    'apikey' : apiKeys["ALPHAVANTAGEKEY"],
    'function' : 'TIME_SERIES_DAILY', #daily resolution (open, high, low, close, volume)
    'symbol' : symb, #ticker symbol
    'outputsize' : 'full' #upt to 20yrs of data
  }

  response = requests.request('GET', url, params=params).text
  out = open(symb+'.txt','w')

  out.write(response)
  out.close()

stonkFile = open(symb+'.txt','r')
stonkData = json.loads(stonkFile.read())
stonkFile.close()


dateData = stonkData[list(stonkData.keys())[1]] #time series (daily) - index 0=meta data
# oneDate = dateData[list(dateData.keys())[date]] #date to get to
# dateInfo = oneDate[list(oneDate.keys())[info]] #stock info to grab
length = min(int(365/12),len(dateData)-1)

opens = [0]*length
highs = [0]*length
lows = [0]*length
closes = [0]*length
volumes = [0]*length


for i in range(length):
  oneDate = dateData[list(dateData.keys())[length-i]] #date to get to
  opens[i] = float(oneDate[list(oneDate.keys())[0]]) #stock info to grab
  highs[i] = float(oneDate[list(oneDate.keys())[1]])
  lows[i] = float(oneDate[list(oneDate.keys())[2]])
  closes[i] = float(oneDate[list(oneDate.keys())[3]])
  volumes[i] = float(oneDate[list(oneDate.keys())[4]])


startDate = 0 #date to start investing
myBal = [0]*length
myEq = [0]*length
monies = [0]*length


myBal[startDate] = 100 #starting buying power
startEq = 0
sharesHeld = 0
minDays2Hold = 1
buyDay = startDate
sellPrice = 0

sellUpPerc = 10 # stock to sell up
sellDnPerc = 15 # stock to sell down
endRatio = 1.2 #end if current portfolio is this many times larger than the start
maxLoss = 50 #max acceptable loss TODO: make a function of time

for i in range(startDate+1,length):
  myEq[i] = opens[i]*sharesHeld
  myBal[i] = myBal[i-1]

  if((opens[i]>=sellPrice) and sharesHeld==0):
    #buy
    sharesHeld = int(myBal[i]/opens[i])
    myEq[i] = sharesHeld*opens[i]
    myBal[i] = myBal[i]-myEq[i]
    startEq = myEq[i]
    buyDay = i
  elif(((i-buyDay) >= minDays2Hold) and (myEq[i]>(1+sellUpPerc/100)*startEq or myEq[i]<(1-sellDnPerc/100)*startEq)):
    # input(str(myEq[i]>(1+sellUpPerc/100)*startEq)+ str(myEq[i]<(1+sellDnPerc/100)*startEq))
    #sell
    myBal[i] = myBal[i] + myEq[i]
    myEq[i]=0
    sharesHeld = 0
  else: #hold
    myEq[i] = opens[i]*sharesHeld

  monies[i] = myEq[i]+myBal[i] #total portfolio value

  # input(str(i)+" - Shares: "+str(sharesHeld)+" - Equity: "+str(myEq[i])+" - Monies: "+str(monies[i]))
  if(monies[i]>=endRatio*monies[startDate+1] or monies[i]<=(1-maxLoss/100)*monies[startDate+1]):
    if(sharesHeld>0):
      myBal[i] = myBal[i] + myEq[i]
      myEq[i]=0
      sharesHeld = 0
      sellPrice = opens[i]
      print(sellPrice)

    for j in range(i,len(monies)):
      monies[j] = monies[i]
      myBal[j] = myBal[i]

    if(monies[i]>=endRatio*monies[startDate+1]):
      print(str(i)+" - "+str(endRatio))
      break




plt.figure(0)
plt.subplot(311)
plt.plot(opens)
plt.title('opens')
plt.subplot(312)
plt.title('Monies')
plt.plot(monies)
plt.subplot(313)
plt.title('myEq/myBal')
plt.plot(myEq)
plt.plot(myBal)
plt.show()
