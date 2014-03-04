import json
from multiprocessing import Process
import sys
from twython import TwythonStreamer
from stream import BufferedStream, AbstractStream


class TweetStream(BufferedStream):
    def __init__(self, buf, app_key, app_secret, access_token, access_token_secret):
        super(TweetStream, self).__init__(buf)
        self.source = self.TweetSource(self, app_key, app_secret, access_token,
                                       access_token_secret)
        self.worker = Process(target=self.source.statuses.sample)
        self.worker.daemon = True

    def connect(self):
        super(TweetStream, self).connect()
        self.worker.start()

    def disconnect(self):
        super(TweetStream, self).disconnect()

        self.source.disconnect()
        self.worker.terminate()

    class TweetSource(TwythonStreamer):
        def __init__(self, publish_stream, app_key, app_secret, access_token, access_token_secret):
            super(TweetStream.TweetSource, self).__init__(app_key, app_secret, access_token,
                                                          access_token_secret)
            self.publish_stream = publish_stream

        def on_success(self, data):
            if 'text' in data:
                self.publish_stream.register(data)

        def on_error(self, status_code, data):
            sys.stderr.write(status_code, data)


class JSONInputStream(AbstractStream):
    """
    Loads a file containing a separate JSON object on each line into a stream for processing.
    """

    def __init__(self, filename):
        self.input = open(filename, 'r')
        self.next_line = None

    def has_next(self):
        if self.next_line is not None:
            return True

        try:
            self.next_line = self.input.next()
        except StopIteration:
            self.next_line = None

        return self.next_line is not None

    def next(self):
        if not self.has_next():
            raise Exception("Iteration has no more elements")

        to_return = json.loads(self.next_line)
        self.next_line = None

        return to_return
