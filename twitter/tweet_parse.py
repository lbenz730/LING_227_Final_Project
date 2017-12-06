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
	tweet[0] = "<s>"
	tweet[len(tweet)-1] = "</s>"
	tokens = []
	punct = ["?", ".", "!"]
	for i in range(len(tweet)):
		if tweet[i] in punct:
			tokens.extend(["</s>", "<s>"])
		elif tweets[i] != ",":
			tokens.extend([tweet[i]])

	### Remove extra punctuation
	while (tokens[len(tokens) - 2] == "<s>"):
		tokens = tokens[:len(tokens) - 2]

	return tokens