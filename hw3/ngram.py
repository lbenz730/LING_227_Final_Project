import re
import sys
import random
import math
from datetime import datetime
from collections import defaultdict
from itertools import chain
import numpy as np

# Kevin Truong kt525
# 10/29/2017
# kevin.truong@yale.edu

addk = 0 
num = 0
lamb = 0
perplexity = 0 
#get unique words
def unique_words(lines):
        return set(chain(*(line.split() for line in lines if line)))
def generate_trisentence():
    sentence = ""
    current = ''
    second = ''
    while current is not '#' and second is not '#':
        if current == '': current = '#'
        if second == '': second = generate_biword(current)
        #print current,second
        temp = generate_triword(current,second)
        sentence += current + " "
        current = second
        second = temp
    return sentence + '#' 
def generate_bisentence():
    sentence = "#"
    current = ''
    while current is not '#':
        if current == '': current = '#'
        current = generate_biword(current)
        sentence += " " + current
    return sentence
#given a word, randomly generates and returns the next word using the trigram model
def generate_triword(word, word2):
    # generate a random float between 0 and 1
    # we will use this float to probabilistically select a 'bin'
    # corresponding to a word in our bigram model
    #random.seed(datetime.now())
    if addk:
        rand = random.uniform(0,0.0001)
    else:
        rand = random.uniform(0,1)
    # go through each possible second word
    temp = 1
    for following in trigram[word][word2]:
        # subtract this word's probability from rand 
        rand -= trigram[word][word2][following]
	#print following 
        # as soon as we 'cross over' zero we have found the word for that bin
        if rand < 0.0: return following
        temp = following
    return trigram[word][word2].keys()[-1]

#given a word, randomly generates and returns the next word using the bigram model
def generate_biword(word):
    # generate a random float between 0 and 1
    # we will use this float to probabilistically select a 'bin'
    # corresponding to a word in our bigram model
    rand = random.uniform(0,1)
    # go through each possible second word
    for following in bigram[word]:
        # subtract this word's probability from rand 
        rand -= bigram[word][following]
        # as soon as we 'cross over' zero we have found the word for that bin
        if rand < 0.0: return following
    return bigram[word].keys()[-1]

trigram = defaultdict(lambda:defaultdict(lambda:{}))
def tri():
    counts = defaultdict(lambda:0)
    tricounts = defaultdict(lambda:defaultdict(lambda:defaultdict(lambda:0)))
    # this loops through all the data and stores counts
    global addk
    global num
    global lamb
    global perplexity
    N = 1
    if(addk):
        N = 2 
    else:
        N = 1
    with open(sys.argv[N]) as language:
	for line in language:
	    # we have to have a way to begin and end each line
	   line = line.strip()
	   words = re.split(r'[,.?"!\s:;]+|--', line)

	   # we go through each position and keep track of word and word pair counts
           for i in range(len(words)-2):
               counts[words[i]] += 1
	       tricounts[words[i]][words[i+1]][words[i+2]] += 1

    V = 0 
    #addk smoothing part
    if addk: 
        with open(sys.argv[N]) as language:
            uni = unique_words(language)
        
        uni = list(uni)
        uni_temp = uni[:]
        #look for trigrams that do not occur and add count to lambda
        for l in tricounts.keys():
            for m in tricounts[l].keys():
                uni.remove(m)
                uni_2 = uni_temp[:]
                for t in tricounts[l][m].keys():
                    V += lamb
                    uni_2.remove(t) 
                for unseen in uni_2:
                    V += lamb
                    tricounts[l][m][unseen] = lamb
            for unseen in uni:
                for uniq in uni_temp:
                    V += lamb
                    tricounts[l][unseen][uniq] = lamb

            uni = uni_temp[:]
# this loops through all word pairs and computes relative frequency estimates
    for word1 in counts:
	for word2 in tricounts[word1]:
	    for word3 in tricounts[word1][word2]:
		trigram[word1][word2][word3] = float(tricounts[word1][word2][word3])/float(counts[word1]+V)
		#print "P(" + word3 + " | " + word2 + " | " + word1 + ")\tis\t" + str(trigram[word1][word2][word3])
    #for test files
    if(len(sys.argv) >= 4): 
        q = 0
        logsum = 0
        N = 4
        if addk: 
            N = 4
        else: 
            N = 3 
        try: 
            with open(sys.argv[N]) as test:
                for line in test:
                    #prepare the test file
                    line = "# " + line.strip() + " #"
                    prob = 0
                    prob0 = 0
                    #split into each phone
                    phones = re.split(r'\s',line)
                    #loop for trigrams
                    for i in range(len(phones)-3):
                        #if trigram found add probability of that trigram
                        if(phones[i] in trigram.keys() and phones[i+1] in trigram[phones[i]].keys() and phones[i+2] in trigram[phones[i]][phones[i+1]].keys()):
                            prob += np.log2([trigram[phones[i]][phones[i+1]][phones[i+2]]])[0]
                        #trigram not found 
                        else:
                            prob0 = 1
                            prob -= float("inf")
                    #print probability for each word
                    if sys.argv[num] == '3':
                        if prob0:
                            print "P( " + " ".join(i for i in phones) + " ) = " +  str(0)
                        else:
                            print "P( " + " ".join(i for i in phones) + " ) = " +  str(math.pow(2,prob))
                    q += 1
                    logsum+= prob
            #print preplexity for trigrams
            if sys.argv[num] == '3':
                print ("Perplexity = "  + str(math.pow(2,logsum/q*-1)))
        except(IndexError):
            pass


bigram = defaultdict(lambda:{})
def bi():
    global addk
    global num
    global lamb
    global perplexity
    counts = defaultdict(lambda:0)
    bicounts = defaultdict(lambda:defaultdict(lambda:0))
    q = 0
    logsum = 0
    # this loops through all the data and stores counts
    N = 1

    if(addk == 1):
        N = 2
    else:
        N = 1 
    with open(sys.argv[N]) as language:
	for line in language:
	   # we have to have a way to begin and end each line
           #print line
           line = line.strip() 
           #line = line.strip() 
           words = re.split(r'[,.?"!\s:;]+|--', line)

           # we go through each position and keep track of word and word pair counts
           for i in range(len(words)-1):
               counts[words[i]] = counts[words[i]] + 1
               bicounts[words[i]][words[i+1]] = bicounts[words[i]][words[i+1]] + 1
    V = 0 
    #if add lambda
    if addk: 
        #open the training file and get all the unique words 
        with open(sys.argv[N]) as language:
            uni = unique_words(language)
        uni = list(uni)
        uni_temp = uni[:]
        for l in bicounts.keys():
            #remove the phones that have been seen
            for k in bicounts[l].keys():
                uni.remove(k)
                V += lamb 
            #if the phone has not been seen, make the count equal to lamb
            for unseen in uni:
                bicounts[l][unseen] = lamb
                V += lamb
            #loop for the entire training file 
            uni = uni_temp[:]
    # this loops through all word pairs and computes relative frequency estimates
    for word1 in counts:
        for word2 in bicounts[word1]:
            bigram[word1][word2] = float(bicounts[word1][word2])/float(counts[word1] + V)
            if(len(sys.argv) == 4):
                q = q + 1 
                logsum = logsum + math.log(bigram[word1][word2],2)
            #print "P(" + word2 + " | " + word1 + ")\tis\t" + str(bigram[word1][word2])
        
    #for testfiles
    if(len(sys.argv) >= 4):
        N = 4
        if addk:
            N = 4
        else: 
            N = 3 

        logsum = 0
        q = 0
        try:
            with open(sys.argv[N]) as test:
                
                for line in test:
                    #prep each line 
                    line = "# " + line.strip() + " #"
                    prob = 0
                    #split into each phone
                    phones = re.split(r'\s',line)
                    #only need to look at the first n-2 terms 
                    q += len(phones)
                    q -= 2
                    prob0 = 0
                    for i in range(len(phones)-2):
                        #if exists add the porbability
                        if(phones[i] in bigram.keys() and phones[i+1] in bigram[phones[i]].keys()):
                            prob += np.log2([bigram[phones[i]][phones[i+1]]])[0]
                        #else something bad and the perplexity is automatically inf
                        else:
                            prob0 = 1
                            prob -= float("inf")

                    if sys.argv[num] == '2':
                        # a bigram did not exist so the probability is 0
                        if prob0:
                            print "P( " + " ".join(i for i in phones) + " ) = " +  str(0)
                        else:
                            print "P( " + " ".join(i for i in phones) + " ) = " +  str(math.pow(2,prob))
                    q += 1
                    logsum+= prob
            #print perplexity for bigrams 
            if sys.argv[num] == '2':
                print ("Perplexity = "  + str(math.pow(2,logsum/q*-1)))
                perplexity = math.pow(2,logsum/q*-1)
                #print perplexity
        except(IndexError):
            pass

def main():
    if(len(sys.argv) <3 or len(sys.argv) > 5):
	print  "Usage: python ngram.py (-addk) training_file N testfile"
    else:
        global addk
        global num
        global lamb
        num = 2
        #look for the add lambda
        add = re.match(r'-add', sys.argv[1])
        if(add):
            num = 3
            addk = 1
            #check to see if the lambda is valid
            try: 
                lamb = float(sys.argv[1][4:])
            except(ValueError):
                lamb = 0 
        else: 
            num = 2 
        #check to see if bi or tri gram
        if sys.argv[num] != '2' and sys.argv[num] != '3':
	    print "N must be between 2 and 3"
        else:
            bi()
            #print 25 times
            if sys.argv[num] == '2':
                '''
                for i in range(0,10000,1):
                    lamb = i/float(10000)    
                    bi()
                '''
                for i in xrange(25):
                    print generate_bisentence()
            else:    
                #print 25 times
                tri()
                for i in xrange(25):
                    print generate_trisentence()

if __name__ == "__main__":
    main()

