import re
import string 
import nltk.tokenize 
import os 
import sys

reload(sys)
sys.setdefaultencoding('utf8')

# no punctuation

def speech_parse(file, dir):
    with open(dir +'/' + file) as f:
        lines = f.readlines()
        text = []
        del lines[0:2]
        for line in lines:
                line = re.sub("---", "", line)
                line = re.sub("--", " ", line)
                line = re.sub("-", " ", line)
                tokenized = nltk.word_tokenize(line)
                try:
                    index = tokenized.index(">")
                    tokenized = tokenized[index+1:]
                except(ValueError):
                    pass
                tokenized = " ".join(tokenized)
                text.append(tokenized)
        text = [x for x in text if x != []]
	return text 
            
def clean_speech(lines):
    tokens = ["<s>"]
    punct = ["?", ".", "!",".."," ", '"']
    line = nltk.word_tokenize(lines)
    for i in range(len(line)):
	if line[i] in punct:
	    tokens.extend(["</s>", "<s>"])
	elif line[i] != ",":
	    tokens.extend([line[i].lower()])
    tokens.extend(["</s>"])
    if len(tokens) > 2:
        try:
            while (tokens[len(tokens) - 2] == "<s>"):
	        tokens = tokens[:len(tokens) - 2]
	    while (tokens[1] == "</s>"):
	        tokens = tokens[2:]
        except(IndexError):
            return tokens
    return tokens
 
def parse(dir):
    arr = list()
    for filename in os.listdir(dir):
        if filename.endswith(".txt"): 
            for i in speech_parse(filename,dir):
                parse = clean_speech(i) 
                if len(parse) > 2:
                    arr.append(parse)
        else:
            print "Usage: python tok.py directory"
    return arr



