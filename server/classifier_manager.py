from multiprocessing.managers import BaseManager
from spout.sources import TweetStream
from spout.queues import QueueBufferedQueue
from classifier import Classifier, TrainOperation
from filters import TweetsWithHashtagsPredicate, TweetsInEnglishPredicate, NoRetweetsPredicate
from oauth import credentials
from tokeniser import TokeniseTweetFunction

class _ClassifierManager(BaseManager):
    pass

def get_classifier():
    _ClassifierManager.register('Classifier', Classifier, exposed=['train',
                                                                   'classify',
                                                                   'get_hashtags',
                                                                   'get_hashtag_tokens',
                                                                   'get_memory_usage',
                                                                   'get_tokens',
                                                                   'get_token_hashtags',
                                                                   'get_totals',
                                                                   'get_unique_counts',
                                                                   'get_uptime',
                                                                   'state_dump',
                                                                   'state_load'])

    mymanager = _ClassifierManager()
    mymanager.start()

    return mymanager.Classifier()

def train_classifier(classifier):
    twitter = TweetStream(QueueBufferedQueue(3), *credentials('oauth.json'))
    twitter.connect()

    twitter \
        .filter(TweetsWithHashtagsPredicate()) \
        .filter(TweetsInEnglishPredicate()) \
        .filter(NoRetweetsPredicate()) \
        .map(TokeniseTweetFunction(stop_tokens=True, punctuation=False, usernames=False, urls=False)) \
        .for_each(TrainOperation(classifier))

def dump_classifier(classifier):
    classifier.state_dump('state')
