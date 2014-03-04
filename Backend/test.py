from classifier import TrainClassifierOperation, TokenizeTweetFunction
from filters import TweetsWithHashtagsPredicate, TweetsInEnglishPredicate
from input import TweetStream, JSONInputStream
from output import PrintTweetOperation
from structures import QueueBufferedQueue
from utils import credentials

classifier = TrainClassifierOperation()

# twitter = TweetStream(QueueBufferedQueue(3), *credentials('oauth.json'))
# twitter.connect()

# twitter \
#     .filter(TweetsWithHashtagsPredicate()) \
#     .filter(TweetsInEnglishPredicate()) \
#     .map(TokenizeTweetFunction()) \
#     .for_each(classifier, 10)
#
# twitter.disconnect()

f = JSONInputStream('tweets.json')

f \
    .map(TokenizeTweetFunction()) \
    .for_each(classifier)


import pprint
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(classifier.fc)
