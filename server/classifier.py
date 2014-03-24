from __future__ import division
from multiprocessing import Lock
from datetime import datetime
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
        self.tc = {}
        self.tweet_total = 0
        self.hashtag_total = 0
        self.start_time = datetime.now()

        self.lock = Lock()

    def train(self, tweet_tokens):
        # Separate hashtags and tokens
        hashtags = set()
        tokens = set()
        for token in tweet_tokens:
            if token[0] == '#' and len(token) > 1:
                hashtags.add(unicode(token[1:]).lower())
            else:
                tokens.add(unicode(token).lower())

        # Ensure tweet has some hashtags and some non-hashtag tokens
        if len(hashtags) == 0 or len(tokens) == 0:
            return

        with self.lock:
            for token in tokens:
                if token in self.fc:
                    for hashtag in hashtags:
                        self.fc[token][hashtag] = self.fc[token].get(hashtag, 0) + 1
                else:
                    self.fc[token] = dict.fromkeys(hashtags, 1)

                self.tc[token] = self.tc.get(token, 0) + 1

            for hashtag in hashtags:
                self.hashtag_total += 1
                self.cc[hashtag] = self.cc.get(hashtag, 0) + 1

            self.tweet_total += 1

    def fprob(self, token, hashtag):
        if token not in self.fc:
            return 0
        return self.fc[token].get(hashtag, 0) / self.cc[hashtag]

    def weightedprob(self, token, hashtag, weight=1.0, ap=0.5):
        fprob = self.fprob(token, hashtag)

        totals = self.tc[token]

        return ((weight * ap) + (totals * fprob)) / (weight + totals)

    def docprob(self, tokens, hashtag):
        p = 1
        for token in tokens:
            p *= self.weightedprob(token, hashtag)

        return p

    def prob(self, tokens, hashtag):
        catprob = self.catcount(hashtag) / self.totalcount()
        docprob = self.docprob(tokens, hashtag)
        return docprob * catprob

    def classify(self, tweet, results=None):
        # Twokenize tweet
        tweet_tokens = tokenize(tweet)

        # Filter out any existing hashtags
        tokens = set()
        for token in tweet_tokens:
            if token[0] != '#':
                tokens.add(unicode(token).lower())

        probs = {}

        for hashtag in self.hashtags():
            probs[hashtag] = self.prob(tokens, hashtag)

        return sorted(probs.iteritems(), key=lambda t: t[1], reverse=True)[:results]

    ################################################################################################
    # Getter/setter methods

    def fcount(self, token, hashtag):
        with self.lock:
            if token in self.fc and hashtag in self.fc[token]:
                return self.fc[token][hashtag]
            return 0

    def catcount(self, hashtag):
        with self.lock:
            if hashtag in self.cc:
                return self.cc[hashtag]
            return 0

    def totalcount(self):
        with self.lock:
            return self.hashtag_total

    def hashtags(self):
        with self.lock:
            return self.cc.keys()

    def get_model(self):
        with self.lock:
            return self.fc, self.cc, self.tweet_total

    def get_uptime(self):
        return datetime.now() - self.start_time

    ################################################################################################
    # State loading/dumping

    def state_dump(self, fileprefix):
        with open("{0}-{1}.pickle".format(fileprefix, time.strftime("%Y%m%d%H%M%S")), "wb") as f:
            with self.lock:
                pickle.dump(self.fc, f, pickle.HIGHEST_PROTOCOL)
                pickle.dump(self.cc, f, pickle.HIGHEST_PROTOCOL)
                pickle.dump(self.tc, f, pickle.HIGHEST_PROTOCOL)
                pickle.dump(self.tweet_total, f, pickle.HIGHEST_PROTOCOL)
                pickle.dump(self.hashtag_total, f, pickle.HIGHEST_PROTOCOL)

    def state_load(self, filename):
        with open(filename, "rb") as f:
            with self.lock:
                self.fc = pickle.load(f)
                self.cc = pickle.load(f)
                self.tc = pickle.load(f)
                self.tweet_total = pickle.load(f)
                self.hashtag_total = pickle.load(f)
