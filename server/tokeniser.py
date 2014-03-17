from spout.structs import Function
from twokenize.twokenize import tokenize


class TokeniseTweetFunction(Function):
    """
    Takes in a tweet JSON object and tokenises the tweet text using Brendan O'Connor's
    "twokenizer".
    """
    def apply(self, input):
        return tokenize(input['text'])


class TokeniseTextFunction(Function):
    """
    Takes in a plain text string and tokenises it using Brendan O'Connor's "twokenizer".
    """
    def apply(self, input):
        return tokenize(input)
