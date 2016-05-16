class node(object):
	def __init__(self, value):
		self.value = value
		self.count = 0 
		self.wins = 0
		self.winP = 0.0
	def __str__(self):
		return self.value, " ", str(self.count), " ", str(self.wins), " ", str(self.winP)
	def __repr__(self):
		return self.value + " " + str(self.count) + " " + str(self.wins) + " " + str(self.winP)
	def increment(self):
		self.count = self.count + 1
	def winIncrement(self):
		self.wins = self.wins + 1
	def winPercentage(self):
		self.winP = float(self.wins)/self.count

_end = '_end_'

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
		currentDict[0] = _end
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

tomato = makeTrie(chunked, scores)


f = open('tables.txt', 'w')
f.write("{0}" .format(tomato))
f.close()