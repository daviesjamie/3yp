import sys
from twython import TwythonStreamer
from utils import credentials
import json
import time


class Streamer(TwythonStreamer):

    def __init__(self, app_key, app_secret, access_token, access_token_secret, limit=100):
        self.limit = limit
        self.counter = 0
        self.fname = 'tweets_' + time.strftime('%Y%m%d-%H%M%S') + '.json'
        self.output = open(self.fname, 'w')
        self.delout = open('delete.txt', 'a')

        super(Streamer, self).__init__(app_key, app_secret, access_token, access_token_secret)

    def on_success(self, data):
        """Decides how to handle the tweet."""

        if 'text' in data:
            self.on_status(data)

        elif 'delete' in data:
            delete = data['delete']['status']
            if self.on_delete(delete['id'], delete['user_id']) is False:
                return False

        elif 'limit' in data:
            if self.on_limit(data['limit']['track']) is False:
                return False

        elif 'warning' in data:
            warning = data['warnings']
            print warning['message']
            return False

    def on_status(self, data, verbose=True):
        json_data = json.dumps(data)
        self.output.write(json_data + "\n")
        self.counter += 1

        if verbose:
            print self.counter

        if self.counter >= self.limit:
            self.output.close()
            self.disconnect()

        return

    def on_delete(self, status_id, user_id):
        self.delout.write(str(status_id) + "\n")
        return

    def on_limit(self, track):
        sys.stderr.write(track + "\n")
        return

    def on_error(self, status_code, data):
        sys.stderr.write("Error: " + str(status_code) + "\n")
        return False

    def on_timeout(self):
        sys.stderr.write("Timeout, sleeping for 60 seconds...\n")
        time.sleep(60)
        return


if __name__ == '__main__':
    stream = Streamer(*credentials("oauth.json"))
    stream.statuses.sample()