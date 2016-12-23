#!/usr/bin/python

import csv
from wesparatinglib import *
import os
import sys 

RATNAME = "betatrunc.dat"
TOUIDX = "tou_idx.csv"
#rootDir = "../Tournaments/"    # Relative path -- this is where I unzipped the tournaments into
 #for filename in [ y for y in files if '.tou' in y]:  # only want .tou files
with open(TOUIDX,'r') as f:
	for row in f.readlines():
  # do stuff here 
		LONGROW = row.split(",")
		TOUPATH = "../" + row[6:9] + "/" + LONGROW[2] + "/"
		#TOUNAME = str(LONGROW[3]) + ".tou"
		TOUNAME = os.path.join(row[6:10], LONGROW[1], LONGROW[3]) + ".tou"
		print TOUNAME #debug
		tournament = Tournament(RATNAME, TOUNAME)
		print tournament.getName()
		print tournament.getDate()
		tournament.calcRatings() #calls up 'calcNewRatingBySpread'
		RATNAME = TOUNAME.replace('.tou', '.RT2') #replace old rating file for new iteration
		print RATNAME + "\n"
		with open(RATNAME, 'w') as g:
			tournament.outputRatfile(g)
			ST2FILE = TOUNAME.replace('.tou', '.ST2')
			with open(ST2FILE, 'w') as g:
				tournament.outputResults(g)

