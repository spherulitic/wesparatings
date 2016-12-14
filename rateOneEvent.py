#!/usr/bin/python

from wesparatinglib import *
import os
import sys

RATNAME = 'rating.dat'
TOUNAME = '06wysc.tou'

tournament = Tournament(RATNAME, TOUNAME)

print tournament.getName()
print tournament.getDate()
tournament.calcRatings()
tournament.outputResults(sys.stdout)
#for section in tournament.getSections():
#	print section.getName()
#	for player in section.getPlayers():
#		#print "getName"			
#		#List out the names of players
#		print player.getName()
###playerlist = PlayerList(object)		
###for player in playerlist.getPlayerByName():
###	print name
##	
##print "Show games for Round 1\n"
###retrieve a specific round in the tourney "For each game"
#i=1
#for game in tournament.getSections()[0].getRounds()[i].getGames():
#	for player, score in game.getResult().iteritems():
#	#Let the magic happen
#		print "{0} ({1}): {2}".format(player.getName(), player.getInitRating(), score)
