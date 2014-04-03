from spout.structs import Function
from twokenize.twokenize import tokenize

stop_word_file = "stopwords.txt"


def _get_stop_words():
    with open(stop_word_file, 'r') as f:
        words = f.read().splitlines()

    return set(words)


class TokeniseTextFunction(Function):
    """
    Takes in a plain text string and tokenises it using Brendan O'Connor's "twokenizer".
    """
    def __init__(self):
        self.stop_words = _get_stop_words()

    def apply(self, input):
        twokens = tokenize(input)
        tokens = [t.lower() for t in twokens if t.lower() not in self.stop_words]
        return tokens


class TokeniseTweetFunction(TokeniseTextFunction):
    """
    Takes in a tweet JSON object and tokenises the tweet text using Brendan O'Connor's
    "twokenizer".
    """
    def __init__(self):
        super(TokeniseTweetFunction, self).__init__()

    def apply(self, input):
        return super(TokeniseTweetFunction, self).apply(input['text'])
