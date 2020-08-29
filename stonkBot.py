#!/usr/bin/python

import alpacaalgos as algos

def main():
  print("\nStarting up...\n")
  algos.a.checkValidKeys()
  isMaster = 1
  if(isMaster):
    algos.mainAlgo() #used to easily switch between the different algos in the algo file
  else:
    #TODO: ping master. if no response
    #populate latest trades with today's trades
    #run alg
    f = open('../stockStuff/latestTrades.json','w')
    f.write(algos.a.getTrades(algos.dt.date.today())) #get today's trades
    f.close()

#TODO: stop main algo if(is not master and master is online/running)
#TODO: edit main algo to run forever if master, or to check periodically for a running master if slacve

if __name__ == '__main__':
  main()
