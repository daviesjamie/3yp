import json
from structures import Operation


class PrintTweetOperation(Operation):
    """
    Simple operation to print the text of a tweet.
    """
    def perform(self, obj):
        print obj['text']


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
