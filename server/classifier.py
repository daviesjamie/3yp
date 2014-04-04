from __future__ import division
from multiprocessing import Lock
from datetime import datetime
from spout.structs import Function, Operation
import time
from twokenize.twokenize import tokenize
import cPickle as pickle
from pympler import asizeof


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
        self.hc = {}    # { hashtag: count }
        self.htc = {}   # { hashtag: { token: count } }
        self.tc = {}    # { token: count }
        self.thc = {}   # { token: { hashtag: count } }
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
                if token in self.thc:
                    for hashtag in hashtags:
                        self.thc[token][hashtag] = self.thc[token].get(hashtag, 0) + 1
                else:
                    self.thc[token] = dict.fromkeys(hashtags, 1)

                self.tc[token] = self.tc.get(token, 0) + 1

            for hashtag in hashtags:
                if hashtag in self.htc:
                    for token in tokens:
                        self.htc[hashtag][token] = self.htc[hashtag].get(token, 0) + 1
                else:
                    self.htc[hashtag] = dict.fromkeys(tokens, 1)

                self.hc[hashtag] = self.hc.get(hashtag, 0) + 1
                self.hashtag_total += 1

            self.tweet_total += 1

    def classify(self, tweet, results=None):
        # Twokenize tweet
        tweet_tokens = tokenize(tweet)

        # Filter out any existing hashtags
        tokens = set()
        for token in tweet_tokens:
            if token[0] != '#':
                tokens.add(unicode(token).lower())

        probs = {}

        for hashtag in self._hashtags():
            probs[hashtag] = self._prob(tokens, hashtag)

        return sorted(probs.iteritems(), key=lambda t: t[1], reverse=True)[:results]


    ################################################################################################
    # Classification helper methods

    def _catcount(self, hashtag):
        with self.lock:
            if hashtag in self.hc:
                return self.hc[hashtag]
            return 0

    def _docprob(self, tokens, hashtag):
        p = 1
        for token in tokens:
            p *= self._weightedprob(token, hashtag)
        return p

    def _fcount(self, token, hashtag):
        with self.lock:
            if token in self.thc and hashtag in self.thc[token]:
                return self.thc[token][hashtag]
            return 0

    def _fprob(self, token, hashtag):
        if token not in self.thc:
            return 0
        return self.thc[token].get(hashtag, 0) / self.hc[hashtag]

    def _hashtags(self):
        with self.lock:
            return self.hc.keys()

    def _prob(self, tokens, hashtag):
        docprob = self._docprob(tokens, hashtag)
        catprob = self._catcount(hashtag) / self._totalcount()
        return docprob * catprob

    def _totalcount(self):
        with self.lock:
            return self.hashtag_total

    def _weightedprob(self, token, hashtag, weight=1.0, ap=0.5):
        fprob = self._fprob(token, hashtag)
        totals = self.tc.get(token, 0)
        return ((weight * ap) + (totals * fprob)) / (weight + totals)


    ################################################################################################
    # Getter methods

    def get_cc(self, num=None):
        with self.lock:
            if num:
                return sorted(self.cc.iteritems(), key=lambda t: t[1], reverse=True)[:num]
            return self.cc

    def get_counts(self):
        with self.lock:
            return len(self.fc.keys()), len(self.cc.keys())

    def get_hashtag_tokens(self, hashtag, num=None):
        if num:
            return sorted(self.ct[hashtag].iteritems(), key=lambda t: t[1], reverse=True)[:num]
        return self.ct[hashtag]

    def get_memory_usage(self):
        return asizeof.asizeof(self.fc), asizeof.asizeof(self.cc), asizeof.asizeof(self.tc)

    def get_tc(self, num=None):
        with self.lock:
            if num:
                return sorted(self.tc.iteritems(), key=lambda t: t[1], reverse=True)[:num]
            return self.tc

    def get_token_hashtags(self, token, num=None):
        if num:
            return sorted(self.fc[token].iteritems(), key=lambda t: t[1], reverse=True)[:num]
        return self.fc[token]

    def get_totals(self):
        return self.tweet_total, self.hashtag_total

    def get_uptime(self):
        return datetime.now() - self.start_time


    ################################################################################################
    # State loading/dumping

    def state_dump(self, fileprefix):
        with open("{0}-{1}.pickle".format(fileprefix, time.strftime("%Y%m%d%H%M%S")), "wb") as f:
            with self.lock:
                pickle.dump(self.hc, f, pickle.HIGHEST_PROTOCOL)
                pickle.dump(self.htc, f, pickle.HIGHEST_PROTOCOL)
                pickle.dump(self.tc, f, pickle.HIGHEST_PROTOCOL)
                pickle.dump(self.thc, f, pickle.HIGHEST_PROTOCOL)
                pickle.dump(self.tweet_total, f, pickle.HIGHEST_PROTOCOL)
                pickle.dump(self.hashtag_total, f, pickle.HIGHEST_PROTOCOL)

    def state_load(self, filename):
        with open(filename, "rb") as f:
            with self.lock:
                self.hc = pickle.load(f)
                self.htc = pickle.load(f)
                self.tc = pickle.load(f)
                self.thc = pickle.load(f)
                self.tweet_total = pickle.load(f)
                self.hashtag_total = pickle.load(f)
                print "State sucessfully loaded from " + filename
