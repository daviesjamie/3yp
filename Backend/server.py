from flask import Flask
from flask.ext import restful
from spout.queues import QueueBufferedQueue
from spout.sources import TweetStream
from classifier import Classifier, TokenizeTweetFunction, TrainOperation
from filters import TweetsWithHashtagsPredicate, TweetsInEnglishPredicate
from utils import credentials


def run():
    classifier = Classifier()

    twitter = TweetStream(QueueBufferedQueue(3), *credentials('oauth.json'))
    twitter.connect()

    twitter \
        .filter(TweetsWithHashtagsPredicate()) \
        .filter(TweetsInEnglishPredicate()) \
        .map(TokenizeTweetFunction()) \
        .for_each(TrainOperation(classifier), 10)

    app = Flask(__name__)
    api = restful.Api(app)

    api.add_resource(Status,'/')
    api.add_resource(Classification, '/classify')
    api.add_resource(Model, '/model')
    api.add_resource(Counts, '/counts')

    app.run(debug=True)


class Status(restful.Resource):
    pass


class Classification(restful.Resource):
    pass


class Model(restful.Resource):
    pass


class Counts(restful.Resource):
    pass


if __name__ == '__main__':
    run()