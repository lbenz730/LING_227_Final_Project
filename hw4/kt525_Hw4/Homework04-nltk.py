import nltk

#import brown corpus
from nltk.corpus import brown

# module for training a Hidden Markov Model and tagging sequences
from nltk.tag.hmm import HiddenMarkovModelTagger

# module for computing a Conditional Frequency Distribution
from nltk.probability import ConditionalFreqDist

# module for computing a Conditional Probability Distribution
from nltk.probability import ConditionalProbDist

# module for computing a probability distribution with the Maximum Likelihood Estimate
from nltk.probability import MLEProbDist

import operator
import random

# Kevin Truong
# kt525
# 11/15/2017
# Pset 4 Homework04-nltk.py

# Usage python Homework04-nltk.py


############# INTRO POS #################

def intro():
  # NLTK provides corpora tagged with part-of-speech (POS) information and some tools to access this information
  # The Penn Treebank tagset is commonly used for English
  nltk.help.upenn_tagset()

  # We can retrieve the tagged sentences in the Brown corpus by calling the tagged_sents() function
  tagged_sentences = brown.tagged_sents(categories= 'news')
  print "Sentence tagged with Penn Treebank POS labels:"
  print tagged_sentences[42]

   # We can access the Universal tags by changing the tagset argument
  tagged_sentences_universal = brown.tagged_sents(categories= 'news', tagset='universal')
  print "Sentence tagged with Universal POS:"
  print tagged_sentences_universal[42]

# Comment to hide intro
#intro()


############# Problem 1 #################
# Insert solution for problem 1 here
# Input: genre (string), tagset (string)
# Output: number_of_tags (int), top_tags (list of string)


# get the number of tags found in the corpus
# compute the Frequency Distribution of tags

def prob1(genre,tagset):
  
  # get the tagged words from the corpus
  tagged_words = brown.tagged_words(categories= genre, tagset=tagset)
  
  # build a list of the tags associated with each word
  tags = [i[1] for i in tagged_words]
  # using the above list compute the Frequency Distribution of tags in the corpus
  # hint: use nltk.FreqDist()
  tagsFDist = nltk.FreqDist(tags)
  
  # retrieve the total number of tags in the tagset
  number_of_tags = len(set(tags)) 
  
  # retrieve the top 10 most frequent tags
  top_tags = tagsFDist.most_common(10)
  return (number_of_tags,top_tags)



def test_prob1():
  print "Tag FreqDist for news:"
  print prob1('news',None)

  print "Tag FreqDist for science_fiction:"
  print prob1('science_fiction',None)

  # Do the same thing for a different tagset: Universal

  print "Tag FreqDist for news with Universal tagset:"
  print prob1('news','universal')

  print "Tag FreqDist for science_fiction with Universal tagset:"
  print prob1('science_fiction','universal')

'''
Tag FreqDist for news:
(218, [(u'NN', 13162), (u'IN', 10616), (u'AT', 8893), (u'NP', 6866), (u',', 5133), (u'NNS', 5066), (u'.', 4452), (u'JJ', 4392), (u'CC', 2664), (u'VBD', 2524)])

Tag FreqDist for science_fiction:
(127, [(u'NN', 1541), (u'IN', 1176), (u'.', 1077), (u'AT', 1040), (u',', 791), (u'JJ', 723), (u'NNS', 532), (u'VBD', 531), (u'RB', 522), (u'VB', 495)])

Tag FreqDist for news with Universal tagset:
(12, [(u'NOUN', 30654), (u'VERB', 14399), (u'ADP', 12355), (u'.', 11928), (u'DET', 11389), (u'ADJ', 6706), (u'ADV', 3349), (u'CONJ', 2717), (u'PRON', 2535), (u'PRT', 2264)])

Tag FreqDist for science_fiction with Universal tagset:
(12, [(u'NOUN', 2747), (u'VERB', 2579), (u'.', 2428), (u'DET', 1582), (u'ADP', 1451), (u'PRON', 934), (u'ADJ', 929), (u'ADV', 828), (u'PRT', 483), (u'CONJ', 416)])


For the news genre, there are more tags than the science_fiction genre. There are about 2 times more tags in news than in science_fiction. The first two tags for news and science are the same: NN and IN but the quantity of each of those tags in those genres are different. The NN tag in news has about 13162 occurences but the NN tag in science_fiction has 1541 occurance. The news category most likely has more parts of speech and more words then the science_fiction category. Changing the target, the number of tags changes to 12. The top two cases with the Universal target are Noun and Verb. The number of each tags incerases. For the NOUN tag  
'''

### Uncomment to test problem 1
# Let's look at the top tags for different genre and tagsets
#  and observe the differences
test_prob1()

############# Problem 2 #################
# Solution for problem 2
# Input: sentence (list of string), size (<4600)
# Output: hmm_tagged_sentence (list of tuples), tagger (HiddenMarkovModelTagger)

# hint: use the help on HiddenMarkovModelTagger to find out how to train, tag and evaluate the HMM tagger
def prob2(sentence, size):
  
  tagged_sentences = brown.tagged_sents(categories= 'news')
  
  # set up the training data
  train_data = tagged_sentences[-size:]
  
  # set up the test data
  test_data = tagged_sentences[:100]

  # train a HiddenMarkovModelTagger, using the train() method
  tagger = HiddenMarkovModelTagger.train(train_data)

  # using the hmm tagger tag the sentence
  hmm_tagged_sentence = tagger.tag(sentence)
  
  # using the hmm tagger evaluate on the test data
  eres = tagger.evaluate(test_data)

  return (tagger, hmm_tagged_sentence,eres)

'''

Sentenced tagged with nltk.HiddenMarkovModelTagger:
[(u'The', u'AT'), (u"mayor's", u'QL'), (u'present', u'JJ'), (u'term', u'NN'), (u'of', u'IN'), (u'office', u'NN'), (u'expires', u'.'), (u'Jan.', u'.'), (u'1', u'.'), (u'.', u'.')]
Eval score:
0.714726631393

Sentenced tagged with nltk.HiddenMarkovModelTagger:
[(u'The', u'AT'), (u"mayor's", u'NN$'), (u'present', u'JJ'), (u'term', u'NN'), (u'of', u'IN'), (u'office', u'NN'), (u'expires', u'IN'), (u'Jan.', u'NP'), (u'1', u'CD'), (u'.', u'.')]
Eval score:
0.86860670194

Here we see that for longer training sets the eval score is higher; therefore longer corpora are better  
'''

def test_prob2():
  tagged_sentences = brown.tagged_sents(categories= 'news')
  words = [tp[0] for tp in tagged_sentences[42]]
  (tagger, hmm_tagged_sentence, eres ) = prob2(words,500)
  print "Sentenced tagged with nltk.HiddenMarkovModelTagger:"
  print hmm_tagged_sentence
  print "Eval score:"
  print eres

  (tagger, hmm_tagged_sentence, eres ) = prob2(words,3000)
  print "Sentenced tagged with nltk.HiddenMarkovModelTagger:"
  print hmm_tagged_sentence
  print "Eval score:"
  print eres

### Uncomment to test problem 2
#Look at the tagged sentence and the accuracy of the tagger. How does the size of the training set affect the accuracy?
test_prob2()



############# Problem 3 #################
# Solution for problem 3 (first part)
# Input: tagged_words (list of tuples)
# Output: emission_FD (ConditionalFreqDist), emission_PD (ConditionalProbDist), p_NN (float), p_DT (float)


# in the previous labs we've seen how to build a freq dist
# we need conditional distributions to estimate the transition and emission models
# in this problem we estimate the emission model
def prob3A(tagged_words):

  # prepare the data
  # the data object should be a list of tuples of conditions and observations
  # in our case the tuples will be of the form (tag,word) where words are lowercased
  data = [(i[1], i[0].lower()) for i in tagged_words]

  # compute a Conditional Frequency Distribution for words given their tags using our data
  emission_FD = ConditionalFreqDist(data)
  
  print emission_FD['NN']
  # return the top 10 most frequent words given the tag NN
  top_NN = emission_FD['NN'].most_common(10)
  
  # Compute the Conditional Probability Distribution using the above Conditional Frequency Distribution. Use MLEProbDist estimator.
  emission_PD = ConditionalProbDist(emission_FD, MLEProbDist)
  
  # compute the probabilities of P(year|NN) and P(year|DT)
  p_NN = emission_PD['NN'].prob('year')
  p_DT = emission_PD['DT'].prob('year')
  
  return (emission_FD, top_NN, emission_PD, p_NN, p_DT)


def test_prob3a():
  tagged_words = brown.tagged_words(categories='news')
  (emission_FD, top_NN, emission_PD, p_NN, p_DT) = prob3A(tagged_words)
  print "Frequency of words given the tag *NN*: ", top_NN
  print "P(year|NN) = ", p_NN
  print "P(year|DT) = ", p_DT

### Uncomment to test problem 3a
#Look at the estimated probabilities. Why is P(year|DT) = 0 ? What are the problems with having 0 probabilities and what can be done to avoid this?
'''
Frequency of words given the tag *NN*:  [(u'year', 137), (u'time', 98), (u'state', 92), (u'week', 86), (u'man', 72), (u'home', 72), (u'school', 65), (u'program', 65), (u'night', 64), (u'day', 62)]
P(year|NN) =  0.0104087524692
P(year|DT) =  0.0

P(year|DT) is 0 because year is never a determiner but is often a noun. The problem with having 0 probabilities is that 
the HMM will break if it ever encounters that possibility. It is best to smooth with some kind of 
smoothing algorithm.

'''
#test_prob3a()

############# Problem 3 part B #################
# Solution for problem 3 part B
# Input: tagged_sentences (list)
# Output: emission_FD (ConditionalFreqDist), emission_PD (ConditionalProbDist), p_VBD_NN, p_DT_NN

# compute the transition probabilities
# the probabilties of a tag at position i+1 given the tag at position i
def prob3b(tagged_sentences):
  
  # prepare the data
  # the data object should be an array of tuples of conditions and observations
  # in our case the tuples will be of the form (tag_(i),tag_(i+1))
  data = []
  for i in range(len(tagged_sentences)):
      for j in range(len(tagged_sentences[i])-1):
        data.append((tagged_sentences[i][j][1],tagged_sentences[i][j+1][1]))
  

  # compute the Conditional Frequency Distribution for a tag given the previous tag
  transition_FD = ConditionalFreqDist(data)
  
  # compute the Conditional Probability Distribution for the
  # transition probability P(tag_(i+1)|tag_(i)) using the MLEProbDist
  # to estimate the probabilities
  transition_PD = ConditionalProbDist(transition_FD, MLEProbDist)

  # compute the probabilities of P(NN|VBD) and P(NN|DT)
  p_VBD_NN = transition_PD['VBD'].prob('NN')
  p_DT_NN = transition_PD['DT'].prob('NN')

  return (transition_FD, transition_PD,p_VBD_NN, p_DT_NN )


def test_prob3b():
  tagged_sentences = brown.tagged_sents(categories= 'news')
  (transition_FD, transition_PD,p_VBD_NN, p_DT_NN ) = prob3b(tagged_sentences)
  print "P(NN|VBD) = ", p_VBD_NN
  print "P(NN|DT) = ", p_DT_NN

### Uncomment to test problem 3 part B
# Are the results what you would expect? The sequence NN DT seems very probable. How will this affect the sequence tagging
'''
P(NN|VBD) =  0.0285261489699
P(NN|DT) =  0.528911564626P

I would think determiners would be higher because often nouns go after determiners. 
The algorithm will choose nouns after determiners more times than nouns would be after verbs. 
'''
#test_prob3b()
