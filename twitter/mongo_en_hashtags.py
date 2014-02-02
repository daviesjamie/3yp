from twython import TwythonStreamer
import json
import pymongo
import sys

APP_KEY = 'R1zJdC7s4X4zWl9cyBtTuA'
APP_SECRET = 'Wq7AReVM5gGVG60V3t2hrdxr3BIhPlZgWN92o7ZtsmM'
ACCESS_TOKEN = '34354896-F96Omh8C9YX9wyKfFF9CfdP1tTSOJ09pezwkHIoGp'
ACCESS_TOKEN_SECRET = 'DKw7igfi0ncKDK6oIcCykrazBcwsZOAwzG8BKaKkrsq60'

class MyStreamer(TwythonStreamer):
    def initialise(self, numTweets):
        self.conn = pymongo.MongoClient()
        self.db = self.conn['tweets']

        self.numTweets = numTweets
        self.tweetCount = 0

    def on_success(self, data):
        if 'text' in data and data['lang'] == 'en' and data['entities']['hashtags']:
            self.db.testset.insert(data)

            self.tweetCount += 1

            if self.tweetCount > self.numTweets:
                self.disconnect()
                print 'Done!'
            else:
                print self.tweetCount

numTweets = int(sys.argv[1]) if len(sys.argv) > 1 else 1000

stream = MyStreamer(APP_KEY, APP_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
stream.initialise(numTweets)
stream.statuses.sample()
