import json
from structures import Operation, Predicate


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


class TruePredicate(Predicate):
    """
    Simple predicate that always returns True. Used for testing purposes only.
    """
    def test(self, obj):
        return True


class NullOperation(Operation):
    """
    An empty operation that does nothing, it is simply used to pull objects through the stream.
    Used for testing purposes only.
    """
    def perform(self, obj):
        pass
