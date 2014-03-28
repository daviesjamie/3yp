from multiprocessing import Process
from multiprocessing.managers import BaseManager
from apscheduler.scheduler import Scheduler
from flask import Flask
from flask.ext.restful import Resource, Api, reqparse
from pympler import asizeof
from spout.queues import QueueBufferedQueue
from spout.sources import TweetStream
import sys
from classifier import Classifier, TrainOperation
from filters import TweetsWithHashtagsPredicate, TweetsInEnglishPredicate, NoRetweetsPredicate
from oauth import credentials
from tokeniser import TokeniseTweetFunction

class ClassifierManager(BaseManager):
    pass

ClassifierManager.register('Classifier', Classifier, exposed=['train',
                                                              'classify',
                                                              'state_dump',
                                                              'state_load',
                                                              'fprob',
                                                              'weightedprob',
                                                              'docprob',
                                                              'prob',
                                                              'fcount',
                                                              'catcount',
                                                              'totalcount',
                                                              'hashtags',
                                                              'get_counts',
                                                              'get_totals',
                                                              'get_uptime',
                                                              'get_memory_usage'])

mymanager = ClassifierManager()
mymanager.start()

classifier = mymanager.Classifier()

def _train_classifier():
    twitter = TweetStream(QueueBufferedQueue(3), *credentials('oauth.json'))
    twitter.connect()

    twitter \
        .filter(TweetsWithHashtagsPredicate()) \
        .filter(TweetsInEnglishPredicate()) \
        .filter(NoRetweetsPredicate()) \
        .map(TokeniseTweetFunction()) \
        .for_each(TrainOperation(classifier))

def _dump_classifier():
    classifier.state_dump('state')

trainer = Process(target=_train_classifier)

sched = Scheduler()
sched.start()
sched.add_interval_job(_dump_classifier, hours=1)

app = Flask(__name__)
api = Api(app)


class ClassificationAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('text', type=str, required=True, help='No text to classify was provided', location='json')
        self.reqparse.add_argument('results', type=int, required=False, default=5, location='json')
        super(ClassificationAPI, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        return classifier.classify(args['text'], results=args['results']), 201


class StatusAPI(Resource):
    def get(self):
        fc, cc = classifier.get_counts()
        tweet_total, hashtag_total = classifier.get_totals()
        uptime = classifier.get_uptime()
        fm, cm, tm = classifier.get_memory_usage()

        return {
            "training": {
                "tweet_total": tweet_total,
                "hashtag_total": hashtag_total,
                "unique_tokens": fc,
                "unique_hashtags": cc,
            },
            "memory": {
                "fc_kb": fm / float(1024),
                "cc_kb": cm / float(1024),
                "tc_kb": tm / float(1024),
                "fc_mb": fm / float(1048576),
                "cc_mb": cm / float(1048576),
                "tc_mb": tm / float(1048576),
            },
            "uptime":{
                "days": uptime.days,
                "hours": int(uptime.total_seconds() / 3600) % 24,
                "minutes": int((uptime.total_seconds() % 3600) / 60),
                "seconds": int(uptime.total_seconds() % 60),
            },
        }


api.add_resource(ClassificationAPI, '/api/classify')
api.add_resource(StatusAPI, '/api/status')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        classifier.state_load(sys.argv[1])
    else:
        trainer.start()

    app.run(debug=True)
