from multiprocessing import Process
import sys
from twython import TwythonStreamer
from stream import BufferedStream


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