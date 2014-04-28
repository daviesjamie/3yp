from django.conf.urls import patterns, include, url

urlpatterns = patterns('clever_twit.views',
    url(r'^$', 'index', name='index'),
    url(r'^tweet/?$', 'tweet', name='tweet'),
    url(r'^search/?$', 'search', name='search'),
    url(r'^results/?$', 'results', name='results'),
    url(r'^hashtags/?$', 'hashtags', name='hashtags'),
    url(r'^hashtag/?$', 'hashtag', name='hashtag'),
    url(r'^tokens/?$', 'tokens', name='tokens'),
    url(r'^token/?$', 'token', name='token'),
    url(r'^stats/?$', 'stats', name='stats'),
)
