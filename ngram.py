import sys
import re
import random
import numpy as np

from collections import defaultdict
from scipy import linalg
from good_turing import good_turing_counts
from tweet_parse import tweet_parse, clean_tweet

# boolean variable for good-turing smoothing:
good_turing = 'false'
tweet = 'false'


# set up dictionaries
counts = defaultdict(lambda:0)
bi_counts = defaultdict(lambda:defaultdict(lambda:0))
bi_tri_counts = defaultdict(lambda:defaultdict(lambda:0))
tri_counts = defaultdict(lambda:defaultdict(lambda:defaultdict(lambda:0)))

#set up dictionaries for new counts
new_counts = defaultdict(lambda:0) 
new_bicounts = defaultdict(lambda:defaultdict(lambda:0))
new_bitricounts = defaultdict(lambda:defaultdict(lambda:0))
new_tricounts = defaultdict(lambda:defaultdict(lambda:defaultdict(lambda:0)))

bigram = defaultdict(lambda:{})
trigram = defaultdict(lambda:defaultdict(lambda:{}))

# open language file and increment counts 
def train_data():


	if ngram == 2:
		if tweet:
			tweets = tweet_parse(training_file)
			for item in tweets:
				if len(item) > 1:
					print item
					item = clean_tweet(item)
					for i in range(len(item)-1):
						counts[item[i]] += 1
						bi_counts[item[i]][item[i+1]] += 1
					counts[item[len(item)-1]] += 1



		# implement good turning 
		if good_turing:
			
			# sort counts 
			sorted_counts = sorted(counts.items(), key=lambda x:x[1])

			# sort bicounts
			sorted_bicounts = []
			for i in bi_counts:
				for j in bi_counts[i]:
					sorted_bicounts.append((i+j,bi_counts[i][j]))

			print sorted_counts
			print sorted_bicounts
			
			sorted_bicounts.sort(key=lambda x: x[1])

			new_counts = good_turing_counts(sorted_counts, 1022000)

			new_bicounts = good_turing_counts(sorted_bicounts, 1022000 * 1022000)


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

				new_bitricounts = good_turing_counts(sorted_bicounts, 1022000 * 1022000)
				new_tricounts = good_turing_counts(sorted_tricounts, 1022000 * 1022000 * 1022000)


		build_grams()

def build_grams():
	# compute relative frequency estimates for word pairs and triples
	if ngram == '2':
		for phone1 in counts:
			for phone2 in bi_counts[phone1]:

				count = 0
				bi_count = 0

				if good_turing:	

					# get updated new count 
					count = float(new_counts[float(counts[phone1])])
					bi_count = float(new_bicounts[float(bi_counts[phone1][phone2])])

				else:
					count = float(counts[phone1])
					bi_count = float(bi_counts[phone1][phone2])


				bigram[phone1][phone2] = bi_count/count
				#print "P(" + phone2 + " | " + phone1 + ")\tis\t" + str(bigram[phone1][phone2])
	else:
		for phone1 in tri_counts:
			for phone2 in tri_counts[phone1]:
				for phone3 in tri_counts[phone1][phone2]:

					bi_count = 0
					tri_count = 0

					if good_turing:

						# get updated new count
						bi_count = float(new_bitricounts[float(bi_tri_counts[phone1][phone2])])
						tri_count = float(new_tricounts[float(tri_counts[phone1][phone2][phone3])])

					else:

						bi_count = float(bi_tri_counts[phone1][phone2])
						tri_count = float(tri_counts[phone1][phone2][phone3])

					trigram[phone1][phone2][phone3] = tri_count/bi_count
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

	sys.argv.remove('-good_turing')
	good_turing = 'true'

	if '-tweet' in sys.argv:
		tweet = 'true'
		sys.argv.remove('-tweet')

training_file = sys.argv[1]
ngram = int(sys.argv[2])

train_data()

if len(sys.argv) == 5:
	test_file = sys.argv[4]
	generate_probabilities()

	#else: 
		#generate_words()