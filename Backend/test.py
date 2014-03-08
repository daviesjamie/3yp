from classifier import Classifier, TokenizeTweetFunction
from input import JSONInputStream

classifier = Classifier()

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
    .for_each(Classifier.TrainOperation(classifier))

classifier.print_model()
classifier.print_counts()
