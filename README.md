# Ling 227 Final Project

History remembers great speakers for their idiosyncracies. From JFK's authenticity and passion to Donald Trump's divisive rhetoric, U.S. presidents are particularly identifiable by their speeches. While nearly any citizen can name the presidents who said "Nothing to fear but fear itself" (Franklin Delano Roosevelt), "Ask not what your country can do for you--ask what you can do for your country" (John F. Kennedy), and "Yes We Can!" (Barack Obama), it remains to be seen whether a language model can do the same. Our project aims to build a language model that determines the most likely speaker of a given input quote. Morover, our project seeks to investigate how the model discernability changes when trained on three types of data: presidential speeches, part of speech tags for presidental speechs, and politicans' tweets.

### Dependecies
```
pip install scipy
pip install numpy
pip install nltk
```
### Running the Bigram Language Model 

To parse and clean the tweets, look at tweet_parse.py. It parses a directory for all the .txt files and returns a list of all cleaned and parsed sentences from all the tweets.

To parse and clean the speeches, look at tok.py. It parses a directory for all the .txt files and returns a list of all cleaned and parsed sentences from all the speeches.

To smooth bigram model with good turing smooth, look at good_turing.py. It applies good_turing smoothing using a logarithmic function. 


To train model and find probabilities of sentences using tweets:

```
python ngram.py -good_turing -tweet TWEET.txt 2 tweet_quotes.txt
```

To train model and find probabilities of sentences using speeches:

```
python ngram.py -good_turing -speech DIR 2 presidential_quotes.txt
```

## Results
For the tweets:
![alt text](https://github.com/lbenz730/LING_227_Final_Project/blob/master/tweet_results.png)

For the speeches:
![alt text](https://github.com/lbenz730/LING_227_Final_Project/blob/master/presidential_results.png)

## Authors

* **Luke Benz** - (https://github.com/lbenz730)
* **Will Langhorne** - (https://github.com/wlanghorne)
* **Kevin Truong** - (https://github.com/ketruong)

See also the list of [contributors](https://github.com/lbenz730/LING_227_Final_Project/graphs/contributors) who participated in this project.


## Works Cited

* Gale, W. and G. Sampson. Good Turing Estimation Without Tears. Journal of Quantitative Linguistics, vol. 2, 217-237, 1995.
* Japi, A. Mimicking Writing Style With Markov Chains. The Sopranos, Silicon Valley, and Summer Afternoons. http://aakashjapi.com/mimicking-writing-style-with-markov-chains/
* Mosteller, F. and D. L. Wallace. Inference and Disputed Authorship: The Federalist. Reading, MA., 1964.
* Zheng, R., Li, J., Chen, H. and Huang, Z. A framework for authorship identification of online messages: Writing-style features and classification techniques. J. Am. Soc. Inf. Sci., 57: 378–393, 2006.
