import string
import os
import re
from spout.structs import Function
from twokenize.twokenize import tokenize

def _get_stop_tokens(file):
    stop_token_file = os.path.join(os.path.dirname(__file__), file)

    with open(stop_token_file, 'r') as f:
        words = f.read().splitlines()

    return set(words)


class TokeniseTextFunction(Function):
    """
    Takes in a plain text string and tokenises it using Brendan O'Connor's "twokenizer".
    """
    def __init__(self, stop_tokens=False, punctuation=False, usernames=False, urls=False):
        self.stop_tokens = stop_tokens
        self.punctuation = punctuation
        self.usernames = usernames
        self.urls = urls

        if self.stop_tokens:
            self.stop_token_list = _get_stop_tokens("stoptokens.txt")

        if self.punctuation:
            self.punctuation_map = dict((ord(char), None) for char in string.punctuation)

        if self.urls:
            self.url_regex = re.compile(r'(?:(?:https?:\/\/)|(?:www\.))[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b(?:[-a-zA-Z0-9@:%_\+.~#?&/=]*)')

    def apply(self, input):
        tokens = tokenize(input.lower())


        if self.punctuation:
            tokens = [t for t in tokens if t.translate(self.punctuation_map)]
        if self.stop_tokens:
            tokens = [t for t in tokens if t not in self.stop_token_list]

        if self.usernames:
            tokens = [t for t in tokens if not t.startswith('@')]

        if self.urls:
            tokens = [t for t in tokens if not re.match(self.url_regex, t)]

        return tokens


class TokeniseTweetFunction(TokeniseTextFunction):
    """
    Takes in a tweet JSON object and tokenises the tweet text using Brendan O'Connor's
    "twokenizer".
    """
    def __init__(self, stop_tokens=False, punctuation=False, usernames=False, urls=False):
        super(TokeniseTweetFunction, self) \
            .__init__(stop_tokens=stop_tokens, punctuation=punctuation, usernames=usernames,
                      urls=urls)

    def apply(self, input):
        return super(TokeniseTweetFunction, self).apply(input['text'])
