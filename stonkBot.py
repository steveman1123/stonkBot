#!/usr/bin/python

import alpacaalgos as algos

def main():
  print("\nStarting up...\n")
  algos.a.checkValidKeys()
  
  if(len(algos.a.getPos())==0):
    print("Will start buying "+str(algos.a.o.c['buyTime'])+" minutes before next close")
  
  algos.mainAlgo() #used to easily switch between the different algos in the algo file

if __name__ == '__main__':
  main()
