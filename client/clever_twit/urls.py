from django.conf.urls import patterns, include, url

urlpatterns = patterns('clever_twit.views',
    url(r'^$', 'tweet', name='tweet'),
)
