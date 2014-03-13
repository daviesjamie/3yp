from multiprocessing import Process
from flask import Flask
from flask.ext.restful import Resource, Api, reqparse
from spout.queues import QueueBufferedQueue
from spout.sources import TweetStream
import sys
from classifier import Classifier, TrainOperation
from filters import TweetsWithHashtagsPredicate, TweetsInEnglishPredicate
from oauth import credentials
from tokeniser import TokeniseTweetFunction


classifier = Classifier()

def _train_classifier():
    twitter = TweetStream(QueueBufferedQueue(3), *credentials('oauth.json'))
    twitter.connect()

    twitter \
        .filter(TweetsWithHashtagsPredicate()) \
        .filter(TweetsInEnglishPredicate()) \
        .map(TokeniseTweetFunction()) \
        .for_each(TrainOperation(classifier), 10)

    twitter.disconnect()

trainer = Process(target=_train_classifier)

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
        return { "status": "ok" }


api.add_resource(ClassificationAPI, '/api/classify')
api.add_resource(StatusAPI, '/api/status')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        classifier.state_load(sys.argv[1])
    else:
        trainer.start()

    app.run(debug=True)
