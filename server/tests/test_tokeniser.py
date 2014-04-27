from nose.tools import assert_equal, assert_not_equal, assert_not_in
from server.tokeniser import TokeniseTextFunction, TokeniseTweetFunction
import string


class TestTokeniseFunctions:

    def test_tokenisation(self):
        t = TokeniseTextFunction()
        assert_equal(t.apply('test'), ['test'])
        assert_equal(t.apply('this is a simple test'), ['this', 'is', 'a', 'simple', 'test'])
        assert_equal(t.apply('OMG! @username just wrote a #test tweet?!'), ['omg', '!', '@username', 'just', 'wrote', 'a', '#test', 'tweet', '?!'])

    def test_case_insensitive(self):
        t = TokeniseTextFunction()
        assert_equal(t.apply('Test'), ['test'])
        assert_equal(t.apply('TEST'), ['test'])
        assert_equal(t.apply('TeStInG'), ['testing'])

    def test_remove_punctuation(self):
        t = TokeniseTextFunction(punctuation=True)
        assert_equal(t.apply('"Today; long, and tiring... blah!" Well?'), ["today", 'long', 'and', 'tiring', 'blah', 'well'])
        assert_equal(t.apply(' '.join(string.punctuation)), [])
        assert_equal(t.apply("jamie's"), ['jamie', "'s"])
        assert_equal(t.apply('"test"'), ['test'])

    def test_remove_stop_tokens(self):
        t = TokeniseTextFunction(stop_tokens=True)
        assert_equal(t.apply('this is a test'), ['test'])
        assert_equal(t.apply("jamie's"), ['jamie'])
        assert_equal(t.apply('this, is! the; .that?'), [',', '!', ';', '.', '?'])
        assert_equal(t.apply("hell you'd only ourselves which those yours herself who's against what's you're wed she's had"), [])

    def test_remove_usernames(self):
        t = TokeniseTextFunction(usernames=True)
        assert_equal(t.apply('@daviesjamie is the best!'), ['is', 'the', 'best', '!'])
        assert_equal(t.apply('@username1 @username2 #hashtag'), ['#hashtag'])
        assert_equal(t.apply('@hello, @user!'), [',', '!'])
        assert_equal(t.apply('ym@6'), ['ym@6'])

    def test_remove_urls(self):
        t = TokeniseTextFunction(urls=True)
        assert_equal(t.apply('http://www.test.com'), [])
        assert_equal(t.apply('www.test.com'), [])
        assert_equal(t.apply('www.test.com/path/to/page'), [])
        assert_equal(t.apply('www.test.com/trailing/slash/'), [])
        assert_equal(t.apply('http://www.test.com/path/to/page.html?get=var&me=jamie'), [])
        assert_equal(t.apply('https://securetest.com'), [])
        assert_equal(t.apply('https://subdomain.test.com'), [])
        assert_equal(t.apply('https://www.subdomain.test.com'), [])
        assert_equal(t.apply('http://images.cheezburger.com/completestore/2011/2/20/a4ea536d-4b21-4517-b498-a3491437d224.jpg'), [])

        assert_not_equal(t.apply('www.'), [])
        assert_not_equal(t.apply('www.a.b.c.d'), [])
        assert_not_equal(t.apply('https:google.com'), [])
        assert_not_equal(t.apply('e.g'), [])
        assert_not_equal(t.apply('T.G.I.F'), [])
        assert_not_in('www.google.com', t.apply("Hey! Check this out: www.google.com, it's awesome!"))

    def test_remove_all_together(self):
        t = TokeniseTextFunction(stop_tokens=True, punctuation=True, usernames=True, urls=True)
        assert_equal(t.apply('http://images.cheezburger.com/completestore/2011/2/20/a4ea536d-4b21-4517-b498-a3491437d224.jpg'), [])
        assert_equal(t.apply('@hello, @user!'), [])
        assert_equal(t.apply('this, is! the; .that?'), [])
        assert_equal(t.apply('@this @there @his @hers'), [])
        assert_not_equal(t.apply("Hey! Check this out: www.google.com, it's awesome!"), [])
        assert_not_in('www.google.com', t.apply("Hey! Check this out: www.google.com, it's awesome!"))
