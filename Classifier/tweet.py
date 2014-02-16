__author__ = 'Jamie Davies'

import auth
import sys


def tweet(api, status):
    """Uses an authenticated Tweepy API object to post a tweet."""

    if len(status) <= 140 :
        api.update_status(status)
    else:
        sys.stderr.write("Tweet is too long!\n")


if __name__ == '__main__':
    tweet(auth.get_api(), sys.argv[1])