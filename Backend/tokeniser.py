from spout.structs import Function
from twokenize.twokenize import tokenize


class TokenizeTweetFunction(Function):
    """
    Takes in a tweet JSON object and tokenizes the tweet text using Brendan O'Connor's
    "twokenizer".
    """
    def apply(self, input):
        return tokenize(input['text'])
