from django.conf.urls import patterns, include, url

urlpatterns = patterns('clever_twit.views',
    url(r'^$', 'index', name='index'),
    url(r'^tweet/?$', 'tweet', name='tweet'),
    url(r'^search/?$', 'search', name='search'),
    url(r'^results/?$', 'results', name='results'),
    url(r'^graphs/?$', 'graphs', name='graphs'),
    url(r'^stats/?$', 'stats', name='stats'),
)
