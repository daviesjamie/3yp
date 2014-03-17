from __future__ import division
from multiprocessing import Lock
from spout.structs import Function, Operation
import time
from twokenize.twokenize import tokenize
import cPickle as pickle


class TrainOperation(Operation):
    """
    Takes in a stream of tokenized tweets and builds a dictionary keeping track of how many times
    each non-hashtag token is associated with a hashtag.
    """
    def __init__(self, classifier):
        self.classifier = classifier

    def perform(self, obj):
        self.classifier.train(obj)


class Classifier(object):
    """
    A naive bayes classifier that uses an internal model of the counts of hashtags appearing for
    each given token to calculate the probability of a hashtag given a token.

    For example, given the tweet:
    "Such a great day! #sunny #sohappy"

    Would be tokenized into:
    ['Such', 'a', 'great', 'day', '!', '#sunny', '#sohappy']

    Resulting in a model looking like:
    {
        'such'  => { 'sunny' => 1, 'sohappy' => 1 },
        'a'     => { 'sunny' => 1, 'sohappy' => 1 },
        'great' => { 'sunny' => 1, 'sohappy' => 1 },
        'day'   => { 'sunny' => 1, 'sohappy' => 1 },
        '!'     => { 'sunny' => 1, 'sohappy' => 1 }
    }
    """
    def __init__(self):
        self.tweet_total = 0

        self.model = {}

        self.token_count = {}
        self.token_total = 0

        self.hashtag_count = {}
        self.hashtag_total = 0

        self.lock = Lock()

    def train(self, tweet):
        # Separate hashtags and tokens
        hashtags = set()
        tokens = set()
        for token in tweet:
            if token[0] == '#' and len(token) > 1:
                hashtags.add(unicode(token[1:]).lower())
            else:
                tokens.add(unicode(token).lower())

        # Ensure tweet has some hashtags and some non-hashtag tokens
        if len(hashtags) == 0 or len(tokens) == 0:
            return

        with self.lock:
            for token in tokens:
                # Increment token -> hashtag count (model)
                if token in self.model:
                    for hashtag in hashtags:
                        self.model[token][hashtag] = self.model[token].get(hashtag, 0) + 1
                else:
                    self.model[token] = dict.fromkeys(hashtags, 1)

                # Increment token_count
                self.token_count[token] = self.token_count.get(token, 0) + 1

                # Increment token_total
                self.token_total += 1

            for hashtag in hashtags:
                # Increment hashtag_count
                self.hashtag_count[hashtag] = self.hashtag_count.get(hashtag, 0) + 1

                # Increment hashtag_total
                self.hashtag_total += 1

            # Increment tweet_total
            self.tweet_total += 1

    def classify(self, tweet, results=5):
        # Twokenize tweet
        tweet_tokens = tokenize(tweet)

        # Filter out hashtags
        tokens = set()
        for token in tweet_tokens:
            if token[0] != '#':
                tokens.add(unicode(token).lower())

        # Apply Bayes' Theorem:
        #
        #                      P(Token|Hashtag) * P(Hashtag)
        # P(Hashtag|Token) = --------------------------------
        #                               P(Token)
        #
        #
        #                          P(Hashtag) * P(Hashtag|Tokens[0]) * P(Hashtag|Tokens[1]) * ... * P(Hashtag|Tokens[N])
        # P(Hashtag|[Tokens]) =  -----------------------------------------------------------------------------------------
        #                                       P(Tokens[0]) * P(Tokens[1]) * ... * P(Tokens[N])

        probs = {}
        with self.lock:
            for token in tokens:
                # Ensure the token is known to the classifier
                if token in self.model:
                    p_token = self.token_count[token] / self.token_total

                    for hashtag in self.model[token]:
                        # Calculate individual probabilities
                        p_hashtag = self.hashtag_count[hashtag] / self.hashtag_total
                        p_token_hashtag = self.model[token][hashtag] / self.token_total

                        # Accumulate probabilities across all tokens
                        probs[hashtag] = probs.get(hashtag, p_hashtag) * \
                                         ( p_token_hashtag * p_hashtag ) / p_token

                        print "token:\t\t\t" + token
                        print "hashtag:\t\t" + hashtag
                        print "p_token:\t\t" + str(p_token)
                        print "p_hashtag:\t\t" + str(p_hashtag)
                        print "p_token_hashtag:\t" + str(p_token_hashtag)
                        print "---------------------------------------------------"

        return sorted(probs.iteritems(), key=lambda t: t[1], reverse=True)[:results]

    def state_dump(self, fileprefix):
        with open("{0}-{1}.pickle".format(fileprefix, time.strftime("%Y%m%d%H%M%S")), "wb") as f:
            with self.lock:
                pickle.dump(self.token_count, f, pickle.HIGHEST_PROTOCOL)
                pickle.dump(self.model, f, pickle.HIGHEST_PROTOCOL)
                pickle.dump(self.tweet_total, f, pickle.HIGHEST_PROTOCOL)

    def state_load(self, filename):
        with open(filename, "rb") as f:
            with self.lock:
                self.token_count = pickle.load(f)
                self.model = pickle.load(f)
                self.tweet_total = pickle.load(f)

    ################################################################################################
    # Getter methods

    def get_tweet_total(self):
        with self.lock:
            return self.tweet_total

    def get_model(self):
        with self.lock:
            return self.model

    def get_token_count(self):
        with self.lock:
            return self.token_count

    def get_token_total(self):
        with self.lock:
            return self.token_total

    def get_hashtag_count(self):
        with self.lock:
            return self.hashtag_count

    def get_hashtag_total(self):
        with self.lock:
            return self.hashtag_total
