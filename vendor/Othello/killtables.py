def init():
	global tomato
	global movesTaken
	movesTaken = []

class node(object):
	def __init__(self, value):
		self.value = value
		self.count = 0 
		self.wins = 0
		self.winP = 0.0
	def __str__(self):
		return self.value + " " + str(self.count) + " " + str(self.wins) + " " + str(self.winP)
	def __repr__(self):
		return self.value + " " + str(self.count) + " " + str(self.wins) + " " + str(self.winP)
	def increment(self):
		self.count = self.count + 1
	def winIncrement(self):
		self.wins = self.wins + 1
	def winPercentage(self):
		self.winP = float(self.wins)/self.count

def makeTrie(allGames, allScores):
	root = [None, {}]
	for game in range(len(allGames)):
		currentDict = root
		for move in range(len(allGames[game])):
			if currentDict[1].get(allGames[game][move]) is None:
				currentDict = currentDict[1].setdefault(allGames[game][move],[node(allGames[game][move]),{}])
			else:
				currentDict = currentDict[1][allGames[game][move]]
			currentDict[0].increment()
			if move % 2 == 0:
				if int(allScores[game][0]) > 32:
					currentDict[0].winIncrement()
			else:
				if int(allScores[game][1]) > 32:
					currentDict[0].winIncrement()
			currentDict[0].winPercentage()
		currentDict[1] =None
	return root

trans = []

f = open('transcripts.txt', 'r')
for i in f:
	temp = i.split(', ')
	temp[1] = temp[1].replace(' \n', "")
	trans.append(temp)
f.close()

scores = []
moves = []

for i in range(len(trans)):
	trans[i][0] = trans[i][0].split('-')
	scores.append(trans[i][0])
	moves.append(trans[i][1])

def chunk(lis):
	output = []
	for i in range(0, len(lis), 2):
		output.append(lis[i:i+2])
	return output

chunked = []
for i in moves:
	chunkedMoves = chunk(i)
	chunked.append(chunkedMoves)

def numToLetter(movesIn):
	out = []
	for move in movesIn:
		move = chr(move[0]+64) + str(move[1])
		out.append(move)
	return out

def translateMoves(movesIn):
	temp = []
	if len(movesIn) > 0 :
		if movesIn[0] == 'F5':
			return movesIn
		elif movesIn[0] == 'C4':
			for m in movesIn:
				L0 = ord(m[0]) - 64
				L1 = 0
				if L0 > 4.20:
					dif = L0 - 4
					L1 = chr(5 - dif +64)
				else:
					dif = 5 - L0
					L1 = chr(4 + dif + 64)
				N0 = int(m[1])
				N1 = 0
				if N0 > 4.20:
					dif = N0 - 4
					N1 = 5 - dif
				else:
					dif = 5 - N0
					N1 = 4 + dif
				temp.append(L1 + str(N1))
		else:
			for m in movesIn:
				L0 = ord(m[0]) - 64
				N0 = int(m[1])
				L1 = chr(N0 + 64)
				N1 = L0
				temp.append(L1 + str(N1))
		return translateMoves(temp)

def letterToNum(move):
	if move == 0:
		return None
	return (ord(move[0])-64-1,int(move[1])-1)

def getHighestWinP(dictionary):
	highestKey = ''
	highestWP = -1
	for i in dictionary:
		if dictionary[i][0].winP > highestWP:
			highestKey = dictionary[i][0].value
			highestWP = dictionary[i][0].winP
	return highestKey

def getSuggestion(trie,listIn):
	if listIn == list():
		return 'F5'
	a = translateMoves(numToLetter(listIn))
	dictionary = trie
	for i in a:
		dictionary = dictionary.get(i)
		if dictionary is not None:
			dictionary = dictionary[1]
		else:
			return 0;
	return getHighestWinP(dictionary)

tomato = makeTrie(chunked, scores)

def hello():
	return letterToNum(getSuggestion(tomato[1], movesTaken))