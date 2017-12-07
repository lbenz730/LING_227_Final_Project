import sys
import re
import random
import numpy as np

from collections import defaultdict
from scipy import linalg

# boolean variable for good-turing smoothing:
good_turing = 'false'


# set up dictionaries
counts = defaultdict(lambda:0)
bi_counts = defaultdict(lambda:defaultdict(lambda:0))
bi_tri_counts = defaultdict(lambda:defaultdict(lambda:0))
tri_counts = defaultdict(lambda:defaultdict(lambda:defaultdict(lambda:0)))

bigram = defaultdict(lambda:{})
trigram = defaultdict(lambda:defaultdict(lambda:{}))

# open language file and increment counts 
def train_data():
	with open(training_file) as language_file:
		language = language_file.read()
		
		# find all words in language
		phones = re.findall(r'#[A-Z\s\n]+#', language) 
		
		# recombine words into string
		text = ''
		for phone in phones:
			text += ''.join(phone)

		# replace '##' with '#' for bigram text 
		bi_text = text.replace('##', '#')
		# get list of phones and char for bi_phones and tri_phones
		bi_phones = re.findall(r'[A-Z]+|#', bi_text)

		if ngram == '2':
			# replace '##' with '#' for bigram text 
			bi_text = text.replace('##', '#')
			# get list of phones
			bi_phones = re.findall(r'[A-Z]+|#', bi_text)

			for i in range(len(bi_phones)-1):
				counts[bi_phones[i]] += 1
				bi_counts[bi_phones[i]][bi_phones[i+1]] += 1

			# implement good turning 
			if good_turing:
				
				# sort counts 
				sorted_counts = sorted(counts.items(), key=lambda x:x[1])

				# sort bicounts
				sorted_bicounts = []
				for i in bi_counts:
					for j in bi_counts[i]:
						sorted_bicounts.append((i+j,bi_counts[i][j]))
				
				sorted_bicounts.sort(key=lambda x: x[1])

				# get counts of counts with zero for unseen counts
				count_of_counts = defaultdict(lambda:0)
				count_of_bicounts = defaultdict(lambda:0)

				# get count of counts with just seen counts
				seen_counts = defaultdict(lambda:0)
				seen_bicounts = defaultdict(lambda:0)

				# number of unseen events = number of words in grammar. There are approximately 1,022,000 words in the english language according to: http://www.telegraph.co.uk/technology/internet/8207621/English-language-has-doubled-in-size-in-the-last-century.html
				n_0 = 1022000 - len(sorted_counts)

				# number of unseen bigrams = (number of english words)^2 - number of seen bigrams
				b_0 = 1022000 * 1022000 - len(sorted_bicounts)

				# set the number of unseen counts and bigrams
				count_of_counts[0] = n_0
				count_of_bicounts[0] = b_0

				# get count_of_counts and seen_counts 
				for i in range(1, int(sorted_counts[len(sorted_counts)-1][1])+1):

					count_of_counts[i] = 0

					for count in sorted_counts: 
						if count[1] == i:
							seen_counts[i] += 1
							count_of_counts[i] += 1

				# get count_of_bicounts and seen_bicounts 
				for i in range(1, int(sorted_bicounts[len(sorted_bicounts)-1][1])+1):

					count_of_bicounts[i] = 0

					for count in sorted_bicounts: 
						if count[1] == i:
							seen_bicounts[i] += 1
							count_of_bicounts[i] += 1

				# build a log function: f(x) = a + blog(x) that maps seen counts to number of seen counts
				x = np.array(seen_counts.keys())
				y = np.array(seen_counts.values())

				cons = np.polyfit(np.log(x), y, 1)

				b = cons[0]
				a = cons[1]

				# build a log function: f(x) = a + blog(x) that maps seen bis to number of seen bis
				w = np.array(seen_bicounts.keys())
				z = np.array(seen_bicounts.values())

				cons = np.polyfit(np.log(w), z, 1)

				c = cons[0]
				d = cons[1]

				# map unseen counts in counts_of_counts using log function
				for k, v in count_of_counts.iteritems():
					if v == 0:
						# computing using function of a, b
						y = a + (b * np.log([k])[0])

						# prevent -inf 
						if y < 0:
							y = 0

						count_of_counts[k] = y

				# map unseen bis in counts_of_bis using log function
				for k, v in count_of_bicounts.iteritems():
					if v == 0:
						# computing using function of a, b
						y = c + (d * np.log([k])[0])

						# prevent -inf 
						if y < 0:
							y = 0

						count_of_bicounts[k] = y


				# implement good-turing
				# use equation c*_k-1 = (k * N_k)/ N_k-1 where c* new count nd N_k is the number of counts equal to k

				# new counts maps counts to updated good turing counts 
				new_counts = defaultdict(lambda:0)

				for k in range (1, len(count_of_counts.keys())):
					new_counts[k] = ((k+1)*count_of_counts[k+1])/(count_of_counts[k])

				# new counts maps bigram counts to updated good turing bigram counts
				new_bis = defaultdict(lambda:0)

				for k in range (1, len(count_of_bicounts.keys())):
					new_bis[k] = ((k+1)*count_of_bicounts[k+1])/(count_of_bicounts[k])


		else:
			# add '#' to the beginning and end of text
			tri_text = '#'+text +'#'
			# get a list of phones
			tri_phones = re.findall(r'[A-Z]+|#', tri_text)

			for i in range(len(tri_phones)-2):
				bi_tri_counts[tri_phones[i]][tri_phones[i+1]] = bi_tri_counts[tri_phones[i]][tri_phones[i+1]] + 1
				tri_counts[tri_phones[i]][tri_phones[i+1]][tri_phones[i+2]] = tri_counts[tri_phones[i]][tri_phones[i+1]][tri_phones[i+2]] + 1
			
			# implement good turning 
			if good_turing:
				
				# sort tricounts 
				sorted_tricounts = []

				for i in tri_counts:
					for j in tri_counts[i]:
						for k in tri_counts[i][j]:
							sorted_tricounts.append((i+j+k, tri_counts[i][j][k]))

				sorted_tricounts.sort(key=lambda x: x[1])

				# sort bicounts
				sorted_bicounts = []
				for i in bi_tri_counts:
					for j in bi_tri_counts[i]:
						sorted_bicounts.append((i+j,bi_tri_counts[i][j]))
				
				sorted_bicounts.sort(key=lambda x: x[1])

				# get tricounts of tricounts with zero for unseen tricounts
				count_on_tricounts = defaultdict(lambda:0)
				count_of_bicounts = defaultdict(lambda:0)

				# get count of tricounts with just seen tricounts
				seen_tricounts = defaultdict(lambda:0)
				seen_bicounts = defaultdict(lambda:0)

				# number of unseen events = number of words in grammar. There are approximately 1,022,000 words in the english language according to: http://www.telegraph.co.uk/technology/internet/8207621/English-language-has-doubled-in-size-in-the-last-century.html
				n_0 = 1022000 - len(sorted_tricounts)

				# number of unseen bigrams = (number of english words)^2 - number of seen bigrams
				b_0 = 1022000 * 1022000 - len(sorted_bicounts)

				# set the number of unseen tricounts and bigrams
				count_on_tricounts[0] = n_0
				count_of_bicounts[0] = b_0

				# get count_on_tricounts and seen_tricounts 
				for i in range(1, int(sorted_tricounts[len(sorted_tricounts)-1][1])+1):

					count_on_tricounts[i] = 0

					for count in sorted_tricounts: 
						if count[1] == i:
							seen_tricounts[i] += 1
							count_on_tricounts[i] += 1

				# get count_of_bicounts and seen_bicounts 
				for i in range(1, int(sorted_bicounts[len(sorted_bicounts)-1][1])+1):

					count_of_bicounts[i] = 0

					for count in sorted_bicounts: 
						if count[1] == i:
							seen_bicounts[i] += 1
							count_of_bicounts[i] += 1

				# build a log function: f(x) = a + blog(x) that maps seen tricounts to number of seen tricounts
				x = np.array(seen_tricounts.keys())
				y = np.array(seen_tricounts.values())
				
				cons = np.polyfit(np.log(x), y, 1)

				b = cons[0]
				a = cons[1]

				# build a log function: f(x) = a + blog(x) that maps seen bis to number of seen bis
				w = np.array(seen_bicounts.keys())
				z = np.array(seen_bicounts.values())

				cons = np.polyfit(np.log(w), z, 1)

				c = cons[0]
				d = cons[1]

				# map unseen tricounts in tricounts_on_tricounts using log function
				for k, v in count_of_tricounts.iteritems():
					if v == 0:
						# computing using function of a, b
						y = a + (b * np.log([k])[0])

						# prevent -inf 
						if y < 0:
							y = 0

						count_of_tricounts[k] = y

				# map unseen bis in tricounts_of_bis using log function
				for k, v in count_of_bicounts.iteritems():
					if v == 0:
						# computing using function of a, b
						y = c + (d * np.log([k])[0])

						# prevent -inf 
						if y < 0:
							y = 0

						count_of_bicounts[k] = y


				# implement good-turing
				# use equation c*_k-1 = (k * N_k)/ N_k-1 where c* new count nd N_k is the number of tricounts equal to k

				# new tricounts maps tricounts to updated good turing tricounts 
				new_tricounts = defaultdict(lambda:0)

				for k in range (1, len(count_of_tricounts.keys())):
					new_tricounts[k] = ((k+1)*count_of_tricounts[k+1])/(count_of_tricounts[k])

				# new tricounts maps bigram tricounts to updated good turing bigram tricounts
				new_bis = defaultdict(lambda:0)

				for k in range (1, len(count_of_bicounts.keys())):
					new_bis[k] = ((k+1)*count_of_bicounts[k+1])/(count_of_bicounts[k])


			for i in range(len(tri_phones)-2):
				bi_tri_counts[tri_phones[i]][tri_phones[i+1]] = bi_tri_counts[tri_phones[i]][tri_phones[i+1]] + 1
				tri_counts[tri_phones[i]][tri_phones[i+1]][tri_phones[i+2]] = tri_counts[tri_phones[i]][tri_phones[i+1]][tri_phones[i+2]] + 1
		build_grams()

def build_grams():
	# compute relative frequency estimates for word pairs and triples
	if ngram == '2':
		for phone1 in counts:
			for phone2 in bi_counts[phone1]:
				bigram[phone1][phone2] = float(bi_counts[phone1][phone2])/float(counts[phone1])
				#print "P(" + phone2 + " | " + phone1 + ")\tis\t" + str(bigram[phone1][phone2])
	else:
		for phone1 in tri_counts:
			for phone2 in tri_counts[phone1]:
				for phone3 in tri_counts[phone1][phone2]:
					trigram[phone1][phone2][phone3] = float(tri_counts[phone1][phone2][phone3])/float(bi_tri_counts[phone1][phone2])
					#print "P(" + phone3 + " | " + phone1 +','+ phone2 + ")\tis\t" + str(trigram[phone1][phone2][phone3])

# bin method to generate random phones
def bi_generate_phone(phone):
	rand = random.uniform(0,1)
	# go through each possible second phone
	for next_phone in bigram[phone]:
		# subtract the  probability of the phone from rand 
		rand -= bigram[phone][next_phone]
		# phone for bin is found when zero is crossed
		if rand < 0.0: return next_phone
	return next_phone


def tri_generate_phone(phone1, phone2):
	rand = random.uniform(0,1)
	# go through each possible 3 second phone
	for next_phone in trigram[phone1][phone2]:
		# subtract the  probability of the phone from rand 
		rand -= trigram[phone1][phone2][next_phone]
		# phone for bin is found when zero is crossed
		if rand < 0.0: return next_phone
	return next_phone


# keeps generating words until '#'' is randomly generated, then returns the whole word
def bi_generate_word():
	word = "#"
	current = ''
	while current is not '#':
		if current == '': current = '#'
		current = bi_generate_phone(current)
		word += " " + current
	return word

# keeps generating words until '# #' is randomly generated, then returns the whole word
def tri_generate_word():
	word = "#"
	first = ''
	second = ''
	while second is not '#':
		if first == '': 
			first = '#'
			second = '#'
		word += " " + second
		buff = second
		second = tri_generate_phone(first, second)
		first = buff
	word += " " + '# #'
	return word

# generate probabilities for test file words
def generate_probabilities():
	with open(test_file) as test:
		Q = 0
		for line in test:
			Q += 1
			if ngram == '2':
				bi_line = "# " + line.strip() + " #"
				bi_phones = re.split(r'\s', bi_line)

				probability = 0

				# for each phone, update sigma_log and probability
				for i in range(len(bi_phones)-1):
					if bi_phones[i] in bigram and bi_phones[i+1] in bigram[bi_phones[i]]:
						probability += np.log2([bigram[bi_phones[i]][bi_phones[i+1]]])[0]
					else:
						probability += np.log2([0])[0]

				# calculate and print probabilties
				print "p(" + bi_line +") = "+ str(2**probability)

			else:
				tri_line = "# # " + line.strip() + " # #"
				tri_phones = re.split(r'\s', tri_line)

				probability = 0

				# for each phone, update sigma_log and probability
				for i in range(len(tri_phones)-2):
					if tri_phones[i] in trigram and tri_phones[i+1] in trigram[tri_phones[i]] and tri_phones[i+2] in trigram[tri_phones[i]][tri_phones[i+1]]:
						probability += np.log2([trigram[tri_phones[i]][tri_phones[i+1]][tri_phones[i+2]]])[0]
					else:
						probability += np.log2([0])[0]

				# calculate and print probabilties
				print "p(" + tri_line +") = "+ str(2**probability)

def generate_words():
	if ngram == '2':
		# print 25 random 'words' using the bigram
		for i in range(25):
			print bi_generate_word()
	elif ngram == '3':
		# print 25 random 'words' using the trigram
		for i in range(25):
			print tri_generate_word()
	else:
		"Error: N-gram not supported"


# Read command line arguments

if '-good_turing' in sys.argv:
	good_turing = 'true'
	training_file = sys.argv[2]
	ngram = sys.argv[3]

	train_data()

	if len(sys.argv) == 5:
		test_file = sys.argv[4]
		generate_probabilities()

	#else: 
		#generate_words()

# when no flag is used
else:
	training_file = sys.argv[1]
	ngram = sys.argv[2]

	train_data()

	if len(sys.argv) == 4:
		test_file = sys.argv[3]
		generate_probabilities()

	#else:
		#generate_words()






