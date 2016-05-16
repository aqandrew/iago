

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
	moves.append(trans[i][1].replace(" ", ""))

def chunk(lis):
	output = []
	for i in range(0, len(lis), 2):
		output.append(lis[i:i+2])
	return output

moveDic = {}
for i in range(60):
	moveDic[i] = {}

print moveDic, '\n'


for i in moves:
	chunkedMoves = chunk(i)
	for j in range(len(chunkedMoves)):
		strMove = chunkedMoves[j]
		count = 0
		if moveDic[j].get(strMove):
			count = moveDic[j][strMove]
		moveDic[j][strMove] = count+1

for i in moveDic:
	print i+1
	for j in moveDic[i]:
		print j, ':', moveDic[i][j]
	print '\n'