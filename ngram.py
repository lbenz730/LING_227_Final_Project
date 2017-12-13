import sys
import re
import random
import numpy as np

from collections import defaultdict
from scipy import linalg
from good_turing import good_turing_counts
from tweet_parse import tweet_parse, clean_tweet
from tok import *
# boolean variable for good-turing smoothing:
good_turing = False
tweet = False
speech = False

global counts
global bi_counts
global bi_tri_counts 
global tri_counts 

#set up dictionaries for new counts
global new_counts
global new_bicounts
global new_bitricounts
global new_tricounts


# set up dictionaries
counts = defaultdict(lambda:0)
bi_counts = defaultdict(lambda:defaultdict(lambda:0))
bi_tri_counts = defaultdict(lambda:defaultdict(lambda:0))
tri_counts = defaultdict(lambda:defaultdict(lambda:defaultdict(lambda:0)))

#set up dictionaries for new counts
new_counts = defaultdict(lambda:0) 
new_bicounts = defaultdict(lambda:0)
new_bitricounts = defaultdict(lambda:0)
new_tricounts = defaultdict(lambda:0)

bigram = defaultdict(lambda:{})
trigram = defaultdict(lambda:defaultdict(lambda:{}))

# open language file and increment counts 
def train_data():

	global new_counts
	global new_bicounts
	global new_bitricounts
	global new_tricounts

	if ngram == 2:
		if tweet:
			tweets = tweet_parse(training_file)
			for item in tweets:
				if len(item) > 1:
					try:
						item = clean_tweet(item)
					except IndexError:
						item = "FAIL"
					if item != "FAIL":
						for i in range(len(item)-1):
							counts[item[i]] += 1
							bi_counts[item[i]][item[i+1]] += 1
						counts[item[len(item)-1]] += 1

	        if speech:
			speeches = parse(training_file)
			for item in speeches:
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
			
			sorted_bicounts.sort(key=lambda x: x[1])

			new_counts = good_turing_counts(sorted_counts, 102200)

			new_bicounts = good_turing_counts(sorted_bicounts, 102200)


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

	global new_counts
	global new_bicounts
	global new_bitricounts
	global new_tricounts

	# compute relative frequency estimates for word pairs and triples
	if ngram == 2:
		for phone1 in counts:
			for phone2 in bi_counts[phone1]:

				if good_turing:

					# get updated new count 
					count = float(new_counts[(counts[phone1])])
					bi_count = float(new_bicounts[bi_counts[phone1][phone2]])



				else:
					count = float(counts[phone1])
					bi_count = float(bi_counts[phone1][phone2])


				bigram[phone1][phone2] = bi_count/count


# generate probabilities for test file words
def generate_probabilities():

	global new_counts
	global new_bicounts
	global new_bitricounts
	global bigram

	with open(test_file) as test:
		Q = 0
		probs = []
		for line in test:
			Q += 1
			if ngram == 2:
				bi_line =  line.strip() 
				bi_phones = re.split(r'\s', bi_line)

				probability = 0

				# for each phone, update sigma_log and probability
				for i in range(len(bi_phones)-1):

					if bi_phones[i] in bigram and bi_phones[i+1] in bigram[bi_phones[i]]:
						probability += np.log2([bigram[bi_phones[i]][bi_phones[i+1]]])[0]
					else:
						probability += np.log2([new_bicounts[0]])[0]

				# calculate and print probabilties
				print "p(" + bi_line +") = "+ str(2**probability)
				probs.extend([str(2**probability)])
		print ",".join(probs)



# Read command line arguments
if '-good_turing' in sys.argv:

	sys.argv.remove('-good_turing')
	good_turing = True

	if '-tweet' in sys.argv:
		tweet = True
		sys.argv.remove('-tweet')

        if '-speech' in sys.argv:
        	speech = True
		sys.argv.remove('-speech')

training_file = sys.argv[1]
ngram = int(sys.argv[2])

train_data()


if len(sys.argv) == 4:
	test_file = sys.argv[3]
	generate_probabilities()
