import re
import string 
import nltk.tokenize 
import os 
import sys

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
        text = [x for x in text if x != []]
	return text 
            
def clean_speech(lines):
    tokens = ["<s>"]
    punct = ["?", ".", "!",".."," ", '"']
    line = nltk.word_tokenize(lines)
    print line
    for i in range(len(line)):
	if line[i] in punct:
	    tokens.extend(["</s>", "<s>"])
	elif line[i] != ",":
	    tokens.extend([line[i].lower()])
    tokens.extend(["</s>"])
    if len(tokens) > 2:
	while (tokens[len(tokens) - 2] == "<s>"):
	    tokens = tokens[:len(tokens) - 2]
	while (tokens[1] == "</s>"):
		    tokens = tokens[2:]
    return tokens


for filename in os.listdir(sys.argv[1]):
    if filename.endswith(".txt"): 
	for i in speech_parse(filename):
		print clean_speech(i) 
    else:
   	print "Usage: python tok.py directory"	

