import urllib

#Function to get URLs for past World Othello Championship game transcripts
def pullURLs(inputURL):
	handle = urllib.urlopen(inputURL)

	allHTML = handle.read()
	lines = allHTML.split('\n')

	before = lines[2653:2679]
	second = []

	for i in before:
		temp = i.split('href="')
		if len(i) > 150:
			second.append(temp)

	third = []

	for i in second:
		for j in i:
			if j[0] == 'h':
				temp = j.split('"')
				third.append(temp[0])

	fourth = []

	for i in range(len(third)):
		if i % 2 == 1:
			fourth.append(third[i])

	return fourth

url = 'http://othellonews.weebly.com/woc-files-1977.html'
urls = pullURLs(url)

def pullData(transcriptURL):
	fourth = []
	for i in range(len(transcriptURL)):
		curURL = transcriptURL[i]

		newHandle = urllib.urlopen(curURL)

		curHTML = newHandle.read()
		lines = curHTML.split('\n')

		first = lines[38:39]
		second = first[0].split('/style')
		third = second[2].split('</span></p><p><span>')
		third[0] = third[0].replace("&nbsp;", "")
		third[0] = third[0].replace("><p><span>", "")
		third.pop()
		for j in third: 
			temp = j.split(" ")
			f = ''
			s = ''
			if len(temp) > 0:
				for k in temp:
					k = k.replace(" ", "")
					if len(k) > 0 and k[0].isdigit():
						f = k
				s = temp[-1].replace("\xc2\xa0", "")

				fourth.append((f,s))
	return fourth

allGames = pullData(urls)
noRepeats = []

for i in range(len(allGames)):
	b = True
	for j in range((i+1),len(allGames)):
		if allGames[i][0] == allGames[j][0]:
			if allGames[i][1] == allGames[j][1]:
				b = False
	if b == True:
		if len(allGames[i][1]) == 120:
			noRepeats.append(allGames[i])

f = open('transcripts.txt', 'w')
for i in noRepeats:
	if len(i[0]) > 1 and len(i[1]) > 1:
		f.write("{0}, {1} \n" .format(i[0],i[1]))
f.close()