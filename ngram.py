### ngram.py
### Luke Benz
### Ling 227
### Homework 3

import numpy as np
import re
import sys
import random
from collections import defaultdict

### Declare Global Q
global Q 

### Generates phone under bigram model
def generate_phone_bi(phone):
	rand = random.uniform(0,1)
	phones = bigram[phone]
	for next_phone in phones:
		rand -= bigram[phone][next_phone]
		if rand < 0.0: 
			return next_phone
	return bigram[phone][phones[len(phones) - 1]]

### Generates phone under trigram model
def generate_phone_tri(phone1, phone2):
	rand = random.uniform(0,1)
	phones = trigram[phone1][phone2]
	for next_phone in phones:
		rand -= trigram[phone1][phone2][next_phone]
		if rand < 0.0: 
			return next_phone
	return trigram[phone1][phone2][phones[len(phones) - 1]]

### Generates word under bigram model
def generate_word_bi():
	word = "#"
	cursor = ""
	while cursor != "#":
		if cursor == "":
			cursor = "#"
		cursor = generate_phone_bi(cursor)
		word += " " + cursor
	return word

### Generates word under trigram model
def generate_word_tri():
	word = "#" 
	cursor1 = "#"
	cursor2 = ""
	word += " " + cursor1
	while cursor2 != "#":
		if cursor2 == "":
			tmp = cursor1
			cursor1 = "#"
			cursor2 = tmp
		tmp = generate_phone_tri(cursor1, cursor2)
		cursor1 = cursor2
		cursor2 = tmp
		word += " " + cursor2
	return word

### Computes Probability of a word
def probability(word):
	global Q
	word = re.split(" ", word)
	### Update Q
	Q += len(word) ### accounts for final #, which was added in before passing to this function
	prob = 0 ### log(prob(#)) 
	### Bigram probabilities
	if n == 2:
		for i in range(1,len(word)):
			try:
				prob += np.log2(bigram[word[i-1]][word[i]])
			except KeyError:
				prob += -float("inf")
	### Trigram Probabilities
	elif n == 3:
		### inital prob of phone 1, and (phone 2 | phone 1)
		try:
			prob = np.log2(bigram[word[0]][word[1]])
		except KeyError:
				prob += -float("inf")
		for i in range(2,len(word)): 
			try:
				prob += np.log2(trigram[word[i-2]][word[i-1]][word[i]])
			except KeyError:
				prob += -float("inf")
	return 2**prob


if __name__ == '__main__':
	### Error Check
	args = len(sys.argv)
	if re.sub("[0-9, \.]*", "", sys.argv[1]) == "-add":
		add_lam = True
		lam = float(re.sub("[A-z, -]", "", sys.argv[1]))
		training_file = sys.argv[2]
		n = int(sys.argv[3])
		if args == 5:
			test_file = sys.argv[4]
		args -= 1
	else:
		add_lam = False
		training_file = sys.argv[1]
		n = int(sys.argv[2])
		if args == 4:
			test_file = sys.argv[3]
		

	if len(sys.argv) != 3 and len(sys.argv) != 4 and len(sys.argv) != 5:
		sys.exit("Error: Proper Usage is python ngram.py -add1 (optional) training_file N test_file (optional)")
	if str(n) not in ['2','3']:
		sys.exit("Error: N must be 2 or 3")

	### Hold counts 
	counts = defaultdict(lambda:0)
	bicounts = defaultdict(lambda:defaultdict(lambda:0))
	tricounts = defaultdict(lambda:defaultdict(lambda:defaultdict(lambda:0)))

	### Collect Counts	
	with open(training_file) as language:
		language = language.readlines()

		### Clean training files without one words per line
		if len(language) == 1:
			language = re.sub(" # ", " #,", str(language))
			language = language.split(",") [0:-1] 
			language[0] = re.sub("^.{4}", "", language[0])
			for i in range(len(language)):
				language[i] =  "# " + language[i]

		### Loop over data and store counts
		for line in language:
			line = line.strip("\n")
			if n == 3:
				line = "# " + line
			phones = re.split(" ", line)

			for i in range(len(phones) - 1):
				counts[phones[i]] = counts[phones[i]] + 1
				bicounts[phones[i]][phones[i+1]] = bicounts[phones[i]][phones[i+1]] + 1
				if i < len(phones) - 2:
					tricounts[phones[i]][phones[i+1]][phones[i+2]]  = tricounts[phones[i]][phones[i+1]][phones[i+2]] + 1	

		### Smoothing
		if add_lam:
			all_phones = ['P', 'T', 'K', 'B', 'D', 'G', 'N', 'NG', 'V', 'TH', 'AH', 'DH', 'S', 'Z', 'SH', 'ZH', 'CH', 'JH', 'L', 'W',
			'R', 'Y', 'H', 'Q', 'DX', 'NX', 'EL', 'IY', 'IH', 'EY', 'EH', 'AE', 'AA', 'AO', 'OW', 'UW', 'UH', 'ER', 'AY','AW', 'OY', 
			'AX', 'IX', 'AXR', 'UX', 'M',"#", "#", "HH", "TH"]

			for p1 in all_phones:
				counts[p1] += lam
				for p2 in all_phones:
					bicounts[p1][p2] += lam
					for p3 in all_phones:
						tricounts[p1][p2][p3] += lam

		### MLE Frequencies
		bigram = defaultdict(lambda:{})
		trigram = defaultdict(lambda:defaultdict(lambda:{}))

		for phone1 in counts:
			for phone2 in bicounts[phone1]:
				bigram[phone1][phone2] = float(bicounts[phone1][phone2])/float(counts[phone1])
				for phone3 in tricounts[phone1][phone2]:
					trigram[phone1][phone2][phone3] = float(tricounts[phone1][phone2][phone3])/float(bicounts[phone1][phone2])

		### Generate Words
		if args == 3:
			if n == 2:
				for i in range(25):
					print generate_word_bi()
			if n == 3:
				for i in range(25):
					print generate_word_tri()

		### Probability and Perplexity
		if args == 4:
			with open(test_file) as test:
				test = test.readlines()
				perplex = 0
				global Q 
				Q = 0
				for line in test:
					line =  re.sub("\n", "", line)
					word = "# " + line.strip(" ") + " #" 
					if n == 3:
						word = "# " + word
					print word
					prob = probability(word)
					print prob

					### Compute Perplexity (We can just sum over log(probs) of words as long as we keep track of Q
					if prob > 0:
						perplex += np.log2(prob)
					else:
						perplex += -float("inf")

			perplexity = 2**(-1/float(Q)*perplex)
			print "Perplexity: ", perplexity