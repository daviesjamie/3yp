import json
from structures import Operation, Function
from twokenize import tokenize


class PrintTweetOperation(Operation):
    """
    Simple operation to print the text of a tweet.
    """
    def perform(self, obj):
        print obj['text']


class TokenizeTweetMapping(Function):
    """
    Takes in a tweet JSON object and tokenizes the tweet text using Brendan O'Connor's
    "twokenizer".
    """
    def apply(self, input):
        return tokenize(input['text'])


class PrintOperation(Operation):
    """
    Simple operation to print whatever input is supplied. Used for testing purposes only.
    """
    def perform(self, obj):
        print obj


class NullOperation(Operation):
    """
    An empty operation that does nothing, it is simply used to pull objects through the stream.
    Used for testing purposes only.
    """
    def perform(self, obj):
        pass

def _load_credentials(cred_file):
    with open(cred_file) as f:
        creds = json.load(f)
    return creds


def credentials(cred_file):
    """
    Fetches OAuth credentials from a JSON file.
    """

    creds = _load_credentials(cred_file)
    app_key = creds['APP_KEY']
    app_secret = creds['APP_SECRET']
    access_token = creds['ACCESS_TOKEN']
    access_token_secret = creds['ACCESS_TOKEN_SECRET']

    return app_key, app_secret, access_token, access_token_secret
