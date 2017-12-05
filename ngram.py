import sys
import re
import random
import numpy as np
from collections import defaultdict

# boolean variable for add-1 smoothing:
add = 'false'
add_var = 1


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

			if add == 'true':
				# get list of unique phones for smoothing
				unique_phones = list(set(bi_phones))
				for i in range(len(unique_phones)):
					for j in range(len(unique_phones)):
						counts[unique_phones[i]] += add_var
						counts[unique_phones[j]] += add_var
						bi_counts[unique_phones[i]][unique_phones[j]] += add_var

			for i in range(len(bi_phones)-1):
				counts[bi_phones[i]] += 1
				bi_counts[bi_phones[i]][bi_phones[i+1]] += 1

		else:
			# add '#' to the beginning and end of text
			tri_text = '#'+text +'#'
			# get a list of phones
			tri_phones = re.findall(r'[A-Z]+|#', tri_text)

			if add == 'true':
				# get list of unique phones for smoothing
				unique_phones = list(set(tri_phones))
				for i in range(len(unique_phones)):
					for j in range(len(unique_phones)):
						for k in range(len(unique_phones)):
							bi_tri_counts[unique_phones[i]][unique_phones[j]] += add_var
							bi_tri_counts[unique_phones[j]][unique_phones[k]] += add_var
							tri_counts[unique_phones[i]][unique_phones[j]][unique_phones[k]] += add_var

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
		sigma_log = 0
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
						sigma_log += np.log2([bigram[bi_phones[i]][bi_phones[i+1]]])[0]
						probability += np.log2([bigram[bi_phones[i]][bi_phones[i+1]]])[0]
					else:
						sigma_log += np.log2([0])[0]
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
						sigma_log += np.log2([trigram[tri_phones[i]][tri_phones[i+1]][tri_phones[i+2]]])[0]
						probability += np.log2([trigram[tri_phones[i]][tri_phones[i+1]][tri_phones[i+2]]])[0]
					else:
						sigma_log += np.log2([0])[0]
						probability += np.log2([0])[0]

				# calculate and print probabilties
				print "p(" + tri_line +") = "+ str(2**probability)
		print "PP(corpus) = " + str(2**(-1/float(Q)* sigma_log))

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

# when -add1 flag is used
if '-add1' in sys.argv:
	add = 'true'
	training_file = sys.argv[2]
	ngram = sys.argv[3]

	train_data()

	if len(sys.argv) == 5:
		test_file = sys.argv[4]
		generate_probabilities()

	else: 
		generate_words()

# when -add_lambda flag is used
elif '-add_lambda' in sys.argv:
	add = 'true'
	add_var = float(sys.argv[2])
	training_file = sys.argv[3]
	ngram = sys.argv[4]

	train_data()

	if len(sys.argv) == 6:
		test_file = sys.argv[5]
		generate_probabilities()

	else: 
		generate_words()

# when no flag is used
else:
	training_file = sys.argv[1]
	ngram = sys.argv[2]

	train_data()

	if len(sys.argv) == 4:
		test_file = sys.argv[3]
		generate_probabilities()

	else:
		generate_words()






