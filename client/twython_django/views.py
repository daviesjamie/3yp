from django.conf import settings
from django.contrib.auth import authenticate, login, logout as django_logout
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from twython import Twython
from twython_django.models import TwitterProfile

def logout(request, redirect_url=settings.LOGOUT_REDIRECT_URL):
    django_logout(request)
    return HttpResponseRedirect(request.build_absolute_uri(redirect_url))

def begin_auth(request):
    twitter = Twython(settings.TWITTER_KEY, settings.TWITTER_SECRET)

    callback_url = request.build_absolute_uri(reverse('twython_django.views.thanks'))
    auth_props = twitter.get_authentication_tokens(callback_url)

    request.session['request_token'] = auth_props
    return HttpResponseRedirect(auth_props['auth_url'])

def thanks(request, redirect_url=settings.LOGIN_REDIRECT_URL):
    oauth_token = request.session['request_token']['oauth_token']
    oauth_token_secret = request.session['request_token']['oauth_token_secret']
    twitter = Twython(settings.TWITTER_KEY, settings.TWITTER_SECRET, oauth_token, oauth_token_secret)

    authorized_tokens = twitter.get_authorized_tokens(request.GET['oauth_verifier'])

    try:
        user = User.objects.get(username=authorized_tokens['screen_name'])
    except User.DoesNotExist:
        user = User.objects.create_user(authorized_tokens['screen_name'], 'asdfhjkl@qwerty.com',
                                        authorized_tokens['oauth_token_secret'])
        profile = TwitterProfile()
        profile.user = user
        profile.oauth_token = authorized_tokens['oauth_token']
        profile.oauth_secret = authorized_tokens['oauth_token_secret']
        profile.save()

    user = authenticate(
        username=authorized_tokens['screen_name'],
        password=authorized_tokens['oauth_token_secret']
    )

    login(request, user)
    return HttpResponseRedirect(redirect_url)


def user_timeline(request):
    user = request.user.twitterprofile
    twitter = Twython(settings.TWITTER_KEY, settings.TWITTER_SECRET, user.oauth_token, user.oauth_secret)
    user_tweets = twitter.get_home_timeline()

    return render_to_response('tweets.html', {'tweets': user_tweets})
