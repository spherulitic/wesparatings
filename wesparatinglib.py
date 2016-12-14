#!/usr/bin/python

import datetime
import string
import math

class Tournament(object):

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

        currentPlayer = self.globalList.getPlayerByName(playerName)
        if currentPlayer is None:
#          print "Creating new player {0}".format(playerName)
          self.globalList.addNewPlayer(Player(playerName))
          currentPlayer = self.globalList.getPlayerByName(playerName)

        currentSection.addPlayer(currentPlayer)

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
    for s in self.sections:
      for p in s.getPlayers():
        p.calcNewRatingBySpread()

  def outputResults(self, outputFile):
    # handle should be open for writing
    for s in self.sections:
      outputFile.write("Section {0}".format(s.getName))
      outputFile.write("\n")
      outputFile.write("{:21} {:10} {:7} {:8} {:8}".format("NAME", "RECORD", "SPREAD", "OLD RAT", "NEW RAT"))
      outputFile.write("\n")
      for p in sorted(s.getPlayers(), key=lambda x: (x.getWins()*100000)+x.getSpread(), reverse=True):
        outputFile.write("{:21} {:10} {:7} {:8} {:8}".format(p.getName(), str(p.getWins()) + "-" + str(p.getLosses()), p.getSpread(), p.getInitRating(), p.getNewRating()))
        outputFile.write("\n")


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
    self.lastPlayed = datetime.date(1969, 12, 31) 

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
    
  def setInitRating(self, rating, dev=0):
    self.initRating = rating
    self.initRatingDeviation = dev

  def setCareerGames(self, games):
    self.careerGames = games

  def setLastPlayed(self, date):
    self.lastPlayed = date

  def getName (self):
    return self.name

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

  def getLastPlayed(self):
    return self.lastPlayed
  
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

  def calcNewRatingBySpread(self):
    """
    An implementation of the Norwegian rating system.
    """
    tau = 90 # to be adjusted for better results
    beta = 5 # number of rating points difference corresponding to one point of expected spread
    mu = self.initRating
    sigma = self.initRatingDeviation
    rho = [] # opponent uncertainty factor
    nu = [] # performance rating by game
    for g in self.games:
      opponent = self.getOpponentByGame(g)
      if (opponent == self):
        continue # skip byes
      opponentMu = opponent.getInitRating()
      opponentSigma = opponent.getInitRatingDeviation()
      rho.append(float(((beta**2) * (tau**2)) + opponentSigma**2))
      gameSpread = g.getResult()[self] - g.getResult()[opponent]
      nu.append(float(opponentMu + (beta * gameSpread)))
    sum1 = 0.0
    sum2 = 0.0
    for m in range(len(rho)):
      sum1 += 1.0/rho[m]
      sum2 += nu[m]/rho[m]
    
    print rho
    print nu
    print self, sum1, sum2
    sigmaPrime = (1/(sigma**2)) + sum1
    sigmaPrime = 1/sigmaPrime

    muPrime = sigmaPrime * ( (mu/(sigma**2)) + sum2)

    self.newRating = int(round(muPrime))
    self.newRatingDeviation = math.sqrt(sigmaPrime)

    

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

        nick = row[0:4]
        state = row[5:8]
        name = row[9:29].strip()  # strip() removes extra spaces, like perl's chomp()
        careerGames = int(row[30:34]) # python makes you explicitly change a string like "345" into an int 345
        rating = int(row[35:39])

        try:
          lastPlayed = datetime.date(int(row[40:44]),int(row[44:46]), int(row[46:48])) 
        except ValueError:
          lastPlayed = datetime.date.today()

        ratingDeviation = float(row[49:])
        self.allPlayers[name] = Player(name) # creates a new Player object and runs __init__ with name as the argument
        self.allPlayers[name].setInitRating(rating, ratingDeviation)
        self.allPlayers[name].setCareerGames(careerGames)
        self.allPlayers[name].setLastPlayed(lastPlayed)

      # output what we have to show the file was parsed
      # note that a dict is unsorted. we can deal with sorting later by converting dict to another data structure

    #  for player in allPlayers.itervalues():
#    print "Name: {0}, Initial Rating: {1}, Career Games: {2}, Last Played: {3}".format(player.getName(), player.getInitRating(), player.getCareerGames(), player.getLastPlayed())
    
  def addNewPlayer(self, player, initRating=1000, careerGames=0, lastPlayed=datetime.date.today(), ratingDeviation=400):
    self.allPlayers[player.getName()] = player
    player.setInitRating(initRating, ratingDeviation)
    player.setCareerGames(careerGames)
    player.setLastPlayed(lastPlayed)


  def getPlayerByName(self, name):
    try:
      return self.allPlayers[name]
    except KeyError:
      return None

