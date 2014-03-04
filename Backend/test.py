from filters import TweetsWithHashtagsPredicate, TweetsInEnglishPredicate
from input import TweetStream
from output import PrintTweetOperation
from structures import QueueBufferedQueue
from utils import credentials

twitter = TweetStream(QueueBufferedQueue(3), *credentials('oauth.json'))
twitter.connect()

twitter \
    .filter(TweetsWithHashtagsPredicate()) \
    .filter(TweetsInEnglishPredicate()) \
    .for_each(PrintTweetOperation(), 10)

twitter.disconnect()
