import re
import string 
import nltk.tokenize 
import os 
import sys
# Usage ./tokenize directory

# no punctuation

def speech_parse(file):
    with open(sys.argv[1] +'/' + file) as f:
        lines = f.readlines()
        text = []
        del lines[0:2]
        for line in lines:
                line = re.sub("---", "", line)
                line = re.sub("--", " ", line)
                line = re.sub("-", " ", line)
                tokenized = nltk.word_tokenize(line)
                text.append(tokenized)
            
def clean_speech(lines):
   
    print lines 


def dir_parse():
    for filename in os.listdir(sys.argv[1]):
	if filename.endswith(".txt"): 
	    speech_parse(filename)
	else:
	    continue


