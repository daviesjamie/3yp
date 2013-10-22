#!/usr/bin/python

from twython import TwythonStreamer
import csv
import sys

APP_KEY = 'R1zJdC7s4X4zWl9cyBtTuA'
APP_SECRET = 'Wq7AReVM5gGVG60V3t2hrdxr3BIhPlZgWN92o7ZtsmM'
ACCESS_TOKEN = '34354896-F96Omh8C9YX9wyKfFF9CfdP1tTSOJ09pezwkHIoGp'
ACCESS_TOKEN_SECRET = 'DKw7igfi0ncKDK6oIcCykrazBcwsZOAwzG8BKaKkrsq60'

class MyStreamer(TwythonStreamer):
    def initialise(self, filename, numTweets):
        self.output = open(filename, 'ab+')
        self.wr = csv.writer(self.output, dialect='excel')
        self.wr.writerow(['id','lang','userid','username','timestamp','text','retweeted','source','sensitive','geo'])

        self.numTweets = numTweets
        self.tweetCount = 0

    def on_success(self, data):
        if 'text' in data:
            tweet = []

            tweet.append(data['id'])
            tweet.append(data['user']['id'])
            tweet.append(data['lang'])
            tweet.append(data['text'].encode('utf-8'))
            tweet.append(data['created_at'])
            
            self.wr.writerow(tweet)
            self.tweetCount += 1

            if self.tweetCount > self.numTweets:
                self.output.close()
                self.disconnect()
                print 'Done!'
            else:
                print self.tweetCount

stream = MyStreamer(APP_KEY, APP_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
stream.initialise('tweets.csv', 1000)
stream.statuses.sample()

