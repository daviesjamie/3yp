from functions import TokenizeTweetFunction
from operations import PrintTweetOperation, PrintOperation
from predicates import TweetsWithHashtagsPredicate, TweetsInEnglishPredicate, TruePredicate
from twitter import TweetStream
from utils import credentials
from structures import QueueBufferedQueue

twitter = TweetStream(QueueBufferedQueue(3), *credentials('oauth.json'))
twitter.connect()

twitter \
    .filter(TweetsWithHashtagsPredicate()) \
    .filter(TruePredicate()) \
    .for_each(PrintTweetOperation(), 10)

twitter.disconnect()
