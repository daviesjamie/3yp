import json
import time
import sys
from twython import Twython, TwythonError
from utils import credentials

class Searcher:

    def __init__(self, app_key, app_secret, access_token, access_token_secret, limit=100):
        self.api = Twython(app_key, app_secret, access_token, access_token_secret)
        self.limit = limit

    def capture(self, query, verbose=True):
        try:
            tweets = self.api.search(q=query, count=self.limit)
        except TwythonError as e:
            sys.stderr.write(e)
            return False

        out_file = 'tweets_' + query + "_" + time.strftime('%Y%m%d-%H%M%S') + '.json'
        with open(out_file, 'w') as f:
            json.dump(tweets['statuses'], f)

        if verbose:
            print str(self.limit) + " tweets written to " + out_file


if __name__ == '__main__':
    searcher = Searcher(*credentials('oauth.json'), limit=10)
    if len(sys.argv) > 1:
        searcher.capture(sys.argv[1])
    else:
        searcher.capture('#BAFTAs')