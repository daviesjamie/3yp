import string
from rfc3987 import match
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
    def __init__(self, stop_words=False, punctuation=False, usernames=False, urls=False):
        self.stop_words = stop_words
        self.punctuation = punctuation
        self.usernames = usernames
        self.urls = urls

        if not self.stop_words:
            self.stop_word_list = _get_stop_words()

        if not self.punctuation:
            self.punctuation_map = dict((ord(char), None) for char in string.punctuation)

    def apply(self, input):
        tokens = tokenize(input)

        if not self.stop_words:
            tokens = [t for t in tokens if t not in self.stop_word_list]

        if not self.punctuation:
            tokens = [t for t in tokens if t.translate(self.punctuation_map)]

        if not self.usernames:
            tokens = [t for t in tokens if not t.startswith('@')]

        if not self.urls:
            tokens = [t for t in tokens if not match(t, rule='IRI')]

        return tokens


class TokeniseTweetFunction(TokeniseTextFunction):
    """
    Takes in a tweet JSON object and tokenises the tweet text using Brendan O'Connor's
    "twokenizer".
    """
    def __init__(self, stop_words=False, punctuation=False, usernames=False, urls=False):
        super(TokeniseTweetFunction, self) \
            .__init__(stop_words=stop_words, punctuation=punctuation, usernames=usernames, urls=urls)

    def apply(self, input):
        return super(TokeniseTweetFunction, self).apply(input['text'])
