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
    def __init__(self, classifier, use_hashtag_text=False):
        self.classifier = classifier
        self.use_hashtag_text = use_hashtag_text

    def perform(self, obj):
        self.classifier.train(obj, self.use_hashtag_text)


class Classifier(object):
    """
    A naive bayes classifier that calculates the hashtag probabilities for any given tweet.

    To calculate the probabilities, the classifier builds and maintains several internal models of
    the tweet/hashtag data:

        - A count of the total number of times each hashtag has been seen
          { hashtag: count }

        - A count of the number of times each token appears with a given hashtag
          { hashtag: { token: count } }

        - A count of the total number of times each token has been seen
          { token: count }

        - A count of the number of times each hashtag appears with a given token
          { token: { hashtag: count } }

    Access to these models is internally protected with a mutex lock, to allow for safe
    simulatenous training and classification, or simultaneous training from different sources.
    """

    def __init__(self):
        """
        Initialises the internal models and counts, and creates the mutex lock.
        """
        self.hc = {}    # { hashtag: count }
        self.htc = {}   # { hashtag: { token: count } }
        self.tc = {}    # { token: count }
        self.thc = {}   # { token: { hashtag: count } }
        self.tweet_total = 0
        self.hashtag_total = 0
        self.start_time = datetime.now()

        self.lock = Lock()

    def train(self, tweet_tokens, use_hashtag_text=False):
        """
        Takes in an iterable collection of tokens (from a tokenised tweet), and uses it to update
        the classifier's internal probability models.
        """
        # Separate hashtags and tokens
        hashtags = set()
        tokens = set()
        for token in tweet_tokens:
            if token[0] == '#' and len(token) > 1:
                hashtags.add(unicode(token[1:]).lower())
                if use_hashtag_text:
                    tokens.add(unicode(token[1:]).lower())
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
        """
        Takes in a string representing the entire text of a tweet, and uses the internal models
        to calculate the probability of that tweet belonging every 'seen' hashtag.

        If results is none, ALL hashtags and their associated probabilities will be returned.
        Otherwise, if results in an int, then that number of hashtags with the highest
        probabilities with be returned.
        """
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
        """
        Returns the total number of times that a hashtag has been seen.
        """
        with self.lock:
            if hashtag in self.hc:
                return self.hc[hashtag]
            return 0

    def _docprob(self, tokens, hashtag):
        """
        Accumulates the weighted probabilities of tokens belonging to a hashtag.
        """
        p = 1
        for token in tokens:
            p *= self._weightedprob(token, hashtag)
        return p

    def _fcount(self, token, hashtag):
        """
        Returns the number of times that a hashtag has appeared with a given token.
        """
        with self.lock:
            if token in self.thc and hashtag in self.thc[token]:
                return self.thc[token][hashtag]
            return 0

    def _fprob(self, token, hashtag):
        """
        Calculates the probability of a token belonging to a hashtag.
        """
        if token not in self.thc:
            return 0
        return self.thc[token].get(hashtag, 0) / self.hc[hashtag]

    def _hashtags(self):
        """
        Returns a list of all hashtags 'seen' by the classifier.
        """
        with self.lock:
            return self.hc.keys()

    def _prob(self, tokens, hashtag):
        """
        The heart of the classifier. Uses Bayes Theorem to calculate the probability of a hashtag
        applying to a set of tokens:

                                  P(Tokens|Hashtag) * P(Hashtag)
            P(Hashtag|Tokens) = ----------------------------------
                                           P(Tokens)

        which is optimised simply to:

            P(Hashtag|Tokens) =  P(Tokens|Hashtag) * P(Hashtag)
        """
        docprob = self._docprob(tokens, hashtag)
        catprob = self._catcount(hashtag) / self._totalcount()
        return docprob * catprob

    def _totalcount(self):
        """
        Returns the total number of hashtags 'seen' by the classifier.
        """
        with self.lock:
            return self.hashtag_total

    def _weightedprob(self, token, hashtag, weight=1.0, ap=0.5):
        """
        Calculates a weighted version of _fprob() to make the classification probabilities less
        sensitive/extreme when tokens/hashtags have only been seen a small number of times.

        The weighting is applied by multiplying _fprob() with an assumed probability (ap) with a
        token weight (i.e., a weight of 2 makes the assumed probability equal to 2 tokens).
        """
        fprob = self._fprob(token, hashtag)
        totals = self.tc.get(token, 0)
        return ((weight * ap) + (totals * fprob)) / (weight + totals)


    ################################################################################################
    # Getter methods

    def get_hashtags(self, num=None):
        """
        If num is specified, returns the top num 'seen' hashtags and their counts.
        If num isn't specified, returns a list of ALL 'seen' hashtags and their counts.
        """
        with self.lock:
            if num:
                return sorted(self.hc.iteritems(), key=lambda t: t[1], reverse=True)[:num]
            return self.hc

    def get_hashtag_tokens(self, hashtag, num=None):
        """
        Returns a list of the top num tokens and their counts that occur with a given hashtag. If
        num is none, returns ALL tokens and their counts for that hashtag.
        """
        if num:
            return sorted(self.htc[hashtag].iteritems(), key=lambda t: t[1], reverse=True)[:num]
        return self.htc[hashtag]

    def get_memory_usage(self):
        """
        Returns the sizes (in bytes) of the four main models that the classifier keeps in memory.
        """
        return asizeof.asizeof(self.hc), asizeof.asizeof(self.htc), asizeof.asizeof(self.tc), \
               asizeof.asizeof(self.thc)

    def get_tokens(self, num=None):
        """
        If num is specified, returns the top num 'seen' tokens and their counts.
        If num isn't specified, returns a list of ALL 'seen' tokens and their counts.
        """
        with self.lock:
            if num:
                return sorted(self.tc.iteritems(), key=lambda t: t[1], reverse=True)[:num]
            return self.tc

    def get_token_hashtags(self, token, num=None):
        """
        Returns a list of the top num hashtags and their counts that occur with a given token. If
        num is none, returns ALL hashtags and their counts for that token.
        """
        if num:
            return sorted(self.thc[token].iteritems(), key=lambda t: t[1], reverse=True)[:num]
        return self.thc[token]

    def get_totals(self):
        """
        Returns the total number of tweets and hashtags that this classifier has been trained with.
        Note that this is not the same as the total number of unique hashtags!
        """
        return self.tweet_total, self.hashtag_total

    def get_unique_counts(self):
        """
        Returns a tuple containing both the total number of unique 'seen' tokens and the total
        number of unique 'seen' hashtags.
        """
        with self.lock:
            return len(self.hc.keys()), len(self.tc.keys())

    def get_uptime(self):
        """
        Returns a datetime.timedelta object that represents how long the classifier has been
        running.
        """
        return datetime.now() - self.start_time


    ################################################################################################
    # State loading/dumping

    def state_dump(self, fileprefix):
        """
        Serialises the classifiers internal state and models and outputs it to a file, so that it
        can be reloaded in the future.
        """
        with open("{0}-{1}.pickle".format(fileprefix, time.strftime("%Y%m%d%H%M%S")), "wb") as f:
            with self.lock:
                pickle.dump(self.hc, f, pickle.HIGHEST_PROTOCOL)
                pickle.dump(self.htc, f, pickle.HIGHEST_PROTOCOL)
                pickle.dump(self.tc, f, pickle.HIGHEST_PROTOCOL)
                pickle.dump(self.thc, f, pickle.HIGHEST_PROTOCOL)
                pickle.dump(self.tweet_total, f, pickle.HIGHEST_PROTOCOL)
                pickle.dump(self.hashtag_total, f, pickle.HIGHEST_PROTOCOL)

    def state_load(self, filename):
        """
        Loads the data from a serialised state dump generated from state_dump().
        CAUTION: Overwrites any existing data stored in the classifier's internal variables.
        """
        with open(filename, "rb") as f:
            with self.lock:
                self.hc = pickle.load(f)
                self.htc = pickle.load(f)
                self.tc = pickle.load(f)
                self.thc = pickle.load(f)
                self.tweet_total = pickle.load(f)
                self.hashtag_total = pickle.load(f)
                print "State sucessfully loaded from " + filename
