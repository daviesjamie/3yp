__author__ = 'Jamie Davies'

import json
from tweepy import API, OAuthHandler


def get_api():
    """Uses the credentials in oauth.json to create and return an authenticated Tweepy API class."""

    try:
        oauth = json.loads(open("oauth.json", 'r').read())
        auth = OAuthHandler(oauth['app_key'], oauth['app_secret'])
        auth.set_access_token(oauth['access_token'], oauth['access_token_secret'])
        api = API(auth)

        if not api.verify_credentials():
            raise Exception("Invalid OAuth credentials")

    except:
        print "Error logging in to Twitter"
        raise

    return api