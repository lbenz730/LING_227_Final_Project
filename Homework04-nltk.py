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

# frequency distribution module from 
from nltk import FreqDist

import operator
import random
import collections

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
  
  # Build a list of the tags associated with each word
  tags = [tag for (word, tag) in tagged_words]

  # Compute the Frequency Distribution of tags in the corpus
  tagsFD = FreqDist(tags)
  
  # Retrieve the total number of tags in the tagset
  number_of_tags = len(tagsFD.values())
  
  # Retrieve the top 10 most frequent tags
  top_tags = sorted(tagsFD, key=tagsFD.__getitem__, reverse = True)
  top_tags = top_tags[:10]
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

### Uncomment to test problem 1
# Let's look at the top tags for different genre and tagsets
#  and observe the differences
test_prob1()

### Obeservations ###
# Across the two genres, we see similar patterns in the most commonly used tags. Namely, in both genres, nouns (NOUN or NN) are most common, with 
# various punctuation and determiners among other frequently used tags. Interestingly, regardless of the tag sets we use, adjectives and conjunctions
# both show up more frequently in the news genre than in the science fiction genre. Using the Brown tag set yields over ten-fold more tags in each genre
# than the Universal tag set. When using the Brown tag set, the news genre uses many more tags than the science fiction genre, while both genres use only 
# 12 tags in under the Universal tag set, likely due to its reduced size. Under the Universal set, Verbs are much more common as the Brown tag set subcategorizes 
# verbs, while under thr Brown corpus, prepositions are much more common, as this tag doesn't exist in the Universal tag set.

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

  # TODO: train a HiddenMarkovModelTagger, using the train() method
  tagger = nltk.tag.hmm.HiddenMarkovModelTagger.train(train_data)

  # TODO: using the hmm tagger tag the sentence
  hmm_tagged_sentence = tagger.tag(sentence)
  
  # TODO: using the hmm tagger evaluate on the test data
  eres = tagger.evaluate(test_data)


  return (tagger, hmm_tagged_sentence,eres)


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

### Observations: ###
# We observe that as the size of the training set increases, the accuracy of the tagger increases. This is observed in both the overall
# evaluation score as well as the accuracy of tags on our output sentence.



############# Problem 3 #################
# Solution for problem 3 (first part)
# Input: tagged_words (list of tuples)
# Output: emission_FD (ConditionalFreqDist), emission_PD (ConditionalProbDist), p_NN (float), p_DT (float)


# in the previous labs we've seen how to build a freq dist
# we need conditional distributions to estimate the transition and emission models
# in this problem we estimate the emission model
def prob3a(tagged_words):

  # TODO: prepare the data
  # the data object should be a list of tuples of conditions and observations
  # in our case the tuples will be of the form (tag,word) where words are lowercased
  data = [(tag, word.lower()) for (word, tag) in tagged_words]

  # TODO: compute a Conditional Frequency Distribution for words given their tags using our data
  emission_FD = ConditionalFreqDist(data)
  
  # TODO: return the top 10 most frequent words given the tag NN
  words_NN = emission_FD["NN"]
  top_NN = words_NN.most_common(10)
  
  # TODO: Compute the Conditional Probability Distribution using the above Conditional Frequency Distribution. Use MLEProbDist estimator.
  emission_PD = ConditionalProbDist(emission_FD, MLEProbDist)
  
  # TODO: compute the probabilities of P(year|NN) and P(year|DT)
  p_NN = emission_PD["NN"].prob("year")
  p_DT = emission_PD["DT"].prob("year")

  
  return (emission_FD, top_NN, emission_PD, p_NN, p_DT)


def test_prob3a():
  tagged_words = brown.tagged_words(categories='news')
  (emission_FD, top_NN, emission_PD, p_NN, p_DT) = prob3a(tagged_words)
  print "Frequency of words given the tag *NN*: ", top_NN
  print "P(year|NN) = ", p_NN
  print "P(year|DT) = ", p_DT

### Uncomment to test problem 3a
#Look at the estimated probabilities. Why is P(year|DT) = 0 ? What are the problems with having 0 probabilities and what can be done to avoid this?
test_prob3a()

### Observations: ###
# P(year|DT) = 0 because we never obseve the word "year" tagged as a DT. Specifically, emission_FD['DT']['year'] = 0 (compared to 
# emission_FD['NN']['year'] = 137). A problem of having 0 probabilities is that the model will not generate certain words given a tag. This
# is problematic because even though we may not observe a certain (word, tag) pair (espeically for less common words), we want to be able to 
# assign in the correct tag, which will not be possible if the correct (word, tag) pair has yet to appear. A way to avoid this is to use
# smoothing (add-1, add-lambda, or backoff for example) to assign small probability mass to every possible (word, tag) pair.


############# Problem 3 part B #################
# Solution for problem 3 part B
# Input: tagged_sentences (list)
# Output: emission_FD (ConditionalFreqDist), emission_PD (ConditionalProbDist), p_VBD_NN, p_DT_NN

# compute the transition probabilities
# the probabilties of a tag at position i+1 given the tag at position i
def prob3b(tagged_sentences):
  
  # TODO: prepare the data
  # the data object should be an array of tuples of conditions and observations
  # in our case the tuples will be of the form (tag_(i),tag_(i+1))
  tags = []
  for sentence in tagged_sentences:
    tmp = [tag for (word, tag) in sentence]
    tags.extend(tmp)

  data = [(tags[i], tags[i+1]) for i in range(len(tags) - 1)]

  # TODO: compute the Conditional Frequency Distribution for a tag given the previous tag
  transition_FD = ConditionalFreqDist(data)
  
  # TODO: compute the Conditional Probability Distribution for the
  # transition probability P(tag_(i+1)|tag_(i)) using the MLEProbDist
  # to estimate the probabilities
  transition_PD = ConditionalProbDist(transition_FD, MLEProbDist)

  # TODO: compute the probabilities of P(NN|VBD) and P(NN|DT)
  p_VBD_NN = transition_PD["VBD"].prob("NN")
  p_DT_NN = transition_PD["DT"].prob("NN")

  return (transition_FD, transition_PD,p_VBD_NN, p_DT_NN )


def test_prob3b():
  tagged_sentences = brown.tagged_sents(categories= 'news')
  (transition_FD, transition_PD,p_VBD_NN, p_DT_NN ) = prob3b(tagged_sentences)
  print "P(NN|VBD) = ", p_VBD_NN
  print "P(NN|DT) = ", p_DT_NN

### Uncomment to test problem 3 part B
# Are the results what you would expect? The sequence NN DT seems very probable. How will this affect the sequence tagging?
test_prob3b()


### Observations: ###
# These are the reults we'd expect. We'd expect the NN DT very often, and in fact see that P(NN|DT) > 0.5 . This will assign NN to the tag following DT 
# more frequently than all other possible tags combined. Thus, we may misclassify certain words following the DT tag, especially in longer sequences 
# such as "The big red hair dog", where we have three adjectives seperating DT from NN.










