import nltk
import sys
import re
#import brown corpus
from nltk.corpus import brown

# module for training a Hidden Markov Model and tagging sequences
from nltk.tag.hmm import HiddenMarkovModelTagger

# module for computing a Conditional Frequency Distribution
from nltk.probability import ConditionalFreqDist

# module for computing a Conditional Probability Distribution
from nltk.probability import ConditionalProbDist, LidstoneProbDist

### added:
from nltk.tag import map_tag
assert map_tag('brown','universal','NR-TL')=='NOUN'
###

import operator
import random
from math import log
from collections import defaultdict
import numpy as np

class HMM:
  def __init__(self,train_data,test_data):
    self.train_data = train_data
    self.test_data = test_data
    self.states = []
    self.viterbi = []
    self.backpointer = []

  #TODO problem 1
  #compute emission model using ConditionalProbDist with the estimator: Lidstone probability distribution with +0.01 added to the sample count for each bin
  def emission_model(self,train_data):
    #TODO prepare data
    #don't forget to lowercase the observation otherwise it mismatches the test data
    
    ### Collect tags and words (lowercased)
    data = []
    for sentence in train_data:
      tmp = [(tag, word.lower()) for (word, tag) in sentence]
      data.extend(tmp)
    
    #TODO compute the emission model
    emission_FD = ConditionalFreqDist(data)
    self.emission_PD = ConditionalProbDist(emission_FD, LidstoneProbDist, 0.01)
    self.states = [u'.', u'ADJ', u'ADP', u'ADV', u'CONJ', u'DET', u'NOUN', u'NUM', u'PRON', u'PRT', u'VERB', u'X']
    #print "states: ",self.states,"\n\n"
    #states:  [u'.', u'ADJ', u'ADP', u'ADV', u'CONJ', u'DET', u'NOUN', u'NUM', u'PRON', u'PRT', u'VERB', u'X']

    return self.emission_PD, self.states

  #test point 1a
  def test_emission(self):
    print "test emission"
    t1 = -self.emission_PD['NOUN'].logprob('fulton') #10.7862305592
    t2 = -self.emission_PD['X'].logprob('fulton') #12.324461856
    return t1,t2

  #compute transition model using ConditionalProbDist with the estimator: Lidstone probability distribution with +0.01 added to the sample count for each bin
  def transition_model(self,train_data):
    data = []
    # TODO: prepare the data
    # the data object should be an array of tuples of conditions and observations
    # in our case the tuples will be of the form (tag_(i),tag_(i+1))
    # DON'T FORGET TO ADD THE START SYMBOL <s> and the END SYMBOL </s>
    tags = []
    for sentence in train_data:
      tmp = ["<s>"] ### Begining of sentenence
      tags_in_sent = [tag for (word, tag) in sentence] ### Get Tags in sentence
      tmp.extend(tags_in_sent)
      tmp.extend(["</s>"]) ### End of sentence
      tags.extend(tmp) ### Add to existing tag set

    data = [(tags[i], tags[i+1]) for i in range(len(tags) - 1)]
    
    #TODO compute the transition model
    transition_FD = ConditionalFreqDist(data)
    self.transition_PD = ConditionalProbDist(transition_FD, LidstoneProbDist, 0.01)
 
    return self.transition_PD
  
  #test point 1b
  def test_transition(self):
    print "test transition"
    transition_PD = self.transition_model(self.train_data)
    start = -transition_PD['<s>'].logprob('NOUN') #1.78408417115
    end = -transition_PD['NOUN'].logprob('</s>') #7.31426021816
    return start,end

  #train the HMM model
  def train(self):
    self.emission_model(self.train_data)
    self.transition_model(self.train_data)
  
  def set_models(self,emission_PD,transition_PD):
    self.emission_PD = emission_PD
    self.transition_PD = transition_PD
  
  #initialize data structures for tagging a new sentence
  #describe the data structures with comments
  #use the models stored in the variables: self.emission_PD and self.transition_PD
  #input 'observation' is first word in the sentence that you will need to tag
  def initialize(self,observation):
    #del self.viterbi[:]
    #del self.backpointer[:]
    #initialize for transition from <s> , begining of sentence
    # use costs (-log-base-2 probabilities)
    #TODO
    
    ### Initilaize Viterbi Structure and Backpointer Structure
    self.viterbi = defaultdict(lambda:defaultdict(lambda:0))
    self.backpointer = defaultdict(lambda:defaultdict(lambda:0))

    for state in self.states:
      self.viterbi[state][0] = -log(self.transition_PD["<s>"].prob(state), 2) - log(self.emission_PD[state].prob(observation), 2)
      self.backpointer[state][0] = "<s>"

  ### Implementations Comments ###
  # In this probelm, I initialize both the viterbi and backpointer structures using nested defaultdicts. This effectively creates a 
  # 2 dimensional array for which we can store our trellis values and the corresponding pointers allowing us to recreate our tagged
  # sequence. I specifically chose to make use of the defaultdict data structure since we don't have to worry about creating the proper
  # dimensions during initialization. Specifically, during the initialization stage, we don't know the length of the sentence we 
  # will tag, and thus don't know how large to make our structues. Since defaultdict structures allow for dynamic memory allocation, we effectively
  # deal with this problem.



   
  
  #tag a new sentence using the trained model and already initialized data structures
  #use the models stored in the variables: self.emission_PD and self.transition_PD
  #update the self.viterbi and self.backpointer datastructures
  #describe your implementation with comments
  #input 'observations' is the list of words to be tagged (including the first word)
  def tag(self,observations):
    for t in range(1,len(observations)):
      for state in self.states:
        ### Compute probability and backpointer for arriving at desired state
        next_viterbi = []
        next_backpointer = []
        for i in range(len(self.states)):
          next_viterbi.extend([self.viterbi[self.states[i]][t - 1] - log(self.transition_PD[self.states[i]].prob(state), 2) - log(self.emission_PD[state].prob(observations[t]), 2)])
          next_backpointer.extend([self.viterbi[self.states[i]][t - 1] - log(self.transition_PD[self.states[i]].prob(state), 2)])
        ### Find Max (min for -log) probability and corresponding backpointer
        self.viterbi[state][t] = min(next_viterbi)
        self.backpointer[state][t] = self.states[np.argmin(next_backpointer)]

        
    #add termination step (for transition to </s> , end of sentence)
    next_viterbi = []
    for i in range(len(self.states)):
        next_viterbi.extend([self.viterbi[self.states[i]][len(observations) - 1] - log(self.transition_PD[self.states[i]].prob("</s>"), 2)])
    self.viterbi["</s>"][len(observations)] = min(next_viterbi)
    self.backpointer["</s>"][len(observations)] = self.states[np.argmin(next_viterbi)]


    #TODO
    #reconstruct the tag sequence using the backpointer
    #return the tag sequence corresponding to the best path as a list (order should match that of the words in the sentence)
    bp = self.backpointer["</s>"][len(observations)]
    tags = [None] * len(observations)
    tags[len(observations)-1] = bp
    for t in reversed(xrange(1,len(observations))):
      tag = self.backpointer[bp][t]
      tags[t-1] = tag
      bp = tag
    return tags

  ### Implementation notes ###
  # To calculate each Viterbi[s][t], I begin by looping over all possible states we could have come from. For each of these possible states,
  # I compute the -logprob of arriving in state s from state (s-1) and emitting tag t. I then compute the minimun(-logprob) to get the Viterbi[s][t]
  # value, and obtain the proper back pointer using the numpy.argmin() function. Finally I implement the termination step in a similar manner to determine
  # the mostly likely state prior to </s>. To obtain the coresponding tag sequence, I trace the back pointers as follows:
  #     1. The final tag is given by the backpointer to </s>
  #     2. Loop over remaining tag positions from end of sentence to beginning of sentence:
  #         a. obtain the next tag as the current backpointer
  #         b. add tag to our set of tags in proper sentence position
  #         c. update our backpointer by taking the backpointer of the most recent tag
  #     3. return the tag set after we have obtained all tags (i.e # tags = length(sentence))


def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    # http://stackoverflow.com/a/33024979
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

def train_hmm():
  #devide corpus in train and test data
  tagged_sentences_Brown = brown.tagged_sents(categories= 'news')
  test_size = 1000
  train_size = len(tagged_sentences_Brown)-1000

  train_data_Brown = tagged_sentences_Brown[:train_size]
  test_data_Brown = tagged_sentences_Brown[-test_size:]

  tagged_sentences_Universal = brown.tagged_sents(categories= 'news', tagset='universal')
  train_data_Universal = tagged_sentences_Universal[:train_size]
  test_data_Universal = tagged_sentences_Universal[-test_size:]


    #create instance of HMM class and initialize the training and test sets
  obj = HMM(train_data_Universal,test_data_Universal)
  
  return obj
def get_tags():
  obj = train_hmm()
  #train HMM
  obj.train()
  file = open(sys.argv[1]).readlines()
  #part B: test accuracy on test set
  for sentence in file:
    sentence = re.sub("<s> ", "", sentence)
    sentence = re.sub("</s>", ".", sentence)
    s = sentence.split(" ")
    obj.initialize(s[0])
    tags = obj.tag(s)
    sent = "<s> " +  " ".join(tags) + " </s>"
    sent = re.sub(r"\.", "<s> </s>", sent)
    print " ".join(sent.split(" ")[:len(sent.split(" ")) - 3]) + " </s>"
  

if __name__ == '__main__':
  
  get_tags()










