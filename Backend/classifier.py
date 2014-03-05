import pprint
from structures import Function, Operation
from twokenize import tokenize


class TokenizeTweetFunction(Function):
    """
    Takes in a tweet JSON object and tokenizes the tweet text using Brendan O'Connor's
    "twokenizer".
    """
    def apply(self, input):
        return tokenize(input['text'])


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
        self.count = 0

    def print_model(self):
        pprint.pprint(self.fc)

    class TrainOperation(Operation):
        """
        Takes in a stream of tokenized tweets and builds a dictionary keeping track of how many times
        each non-hashtag token is associated with a hashtag.
        """
        def __init__(self, classifier):
            self.classifier = classifier

        def perform(self, obj):
            # Separate hashtags and tokens
            hashtags = set()
            tokens = set()
            for token in obj:
                if token[0] == '#':
                    hashtags.add(unicode(token[1:]).lower())
                else:
                    tokens.add(unicode(token).lower())

            if len(hashtags) == 0:
                return

            for token in tokens:
                if token in self.classifier.fc:
                    for hashtag in hashtags:
                        self.classifier.fc[token][hashtag] = self.classifier.fc[token].get(
                            hashtag, 0) + 1
                else:
                    self.classifier.fc[token] = dict.fromkeys(hashtags, 1)

