from django.conf.urls import patterns, include, url

urlpatterns = patterns('clever_twit.views',
    url(r'^$', 'index', name='index'),
    url(r'^tweet/?$', 'tweet', name='tweet'),
)