import numpy as np
from collections import defaultdict

# returns a dictionary mapping counts to new counts which have been smoothed using simple good turing
def good_turing_counts(sorted_counts, unseen):
	# get counts of counts with zero for unseen counts
	count_of_counts = defaultdict(lambda:0)

	# get count of counts with just seen counts
	seen_counts = defaultdict(lambda:0)

	# number of unseen events = number of words in grammar. There are approximately 1,022,000 words in the english language according to: http://www.telegraph.co.uk/technology/internet/8207621/English-language-has-doubled-in-size-in-the-last-century.html
	n_0 = unseen - len(sorted_counts)

	# set the number of unseen counts and bigrams
	count_of_counts[0] = n_0

	# get count_of_counts and seen_counts 
	for i in range(1, int(sorted_counts[len(sorted_counts)-1][1])+2):

		count_of_counts[i] = 0

		for count in sorted_counts: 
			if count[1] == i:
				seen_counts[i] += 1
				count_of_counts[i] += 1

	# build a log function: f(x) = a + blog(x) that maps seen counts to number of seen counts
	x = np.array(seen_counts.keys())
	y = np.array(seen_counts.values())

	cons = np.polyfit(np.log(x), y, 1)

	b = cons[0]
	a = cons[1]

	# map unseen counts in counts_of_counts using log function
	for k, v in count_of_counts.iteritems():
		if v == 0:
			# computing using function of a, b
			f = a + (b * np.log([k])[0])

			# prevent -inf 
			if f < 0:
				f = 1

			count_of_counts[k] = f

	# implement good-turing
	# use equation c*_k-1 = (k * N_k)/ N_k-1 where c* new count nd N_k is the number of counts equal to k

	# new counts maps counts to updated good turing counts 
	new_counts = defaultdict(lambda:0)
	
	for k in range (0, len(count_of_counts.keys())):
		new_counts[k] = ((k+1)*count_of_counts[k+1])/(count_of_counts[k])

	for i in range(0, 50):
		print new_counts[i]

	return new_counts