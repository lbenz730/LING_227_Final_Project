import re
import string
from nltk.tokenize import TweetTokenizer


### Parses File of Tweets and create an array of tweets
def tweet_parse(file):
	tokenizer = TweetTokenizer()
	with open(file) as tweet:
		tweets = []
		tmp = tweet.readlines()
		### Clean Tweet
		for tweet in tmp:
			tweet = re.sub("http.*", "", tweet)
			tweet = re.sub(r"\\", "", tweet)
			tweet = re.sub(r"/", " ", tweet)
			try: 
				" ".join(tokenizer.tokenize(tweet))
			except UnicodeDecodeError:
				tweet = "RT @"
			### Remove Re-Tweets
			if not re.findall("RT @", tweet):
				tweets.extend([tweet])
		return tweets


### Cleans a tweet, returns an array of tokens
def clean_tweet(tweet):
	tokenizer = TweetTokenizer()
	tweet = tokenizer.tokenize(tweet)
	tokens = ["<s>"]
	punct = ["?", ".", "!",".."," ", '"']
	for i in range(len(tweet)):
		if tweet[i] in punct:
			tokens.extend(["</s>", "<s>"])
		elif tweet[i] != ",":
			tokens.extend([tweet[i].lower()])

	tokens.extend(["</s>"])
	### Remove extra punctuation
	if len(tokens) > 2:
		
		while (tokens[len(tokens) - 2] == "<s>"):
			tokens = tokens[:len(tokens) - 2]
		while (tokens[1] == "</s>"):
			tokens = tokens[2:]
	return tokens
