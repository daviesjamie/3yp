from nose.tools import assert_true, assert_false
from server.filters import TweetsWithHashtagsPredicate, TweetsInEnglishPredicate, NoRetweetsPredicate
import string


class TestTweetsWithHashtagsPredicate:

    def test_accept(self):
        f = TweetsWithHashtagsPredicate()

        tweet = {
            "entities": {
                "hashtags": [
                    {
                        "indices": [
                            70,
                            82
                        ],
                        "text": "testhashtag"
                    }
                ]
            }
        }

        assert_true(f.test(tweet))

    def test_reject(self):
        f = TweetsWithHashtagsPredicate()

        tweet = {
            "entities": {
                "hashtags": []
            }
        }

        assert_false(f.test(tweet))


class TestTweetsInEnglishPredicate:

    def test_accept(self):
        f = TweetsInEnglishPredicate()

        tweet = {
            "lang": "en"
        }

        assert_true(f.test(tweet))

    def test_reject(self):
        f = TweetsInEnglishPredicate()

        tweet = {
            "lang": "fr"
        }

        assert_false(f.test(tweet))


class TestNoRetweetsPredicate:

    def test_accept(self):
        f = NoRetweetsPredicate()

        tweet = {
            "retweeted": False
        }

        assert_true(f.test(tweet))

    def test_reject(self):
        f = NoRetweetsPredicate()

        tweet = {
            "retweeted": True
        }

        assert_false(f.test(tweet))
