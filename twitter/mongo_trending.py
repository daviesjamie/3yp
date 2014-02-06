from twython import Twython
import pymongo
import sys

APP_KEY = 'R1zJdC7s4X4zWl9cyBtTuA'
APP_SECRET = 'Wq7AReVM5gGVG60V3t2hrdxr3BIhPlZgWN92o7ZtsmM'
ACCESS_TOKEN = '34354896-F96Omh8C9YX9wyKfFF9CfdP1tTSOJ09pezwkHIoGp'
ACCESS_TOKEN_SECRET = 'DKw7igfi0ncKDK6oIcCykrazBcwsZOAwzG8BKaKkrsq60'

t = Twython(app_key = APP_KEY,
            app_secret = APP_SECRET,
            oauth_token = ACCESS_TOKEN,
            oauth_token_secret = ACCESS_TOKEN_SECRET)

hashtagsFile = sys.argv[1] if len(sys.argv) > 1 else "hashtags.txt"
with open(hashtagsFile) as f:
    hashtags = f.read().splitlines()

numTweets = int(sys.argv[2]) if len(sys.argv) > 2 else 1000

conn = pymongo.MongoClient()
db = conn['tweets']

for hashtag in hashtags:
    print '#' + hashtag

    search = t.search(q=('#'+hashtag), count=numTweets, result_type=recent)
    tweets = search['statuses']

    print len(tweets)

    for tweet in tweets:
        db.trending.insert(tweet)
