#!/usr/bin/python

import datetime
import string
import math
import os 
import sys
import time 
global tournamentDate
tournamentDate = 20060101
global MAX_DEVIATION
MAX_DEVIATION = 300.0

class Tournament(object):
  def checkIndex(self,ratfile,toufile):
    with open(toufile) as f:
      line1 = f.readline().split(',', 1)  # First line: *M31.12.1969 Tournament Name
                  # We get a list: [ '*M31.12.1969', 'Tournament Name']
      self.tournamentName = line1[1].strip()
      try:
        self.tournamentDate = datetime.date(int(line1[0][6:10]), int(line1[0][0:1]), int(line1[0][3:5]))
        print "TOU date parsed as: {0}".format(line1[0][6:10]), int(line1[0][0:1]), int(line1[0][3:5])
      except ValueError:
        print "Cannot parse tournament date: {0} {1} {2}".format(line1[0][2:4], line1[0][5:7], line1[0][8:12])
        self.tournamentDate = datetime.date.today()
        
      restOfFile = f.readlines()

      for line in restOfFile:
        line = f.readline().split(',', 1)  # First line: *M31.12.1969 Tournament Name
                  # We get a list: [ '*M31.12.1969', 'Tournament Name']
        self.tournamentName = line[1].strip()
      try:
        self.tournamentDate = datetime.date(int(line1[0][6:10]), int(line1[0][0:1]), int(line1[0][3:4]))
        print "TOU date parsed as: {0}".format(line1[0][6:10]), int(line1[0][0:1]), int(line1[0][3:4])
      except ValueError:
        print "Cannot parse tournament date: {0} {1} {2}".format(line1[0][2:4], line1[0][5:7], line1[0][8:12])
        self.tournamentDate = datetime.date.today()

        #if (line.strip() == '*** END OF FILE ***'):
        #  continue
        #elif (line[0] == '*') :
        #  currentSection = Section(line[1:]) # Create section object
        #  self.addSection(currentSection)
        #  continue
        #elif (line[0] == ' '):
        #  continue
        ## Don't know if this is the best way to do this
        #playerName = ' '.join([word for word in line.split() if any(letter in word for letter in string.letters) ])  
        #try:
        #  gameScoreList = [ int(word.replace('+', '')) for word in line.split() if any(char in word for char in string.digits) and '@' not in word ]
        #except ValueError:
        #  print "Error parsing tou file {0}. Number fields contain non-digits. Current player: {1}".format(toufile, playerName)

    
  def __init__(self, ratfile, toufile):
    
    self.globalList = PlayerList(ratfile)
    self.sections = [ ] # empty list of Section objects

    with open(toufile) as f:
      line1 = f.readline().split(' ', 1)  # First line: *M31.12.1969 Tournament Name
                  # We get a list: [ '*M31.12.1969', 'Tournament Name']
      self.tournamentName = line1[1].strip()
      try:
        self.tournamentDate = datetime.date(int(line1[0][8:12]), int(line1[0][5:7]), int(line1[0][2:4]))
      except ValueError:
        print "Cannot parse tournament date: {0} {1} {2}".format(line1[0][2:4], line1[0][5:7], line1[0][8:12])
        self.tournamentDate = datetime.date.today()

      restOfFile = f.readlines()

      for line in restOfFile:
        if (line.strip() == '*** END OF FILE ***'):
          continue
        elif (line[0] == '*') :
          currentSection = Section(line[1:]) # Create section object
          self.addSection(currentSection)
          continue
        elif (line[0] == ' '):
          continue
        # Don't know if this is the best way to do this
        playerName = ' '.join([word for word in line.split() if any(letter in word for letter in string.letters) ])  
        try:
          gameScoreList = [ int(word.replace('+', '')) for word in line.split() if any(char in word for char in string.digits) and '@' not in word ]
        except ValueError:
          print "Error parsing tou file {0}. Number fields contain non-digits. Current player: {1}".format(toufile, playerName)

        if (len(gameScoreList) == 1):
          continue # this is a high word listed at the top of the file

        if (len(gameScoreList) == ValueError): #continue anyway
          continue # this is a high word listed at the top of the file

        currentPlayer = self.globalList.getPlayerByName(playerName)
        if currentPlayer is None:
#          print "Creating new player {0}".format(playerName)
          self.globalList.addNewPlayer(Player(playerName))
          currentPlayer = self.globalList.getPlayerByName(playerName)

        currentSection.addPlayer(currentPlayer)
        if not currentPlayer.isUnrated:
          currentPlayer.adjustInitialDeviation(self.tournamentDate)
        currentPlayer.setLastPlayed(self.tournamentDate)

        # TOU FORMAT:
        # Mark Nyman           2488  16 2458  +4 2489 +25 2392   2  345  +8  348
        # Name       (score with prefix) (opponent number) (score with prefix) (opponent number)
        # Score Prefixes: 1 = Tie, 2 = Win
        # Opponent Prefixes: + = player went first
            
        # gameScoreList will have [ 2488, 16, 2458, 4, etc ]
    #    print gameScoreList
        gameScores = [ i%1000 for i in gameScoreList[0::2] ] # take every second member of the list mod 1000
        opponents = gameScoreList[1::2] # take every odd member of the list
#        print currentPlayer.getName()
#        print gameScores
#        print opponents
    
        # For each score, pair in the list:
        # 1. get the nth round. if it doesn't exist, create it.
#        print "{0} game scores; {1} opponents".format(len(gameScores), len(opponents))
        for roundNumber in range(len(gameScores)):
          roundObject = currentSection.getRoundByNumber(roundNumber)
          if roundObject is None:
#            print "Creating round {0}".format(roundNumber)
            roundObject = Round()  
            currentSection.addRound(roundObject)
        # 2. Find the opponent
          try:
            opponent = currentSection.getPlayerByNumber(opponents[roundNumber])
          except IndexError:
            print "Error reading tou file {0}. Fewer opponents than rounds. Current player: {1}".format(toufile, playerName)
      
        # 3. If we know the opponent, we have already parsed their line and created the game object
        #    If not, create a new game object. We will match the opponent to the current player when we parse them
          gameObject = roundObject.getGameByPlayer(opponent)
          if gameObject is None:
            gameObject = Game()
            roundObject.addGame(gameObject)
    #        print "Creating game object for {0} in round {1}".format(currentPlayer.getName(), roundNumber)
    #      else:
    #        print "Found game object for round {0} with {1} vs {2}".format(roundNumber, currentPlayer.getName(), opponent.getName())
          gameObject.addPlayerResult(currentPlayer, gameScores[roundNumber])  
    # now that we are done populating our data structures, let's have each player calculate his wins and spread
    for s in self.sections:
      s.tallyPlayerResults()

        


  def getName (self):
    return self.tournamentName

  def getDate (self):
    return self.tournamentDate

  def getSections (self):
    return self.sections 

  def addSection(self, section):
    self.sections.append(section)

  def calcRatings(self):
  ##### FIRST here -- calculate ratings for unrated players first
  #####   Set their pre-tournament rating to 1500 and deviation to 400 to start
  #####   Rerun the "calculate ratings for unrated players" part repeatedly, 
  #####     using the previously calculated rating as their initial rating
  #####     until the output rating for these players equals the input rating
  #####   THEN for rated players only:
    MAX_ITERATIONS = 50
    for s in self.sections:
      converged = False
      iterations = 0
      opponentSum = 0.0
      while not converged and iterations < MAX_ITERATIONS: 
          converged = True #i.e. when in the loop and 'False' is returned, keep iterating
          
          for p in [dude for dude in s.getPlayers() if dude.isUnrated ]: #for an unrated dude       
              unratedOpps = 0.0
              try:
                unratedOppsPct = unratedOpps/float(len(p.getOpponents()))
              except ZeroDivisionError:
                undatedOppsPct = 0.0
              if unratedOppsPct >= 0.4:
#              if (unratedOpps/float(len(p.getOpponents()) + 1) >= 0.4):
		    for g in s.getPlayers():
			opponentMu = g.getInitRating()
			opponentSum += opponentMu
			opponentAverage = opponentSum/len(s.getPlayers())
			p.setInitRating(opponentAverage)
			preRating = p.getInitRating()
			p.setUnrated(False)
			#p.setUnrated(False)
			print "p played insufficient rated players, initialised to opponentAverage \n"
				
              else:
                    preRating = p.getInitRating()
                    #print "else was executed"
			
              p.calcNewRatingBySpread() #calculates rating as usual
              #converged = (converged and abs(preRating - p.getNewRating()) < 20)
              converged = (converged and preRating == p.getNewRating())
              #print converged
              p.setInitRating(p.getNewRating()) 
              p.setInitDeviation(MAX_DEVIATION)
              iterations = iterations + 1   
              #print "Rating unrated player" + str(p) + ": " + str(p.getNewRating()) + "\n"
         
      for p in [ dude for dude in s.getPlayers() if not dude.isUnrated ]:
        p.calcNewRatingBySpread()

  def outputResults(self, outputFile):#now accepts 2 input (20161214)
        # handle should be open for writing
    for s in self.sections:
		outputFile.write("Section {:1}".format(s.getName()))
		#outputFile.write("\n")
		outputFile.write("{:21} {:10} {:7} {:8} {:8}".format("NAME", "RECORD", "SPREAD", "OLD RAT", "NEW RAT"))
		outputFile.write("\n")
		for p in sorted(s.getPlayers(), key=lambda x: (x.getWins()*100000)+x.getSpread(), reverse=True):
			outputFile.write("{:21} {:10} {:7} {:8} {:8}".format(p.getName(), str(p.getWins()) + "-" + str(p.getLosses()), p.getSpread(), p.getInitRating(), p.getNewRating()))
			outputFile.write("\n")
		
		outputFile.write("\n") #section break
		
		for p in [dude for dude in s.getPlayers() if dude.isUnrated ]:
				outputFile.write("{:21} is unrated \n".format(p.getName()))
		outputFile.write("\n") #section break
		
    rootDir = "../"
    touname = self.tournamentName
    for root, dirs, files in os.walk(rootDir):
      for filename in [ y for y in files if 'tou' in y ]: #for ANY file ending with .tou
        TOUFILE = os.path.join(root, filename)
    #TOO MANY COPIES!
	
    #for s in self.sections:
    #  outFile = open('{0}.ST2'.format(touname), 'a')
    #  outFile.truncate(0)
	##DEBUG      print "Section {0} \n".format(s.getName)
    #  outFile.write("{0} \n".format(s.getName()))
	##DEBUG      print "{:21} {:10} {:7} {:8} {:8} {:8} \n".format("NAME", "RECORD", " SPREAD", "    Old    ", " New   ", "Change", " New Dev")
    #  outFile.write("{:21} {:10} {:7} {:8} {:8} {:8}{:8}\n".format("NAME", "RECORD", " SPREAD", "    Old    ", " New   ", "Change", "New Dev"))
    #  for p in sorted(s.getPlayers(), key=lambda x: (x.getWins()*100000)+x.getSpread(), reverse=True):
    #    #print "{:21} {:10} {:7} {:8} {:8} {:8}".format(p.getName(), str(p.getWins()) + "-" + str(p.getLosses()), p.getSpread(), p.getInitRating(), p.getNewRating(), p.getNewRating()-p.getInitRating())
    #    outFile.write("{:21} {:10} {:7} {:8} {:8} {:8} {:8} \n".format(p.getName(), str(p.getWins()) + "-" + str(p.getLosses()), p.getSpread(), p.getInitRating(), p.getNewRating(), p.getNewRating()-p.getInitRating(),   p.newRatingDeviation))
    #  outFile.write("This tournament's rating is complete :)")
    #
    #  #with open('{0}.ST2', 'r') as rat:
    #  #with open(outFile, 'r') as rat:
    #  #  data = rat.read().splitlines(True)
    #  #with outFile as fout:
    #  #  fout.writelines(data[1:])
    #  outFile.close()

  def outputRatfile(self, outFile):
    outFile.write("NICK     {:20}{:5}{:5} {:9}{:6}\n".format("Name", "Games", " Rat", "Lastplayed", "New Dev"))
    for p in sorted(self.globalList.getAllPlayers().values(), key=lambda p: (p.getNewRating()), reverse=True):
  
	try:
		if (p.getLastPlayed().strftime('%Y%m%d') > 20051231): #exterminate the old
			outFile.write("         {:20}{:5}{:5} {:9}{:6} \n".format(p.getName(), p.getCareerGames(), p.getNewRating(), p.getLastPlayed().strftime('%Y%m%d'), p.newRatingDeviation))
	except ValueError:
		print str(p.getName) + "'s lastPlayed was" + str(p.getLastPlayed())
  #inserted p.getNewLastPlayed on 15th Dec
  #print "This tournament's rating is complete :)"
class Section(object):

  def __init__ (self, name):
    self.players = [] # List of Player objects
    self.rounds = [] # list of Round objects
    self.highgame = { } # should be dict containing Player, Round, Score
    self.name = name

  def addPlayer(self, player):
    self.players.append(player)

  def addRound(self, rnd):
    self.rounds.append(rnd)
  def getPlayers(self):
    return self.players
  
  def getName(self):
    return self.name
  def getRoundByNumber(self, number):
    try:
      return self.rounds[number] 
    except IndexError:
      return None
  def getPlayerByNumber(self, number):
    try:
      return self.players[number-1] # player numbers in the tou file are 1-based
    except IndexError:
      return None
  def getRounds(self):
    return self.rounds

  def tallyPlayerResults(self):
    for p in self.players:
      p.tallyResults()

class Player(object):

  def __init__(self, playerName):
    self.name = playerName
    self.initRating = 0
    self.initRatingDeviation = 0.0
    self.careerGames = 0
    self.wins = 0.0
    self.losses = 0.0
    self.spread = 0
    self.ratingChange = 0
    self.newRating = 0
    self.newRatingDeviation = 0.0
    self.games = [] # list of Game objects
    self.lastPlayed = datetime.date(1999, 12, 31) 
    self.isUnrated = False

  def __str__(self):
    return self.name

  def tallyResults(self):
    for g in self.games:
      score1 = g.getMyScore(self)
      score2 = g.getOpponentScore(self)
      if (score1 > score2):
        self.addGameResult(True, score1-score2)
      else:
        self.addGameResult(False, score2-score1) # for Ties, the "win" boolean doesn't matter

  def getWins(self):
    return self.wins
  def getLosses(self):
    return self.losses
  def getSpread(self):
    return self.spread
    
  def setInitRating(self, rating, dev=MAX_DEVIATION):
    self.initRating = rating
    self.initRatingDeviation = dev
    
    if (self.initRatingDeviation == 0):
      self.initRatingDeviation = MAX_DEVIATION
    else:
      self.initRatingDeviation = dev

    self.newRating = rating
    self.newRatingDeviation = dev

  def setInitDeviation(self, deviation):
    self.initRatingDeviation = deviation

  def setCareerGames(self, games):
    self.careerGames = games
      
    #if self.getOpponentByGame(games) != self:   #problematic
    #  self.careerGames += 1

  def setLastPlayed(self, date):
    self.lastPlayed = date

  def getName (self):
    return self.name
    
  def getDate (self):
    return self.tournamentDate

  def getInitRating(self):
    return self.initRating
  
  def getInitRatingDeviation(self):
    return self.initRatingDeviation

  def getNewRating(self):
    return self.newRating
  def getNewRatingDeviation(self):
    return self.newRatingDeviation
  def getCareerGames(self):
    return self.careerGames
  def setUnrated(self, unrated):
    self.isUnrated = unrated

  def getLastPlayed(self):
    return self.lastPlayed
  
  #def getNewLastPlayed(self):
  #  return self.newLastPlayed
    
  def addGameResult(self, win, spr): 
  # win should be a boolean
  # spread should always be positive
    if (spr == 0):
      self.wins += .5
      self.losses += .5
    elif win:
      self.wins += 1
      self.spread += spr
    else:
      self.losses += 1
      self.spread -= spr

  def addGame(self, game):
    self.games.append(game)
    
    if self.getOpponentByGame(game) != self:
      self.careerGames += 1
  def getScoreByRound(self, r):
    return self.games[r].getResult().self

  def getOpponentByRound(self, r):
    return [p for p in self.games[r].getResult().keys() if (p != self) ][0]
  def getOpponentByGame(self, g):
    # return self for byes
    try:  
      return [p for p in g.getResult().keys() if (p != self)][0]
    except IndexError:
      return self
  def getOpponents(self):
    return [self.getOpponentByGame(g) for g in self.games]   # returns a list of all opponents

  def adjustInitialDeviation(self, tournamentDate):
	c = 10
#    print "Adjusting deviation for " + str(self)
#    print "\nBefore: " + str(self.initRatingDeviation) + "\n"

	inactiveDays = int((tournamentDate - self.lastPlayed).days)
	#DEBUG:
	#print tournamentDate
	#print self.lastPlayed
	#print "Inactive Days: " + str(inactiveDays)
	self.initRatingDeviation = min(math.sqrt(math.pow(int(self.initRatingDeviation), 2) + (math.pow(c, 2)*inactiveDays)), MAX_DEVIATION)
          

  def calcNewRatingBySpread(self): #this rates 1 player
    """
    An implementation of the Norwegian rating system.
    """
    tau = 120 # to be adjusted for better results, WARNING: tau+beta<100
    #increase in tau REDUCES rat change for rated players
    beta = 5 #multiplier applied per one point of expected spread, see nu.append
    mu = self.initRating
    #if (self.p.getLastPlayed().strftime('%Y%m%d') < 20000101):
    #  mu -=400
    sigma = self.initRatingDeviation #Initialise rating deviation of plaeyr
    rho = [] # opponent uncertainty factor
    nu = [] # performance rating by game
    for g in self.games:
      opponent = self.getOpponentByGame(g)
      if (opponent == self):
        continue # skip byes
      opponentMu = opponent.getInitRating()
      #if (opponentMu > 1600):
      #  tau -= opponentMu/400 #suppose opp is Nigel Richards, then he is 'certainly' a good player
      opponentSigma = opponent.getInitRatingDeviation()
      rho.append(float(((beta**2) * (tau**2)) + opponentSigma**2))
      gameSpread = g.getResult()[self] - g.getResult()[opponent]
      if (gameSpread > -1):
        #if(gameSpread > 100):
          #nu.append(float(opponentMu + math.sqrt(beta * gameSpread ))  #increase vol
        
        #else:
          #nu.append(float(opponentMu + math.sqrt(beta * gameSpread)))  #let's mess around
        #if(gameSpread > 300): #spreadcap
        #  nu.append(float(opponentMu + beta * 300))        
        #else:
        nu.append(float(opponentMu + beta * gameSpread))
      else:
        #nu.append(float(opponentMu - math.sqrt(-beta * gameSpread))) #ensure deviations do not subtract
        nu.append(float(opponentMu + beta * gameSpread))
    sum1 = 0.0 
    sum2 = 0.0 
    for m in range(len(rho)): #for each item in the rho list
		sum1 += 1.0/rho[m] #summation of inverse of uncertainty factors (to find 'effective' deviation)
		sum2 += nu[m]/rho[m] #summaton of (INDIVIDUAL perfrat divided by opponent's sigma)
    #print sigma
    #print rho
    #print nu
    #print self, sum1, sum2
    invsigmaPrime = (1.0/(sigma**2)) + sum1 #takes invsquare of original dev, add inv of new sum of devs
    sigmaPrime = 1.0/invsigmaPrime #flips it back to get 'effective sigmaPrime'
    #print sigmaPrime
    muPrime = sigmaPrime * ( (mu/(sigma**2)) + sum2) #calculate new rating using NEW sigmaPrime
    
	#handle short tourneys
    
    change = muPrime - mu

	  #SHORT TOURNEY CAP
    if (len(self.games) < 8):
	  #change *= math.sqrt(len(self.games)/8)
	  change *= len(self.games)/8.0

	#GLOBAL CAP
    if (change > len(self.games)*50.0):
	  change = 50.0*len(self.games)
	  #cap change 

	  
    muPrime = mu + change
    self.newRating = int(round(muPrime))
    
    if (self.newRating < 300):
      self.newRating = 300
      
    #if (self.newRating < 1000): #believes all lousy players can improve :))
    #  sigmaPrime += math.sqrt(1000 - self.newRating)
    self.newRatingDeviation = round(math.sqrt(sigmaPrime),1)
    
    if (self.newRatingDeviation < 80):
      if(self.newRating < 1800):
        self.newRatingDeviation = 80  #minimum value for deviation    
    if (self.newRatingDeviation < 50):
      self.newRatingDeviation = 50


class Round(object):

  def __init__(self):
    self.games = [ ]

  def getGameByPlayer(self, player):    # Returns a game object if a game w/ that player exists in the round, else returns None
    for game in self.games:
      if (player in game.getPlayers()) :
        return game
    return None

  def addGame(self, game):
    self.games.append(game)

  def getGames(self):
    return self.games

class Game(object):

  def __init__(self):
    # s1 and s2 are integers
    # r is a boolean -- is this a rated game?
    self.result = { } # dict with { PlayerObject: score }  
    self.rated = True

  def addPlayerResult(self, player, score):
    self.result[player] = score
    player.addGame(self)

  def getPlayers(self):
    return self.result.keys()

  def isRated(self):
    return self.rated

  def setRated(self, r):
    self.rated = r

  def getResult(self):
    return self.result

  def getMyScore(self, player):
    return self.result[player]

  def getOpponentScore(self, player):
    try:
      opponent = [ p for p in self.result.keys() if (p != player) ][0]
      return self.result[opponent]
    except IndexError:
      return self.result[player]   # If it is a bye and the player was paired with themself, return their score here

class PlayerList(object): # a global ratings list
  def __init__(self, ratfile):
    # Load all current players

    # maybe we should do this by creating a separate PlayerList object and init it with the ratfile?

    self.allPlayers = { } # in Python a dict is a data structure like a hash in Perl
         # we'll store all the players in a dict with the name as the key
         # in practice we should find a better way than loading all players into memory 

    with open(ratfile) as f:
      next(f) # skip headings

      for row in f:
        #print row
        nick = row[0:4]
        state = row[5:8]
        name = row[9:29].strip()  # strip() removes extra spaces, like perl's chomp()
        careerGames = int(row[30:34]) # python makes you explicitly change a string like "345" into an int 345
        #print "Career Games:" + str(careerGames)
        rating = int(row[35:39])

		
#DEVELOPING TOLERANCE FOR HORRIBLY FORMATTED TOU FILES GRRR!
        logFile = open('log.txt', 'a+')
        try:
          lastPlayed = datetime.date(int(row[40:44]),int(row[44:46]), int(row[46:48])) 

          #print name + " last played: " + str(lastPlayed)
        except ValueError:
		  try:
			lastPlayed = datetime.date(int(row[40:44]),int(row[46:48]), int(row[44:46])) 
		  #lastPlayed = datetime.date.today()
			print "Corrected weird date:" + str(int(row[40:44]))+str(int(row[44:46]))+str(int(row[46:48]))
		  except ValueError:
			print "One last try on" + str(ratfile) + "!"
			logFile.write("Problem with ratfile" + str(ratfile) + "\n")
			
			try:
				lastPlayed = datetime.date(int(row[39:43]),int(row[43:45]), int(row[45:47]))
				print "Reading 1 column to the left"
			
			except ValueError:
				try:
					lastPlayed = datetime.date(int(row[41:45]),int(row[45:47]), int(row[47:49])) 
					print "Reading 1 column to the right"
				except ValueError:
					print "I give up!!!"
					lastPlayed = int("20060101")
	
		
        try:
          ratingDeviation = float(row[49:])
        except ValueError:
          ratingDeviation = MAX_DEVIATION
        self.allPlayers[name] = Player(name) # creates a new Player object and runs __init__ with name as the argument
        self.allPlayers[name].setInitRating(rating, ratingDeviation)
        self.allPlayers[name].setCareerGames(careerGames)
        self.allPlayers[name].setLastPlayed(lastPlayed)
        self.allPlayers[name].setUnrated(False)

      # output what we have to show the file was parsed
      # note that a dict is unsorted. we can deal with sorting later by converting dict to another data structure

    #  for player in allPlayers.itervalues():
#    print "Name: {0}, Initial Rating: {1}, Career Games: {2}, Last Played: {3}".format(player.getName(), player.getInitRating(), player.getCareerGames(), player.getLastPlayed())
    
  def addNewPlayer(self, player, initRating=1500, careerGames=0, lastPlayed=datetime.date.today(), ratingDeviation=MAX_DEVIATION, isUnrated=True):
    self.allPlayers[player.getName()] = player
    player.setInitRating(initRating, ratingDeviation)
    player.setCareerGames(careerGames)
    player.setLastPlayed(lastPlayed)
    player.setUnrated(isUnrated)


  def getPlayerByName(self, name):
    try:
      return self.allPlayers[name]
    except KeyError:
      return None

  def getAllPlayers(self):
    return self.allPlayers
    

