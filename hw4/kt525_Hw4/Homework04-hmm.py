import nltk

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
import sys
from math import log
from collections import defaultdict

# Kevin Truong
# kt525
# 11/15/2017
# Pset 4 Homework04-nltk.py

class HMM:
  def __init__(self,train_data,test_data):
    self.train_data = train_data
    self.test_data = test_data
    self.states = []
    self.viterbi = []
    self.backpointer = []

  ############################## problem 1a ####################################
  def emission_model(self,train_data):
    #prepare data
    print train_data
    data = []
    #don't forget to lowercase the observation otherwise it mismatches the test data
    for i in train_data:
        for j in i:
            data.append((j[1], j[0].lower()))
    #compute the emission model
    emission_FD = ConditionalFreqDist(data) 
    self.emission_PD = ConditionalProbDist(emission_FD,LidstoneProbDist,0.01)
    self.states = self.emission_PD.keys()
    
    print "states: ",self.states,"\n\n"
    #states:  [u'.', u'ADJ', u'ADP', u'ADV', u'CONJ', u'DET', u'NOUN', u'NUM', u'PRON', u'PRT', u'VERB', u'X']

    return self.emission_PD, self.states

  #test point 1a
  def test_emission(self):
    print "test emission"
    t1 = -self.emission_PD['NOUN'].logprob('fulton') #10.7862305592
    t2 = -self.emission_PD['X'].logprob('fulton') #12.324461856
    return t1,t2

  
  ############################## problem 1a ####################################
  #compute transition model using ConditionalProbDist with the estimator: Lidstone probability distribution with +0.01 added to the sample count for each bin
  
  def transition_model(self,train_data):
    data = []
    
    # prepare the data
    # the data object should be an array of tuples of conditions and observations
    # in our case the tuples will be of the form (tag_(i),tag_(i+1))
    # DON'T FORGET TO ADD THE START SYMBOL <s> and the END SYMBOL </s>
    
    for s in range(len(train_data)):
        data.append(('<s>', train_data[s][0][1]))
        for i in range(len(train_data[s])-1):
            data.append((train_data[s][i][1],train_data[s][i+1][1]))
        data.append((train_data[s][(len(train_data[s]))-1][1],'</s>')) 

    
    #compute the transition model
    transition_FD = ConditionalFreqDist(data) 
    self.transition_PD = ConditionalProbDist(transition_FD, LidstoneProbDist,0.01)
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
    del self.viterbi
    del self.backpointer
    #initialize for transition from <s> , begining of sentence
    # use costs (-log-base-2 probabilities)
    self.viterbi = defaultdict(lambda:defaultdict(lambda:0))
    self.backpointer = defaultdict(lambda:defaultdict(lambda:0))
    #initialize backpointer
    for s in self.states:
        self.viterbi[s][0] += self.emission_PD[s].logprob(observation) +  self.transition_PD['<s>'].logprob(s) 
        self.backpointer[s][0] = 0
    
  #tag a new sentence using the trained model and already initialized data structures
  #use the models stored in the variables: self.emission_PD and self.transition_PD
  #update the self.viterbi and self.backpointer datastructures
  #describe your implementation with comments
  #input 'observations' is the list of words to be tagged (including the first word)
  
  #P(year|NN) = emission_PD['NN'].prob('year')
  def tag(self,observations):
    tags = []
    index = 0
    current_decisions = []
    T = len(observations)
    for t in range(1,T):
      for state in self.states:

          #set to absolute minimum
          minim_b = float('-inf') 
          minim_v = float('-inf')

          #maximize the trellis
          for sprime in self.states:
              minim_v = max(minim_v, self.viterbi[sprime][t-1] +  self.transition_PD[sprime].logprob(state) +  self.emission_PD[state].logprob(observations[t]))
          self.viterbi[state][t] = minim_v 
          
          #look for argmax
          for sprime in self.states:
              b = self.viterbi[sprime][t-1] +  self.transition_PD[sprime].logprob(state)
              if b > minim_b:
                  minim_b = b
                  self.backpointer[state][t] = sprime 


    #termination step
    minim_v = float('-inf') 
    for s in self.states:
        minim = max(minim_v,  self.viterbi[s][T-1] +  self.transition_PD[s].logprob('</s>'))
        #print minim, s, observations
    self.viterbi['</s>'][T-1] = minim_v 
    minim_b = float('-inf') 
    for s in self.states:
         b = self.viterbi[s][T-1] +  self.transition_PD[s].logprob('</s>')
         if b > minim_b:
            minim_b = b
            self.backpointer['</s>'][T-1] = s

    #reconstruct the tag sequence using the backpointer
    #return the tag sequence corresponding to the best path as a list (order should match that of the words in the sentence)
    qf= self.backpointer['</s>'][T-1]
    current_decisions.append(qf)
    index  = T-1
    while index> 0:
        qf = self.backpointer[qf][index]
        current_decisions.append(qf)
        index -= 1
    #reverse tags
    tags = current_decisions[::-1]
    return tags


def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    # http://stackoverflow.com/a/33024979
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

def main():
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
  
  #train HMM
  obj.train()
  
  #part A: test emission model
  t1,t2 = obj.test_emission()
  if isclose(t1,10.7862305592) and isclose(t2,12.324461856): ### updated again
    print "PASSED test emission\n"
  else:
    print "FAILED test emission\n"
  
  #part A: test transition model
  start,end = obj.test_transition()
  print start,end
  if isclose(start,1.78408417115) and isclose(end,7.31426021816):
    print "PASSED test transition\n"
  else:
    print "FAILED test transition\n"

  #part B: test accuracy on test set
  result = []
  correct = 0
  incorrect = 0
  accuracy = 0
  for sentence in test_data_Universal:
    s = [word.lower() for (word,tag) in sentence]
    obj.initialize(s[0])
    tags = obj.tag(s)
    for i in range(0,len(sentence)):
      if sentence[i][1] == tags[i]:
        correct+=1
      else:
        incorrect+=1
    #print '$$$'
    #print sentence, len(sentence)
  accuracy = 1.0*correct/(correct+incorrect)
  print "accuracy: ",accuracy #accuracy:  0.857186331623
  if isclose(accuracy,0.857142857143): ### updated
    print "PASSED test viterbi\n"
  else:
    print "FAILED test viterbi\n"
  exit() # move me down as you fill in implementations

if __name__ == '__main__':
	
	main()










