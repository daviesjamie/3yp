from nose.tools import assert_equal, assert_not_equal, assert_in, assert_is_instance, assert_raises, assert_not_in, assert_false, assert_true
from datetime import datetime
from server.classifier import Classifier
from server.classifier_manager import get_classifier
import string
import datetime
import multiprocessing


class TestClassifier:

    def test_initialisation(self):
        c = Classifier()
        assert_equal(c.hc, {})
        assert_equal(c.htc, {})
        assert_equal(c.tc, {})
        assert_equal(c.thc, {})
        assert_equal(c.tweet_total, 0)
        assert_equal(c.hashtag_total, 0)
        assert_is_instance(c.start_time, datetime.datetime)
        assert_is_instance(c.lock, multiprocessing.synchronize.Lock)

    def test_training_fails_when_no_hashtags(self):
        c = Classifier()
        c.train(['no', 'hashtags', '!'])
        assert_equal(c.hc, {})
        assert_equal(c.htc, {})
        assert_equal(c.tc, {})
        assert_equal(c.thc, {})
        assert_equal(c.tweet_total, 0)
        assert_equal(c.hashtag_total, 0)

    def test_training_fails_when_all_hashtags(self):
        c = Classifier()
        c.train(['#tag1', '#tag2', '#tag3'])
        assert_equal(c.hc, {})
        assert_equal(c.htc, {})
        assert_equal(c.tc, {})
        assert_equal(c.thc, {})
        assert_equal(c.tweet_total, 0)
        assert_equal(c.hashtag_total, 0)

    def test_training_fails_when_no_tokens(self):
        c = Classifier()
        c.train([])
        assert_equal(c.hc, {})
        assert_equal(c.htc, {})
        assert_equal(c.tc, {})
        assert_equal(c.thc, {})
        assert_equal(c.tweet_total, 0)
        assert_equal(c.hashtag_total, 0)

    def test_training_updates_models(self):
        c = Classifier()

        c.train(['this', 'is', 'a', 'test', 'tweet', '!', '#testing123'])
        assert_in('testing123', c.hc)
        assert_in('testing123', c.htc)
        assert_in('test', c.tc)
        assert_in('test', c.thc)
        assert_in('test', c.htc['testing123'])

        c.train(['same', 'hashtag', '#testing123'])
        assert_in('test', c.htc['testing123'])
        assert_in('same', c.htc['testing123'])

    def test_training_updates_totals(self):
        c = Classifier()

        c.train(['test', '#hashtag'])
        assert_equal(c.tweet_total, 1)
        assert_equal(c.hashtag_total, 1)

        c.train(['same', '#hashtag'])
        assert_equal(c.tweet_total, 2)
        assert_equal(c.hashtag_total, 2)

        c.train(['blah', 'blah', '#tag1', '#tag2', '#tag3'])
        assert_equal(c.tweet_total, 3)
        assert_equal(c.hashtag_total, 5)

    def test_use_hashtag_text_option(self):
        c = Classifier(use_hashtag_text=True)
        c.train(['token', '#hashtag'])
        assert_in('hashtag', c.tc)
        assert_in('hashtag', c.thc)
        assert_in('hashtag', c.htc['hashtag'])

    def test_getters(self):
        c = Classifier()

        c.train(['this', 'is', 'a', 'test', '!', '#testing123'])
        c.train(['yet', 'another', 'test', '#testing123'])
        c.train(['different', 'hashtag', '#blah'])

        # get_hashtags()
        assert_equal(c.get_hashtags(), [('testing123', 2), ('blah', 1)])
        assert_equal(c.get_hashtags(num=1), [('testing123', 2)])

        # get_hashtag_tokens()
        assert_in(('different', 1), c.get_hashtag_tokens('blah'))
        assert_in(('hashtag', 1), c.get_hashtag_tokens('blah'))
        assert_equal(c.get_hashtag_tokens('testing123', num=1), [('test', 2)])

        # get_tokens()
        assert_in(('test', 2), c.get_tokens())
        assert_in(('another', 1), c.get_tokens())
        assert_equal(c.get_tokens(num=1), [('test', 2)])

        c.train(['another', '#hashtag'])
        c.train(['yet', 'another', '#hashtag'])

        # get_token_hashtags()
        assert_in(('hashtag', 2), c.get_token_hashtags('another'))
        assert_in(('testing123', 1), c.get_token_hashtags('another'))
        assert_equal(c.get_token_hashtags('another', num=1), [('hashtag', 2)])

        # get_totals()
        total_tweets, total_tags = c.get_totals()
        assert_equal(total_tweets, 5)
        assert_equal(total_tags, 5)

        # get_unique_counts()
        unique_tags, unique_tokens = c.get_unique_counts()
        assert_equal(unique_tags, 3)
        assert_equal(unique_tokens, 9)

        # get_memory_usage()
        mhc, mhtc, mtc, mthc = c.get_memory_usage()
        assert_true(mhc > 0)
        assert_true(mhtc > 0)
        assert_true(mtc > 0)
        assert_true(mthc > 0)
        c.train(['increase', 'memory', 'usage', '#test'])
        mhc2, mhtc2, mtc2, mthc2 = c.get_memory_usage()
        assert_true(mhc2 > mhc)
        assert_true(mhtc2 > mhtc)
        assert_true(mtc2 > mtc)
        assert_true(mthc2 > mthc)


class TestClassifierManager:

    def test_methods_exist(self):
        required_methods = ['train', 'classify', 'get_hashtags', 'get_hashtag_tokens',
                   'get_memory_usage', 'get_tokens', 'get_token_hashtags', 'get_totals',
                   'get_unique_counts', 'get_uptime', 'state_dump', 'state_load']

        c = get_classifier()

        all_methods = [method for method in dir(c) if callable(getattr(c, method))]

        for m in required_methods:
            assert_in(m, all_methods)

    def test_models_are_protected(self):
        hidden_objects = ['hc', 'htc', 'tc', 'thc', 'tweet_total', 'hashtag_total', 'start_time', 'lock']

        c = get_classifier()

        for o in hidden_objects:
            assert_not_in(o, dir(c))
