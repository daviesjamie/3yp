from twython import TwythonStreamer
import csv
import sys

APP_KEY = 'R1zJdC7s4X4zWl9cyBtTuA'
APP_SECRET = 'Wq7AReVM5gGVG60V3t2hrdxr3BIhPlZgWN92o7ZtsmM'
ACCESS_TOKEN = '34354896-F96Omh8C9YX9wyKfFF9CfdP1tTSOJ09pezwkHIoGp'
ACCESS_TOKEN_SECRET = 'DKw7igfi0ncKDK6oIcCykrazBcwsZOAwzG8BKaKkrsq60'

class MyStreamer(TwythonStreamer):
   def on_success(self, data):
       if 'text' in data and data['lang'] == 'en' and data['entities']['hashtags']:
            for hashtag in data['entities']['hashtags']:
               print '#%s ' % (hashtag['text']),
            print '\n'

stream = MyStreamer(APP_KEY, APP_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
stream.statuses.sample()
