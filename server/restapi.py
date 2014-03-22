from multiprocessing import Process
from multiprocessing.managers import BaseManager
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
from apscheduler.scheduler import Scheduler

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
                                                              'hashtags'])

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

import logging
logging.basicConfig()

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
        return classifier.classify(args['text'], args['results']), 201


class StatusAPI(Resource):
    def get(self):
        token_count = classifier.get_token_count()
        hashtag_count = classifier.get_hashtag_count()
        model = classifier.get_model()

        return {
            "training": {
                "tweet_total": classifier.get_tweet_total(),
                "token_total": classifier.get_token_total(),
                "hashtag_total": classifier.get_hashtag_total(),
                "unique_tokens": len(token_count),
                "unique_hashtags": len(hashtag_count)
            },
            "memory": {
                "token_count_kb": asizeof.asizeof(token_count) / float(1024),
                "hashtag_count_kb": asizeof.asizeof(hashtag_count) / float(1024),
                "model_kb": asizeof.asizeof(model) / float(1024),
                "token_count_mb": asizeof.asizeof(token_count) / float(1024) / float(1024),
                "hashtag_count_mb": asizeof.asizeof(hashtag_count) / float(1024) / float(1024),
                "model_mb": asizeof.asizeof(model) / float(1024) / float(1024),
            }
        }


api.add_resource(ClassificationAPI, '/api/classify')
api.add_resource(StatusAPI, '/api/status')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        classifier.state_load(sys.argv[1])
    else:
        trainer.start()

    app.run(debug=True)
