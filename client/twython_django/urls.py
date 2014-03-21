from django.conf.urls import patterns, include, url

urlpatterns = patterns('twython_django.views',
    url(r'^login/?$', 'begin_auth', name='twitter_login'),
    url(r'^logout/?$', 'logout', name='twitter_logout'),
    url(r'^thanks/?$', 'thanks', name='twitter_callback'),
    url(r'^user_timeline/?$', 'user_timeline', name='twitter_timeline'),
)