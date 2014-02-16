__author__ = 'Jamie Davies'

import sys


def tweet(api, status):
    """Uses an authenticated Tweepy API object to post a tweet."""

    if(len(status) <= 140):
        api.update_status(status)
    else:
        sys.stderr.write("Tweet is too long!\n")