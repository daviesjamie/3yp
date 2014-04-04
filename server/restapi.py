from multiprocessing import Process
import sys

from apscheduler.scheduler import Scheduler
from flask import Flask
from flask.ext.restful import Resource, Api, reqparse

from classifier_manager import get_classifier, train_classifier, dump_classifier


app = Flask(__name__)
api = Api(app)

classifier = get_classifier()


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

num_parser = reqparse.RequestParser()
num_parser.add_argument('num', type=int, location='args')


class TokenAPI(Resource):
    def get(self, token):
        args = num_parser.parse_args()
        return classifier.get_token_hashtags(token, num=args.get('num', None))


class HashtagAPI(Resource):
    def get(self, hashtag):
        args = num_parser.parse_args()
        return classifier.get_hashtag_tokens(hashtag, num=args.get('num', None))


class TokenListAPI(Resource):
    def get(self):
        args = num_parser.parse_args()
        tc = classifier.get_tc(num=args.get('num', None))
        return tc


class HashtagListAPI(Resource):
    def get(self):
        args = num_parser.parse_args()
        cc = classifier.get_cc(num=args.get('num', None))
        return cc


api.add_resource(ClassificationAPI, '/api/classify'                         )
api.add_resource(StatusAPI,         '/api/status'                           )
api.add_resource(HashtagAPI,        '/api/hashtag/<string:hashtag>'         )
api.add_resource(HashtagListAPI,    '/api/hashtags'                         )
api.add_resource(TokenAPI,          '/api/token/<string:token>'             )
api.add_resource(TokenListAPI,      '/api/tokens'                           )


def start():
    trainer = Process(target=train_classifier, args=[classifier])
    trainer.start()

    sched = Scheduler()
    sched.start()
    sched.add_interval_job(dump_classifier, args=[classifier], hours=1)

    app.run(debug=True)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        classifier.state_load(sys.argv[1])
    start()

