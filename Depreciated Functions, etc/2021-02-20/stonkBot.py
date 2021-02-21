#!/usr/bin/python

import alpacaalgos as algos

def main():
  print("\nStarting up...\n")
  algos.a.checkValidKeys()
  
  if(len(algos.a.getPos())==0): #if the trader doesn't have any stocks (i.e. they've not used this algo yet), then give them a little more info
    print("Will generate the stock list "+str(algos.a.o.c['updateListTime'])+" minutes before next close")
    print("Will start buying "+str(algos.a.o.c['buyTime'])+" minutes before next close")

  algos.mainAlgo() #used to easily switch between the different algos in the algo file

if __name__ == '__main__':
  main()
