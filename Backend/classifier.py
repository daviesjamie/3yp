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
        self.fc = {}
        self.cc = {}
        self.tot = 0

        self.lock_fc = Lock()
        self.lock_cc = Lock()
        self.lock_tot = Lock()

    def get_features(self):
        return self.fc

    def get_counts(self):
        return self.cc

    def train(self, tweet):
        # Separate hashtags
        hashtags = set()
        tokens = set()
        for token in tweet:
            if token[0] == '#' and len(token) > 1:
                hashtags.add(unicode(token[1:]).lower())
            else:
                tokens.add(unicode(token).lower())

        if len(hashtags) == 0 or len(tokens) == 0:
            return

        for token in tokens:
            with self.lock_fc:
                if token in self.fc:
                    for hashtag in hashtags:
                        self.fc[token][hashtag] = self.fc[token].get(
                            hashtag, 0) + 1
                else:
                    self.fc[token] = dict.fromkeys(hashtags, 1)

            with self.lock_cc:
                self.cc[token] = self.cc.get(token, 0) + 1

        with self.lock_tot:
            self.tot += 1

    def classify(self, tweet, results=5):
        # Twokenize tweet
        tweet_tokens = tokenize(tweet)

        # Filter out hashtags
        tokens = set()
        for token in tweet_tokens:
            if token[0] != '#':
                tokens.add(unicode(token).lower())

        # Apply Bayes' Theorem
        # P(Hashtag|Token) = P(Token|Hashtag)P(Hashtag) / P(Token)
        probs = {}
        for token in tokens:
            with self.lock_fc:
                if token in self.fc:
                    for hashtag in self.fc[token]:
                        with self.lock_cc:
                            probs[hashtag] = probs.get(hashtag, 1) * (self.fc[token][hashtag] / self.cc[token])

        return sorted(probs.iteritems(), key=lambda t: t[1])[:results]

    def state_dump(self, fileprefix):
        with open("{0}-{1}.pickle".format(fileprefix, time.strftime("%Y%m%d-%H%M%S")), "wb") as f:
            with self.lock_cc and self.lock_fc:
                pickle.dump(self.cc, f)
                pickle.dump(self.fc, f)

    def state_load(self, filename):
        with open(filename, "rb") as f:
            with self.lock_cc and self.lock_fc:
                self.cc = pickle.load(f)
                self.fc = pickle.load(f)
