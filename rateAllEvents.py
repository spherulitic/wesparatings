#!/usr/bin/python

import csv
from wesparatinglib import *
import os

RATNAME = "rating.dat"
rootDir = "../tournaments"    # Relative path -- this is where I unzipped the tournaments into
for root, dirs, files in os.walk(rootDir):
  for filename in [ y for y in files if 'tou' in y]:  # only want .tou files
    # do stuff here 
    TOUNAME = filename
    tournament = Tournament(RATNAME, TOUNAME)
    print tournament.getName()
    print tournament.getDate()
    tournament.calcRatings()
    RATNAME = filename.replace('.tou', '.dat')
    with open(RATNAME, 'w') as f:
      tournament.outputResults(f)

