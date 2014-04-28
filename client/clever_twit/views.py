from __future__ import division
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from random import shuffle
from twython import Twython
import simplejson
import urllib2

def index(request):
    if not request.user.is_authenticated():
        return render(request, 'cover.html')

    return render(request, 'index.html')


@login_required
def tweet(request):
    posted = False
    errors = []

    if request.method == "POST":
        status = request.POST.get('status')

        if len(status) > 140:
            errors.append("That tweet was too long!")
        elif len(status) == 0:
            errors.append("That tweet was empty!")
        else:
            user = request.user.twitterprofile
            twitter = Twython(settings.TWITTER_KEY, settings.TWITTER_SECRET, user.oauth_token, user.oauth_secret)

            twitter.update_status(status=status)
            posted = True


    return render(request, 'tweet.html', { 'posted': posted, 'errors': errors })


@login_required
def search(request):
    return render(request, 'search.html')

@login_required
def hashtags(request):
    req = urllib2.Request('http://kanga-jagd1g11.ecs.soton.ac.uk/api/hashtags?num={0}'.format(50))
    opener = urllib2.build_opener()
    f = opener.open(req)
    tagjson = simplejson.load(f)
    div = tagjson[0][1]
    tags = [(u'#{0}'.format(t[0]),t[1]/div) for t in tagjson]
    shuffle(tags)

    return render(request, 'hashtags.html', { 'hashtags': tags })

@login_required
def hashtag(request):
    return render(request, 'hashtag.html')

@login_required
def tokens(request):
    req = urllib2.Request('http://kanga-jagd1g11.ecs.soton.ac.uk/api/hashtags?num={0}'.format(50))
    opener = urllib2.build_opener()
    f = opener.open(req)
    tokenjson = simplejson.load(f)
    div = tokenjson[0][1]
    tokens = [(t[0],t[1]/div) for t in tokenjson]
    shuffle(tokens)

    return render(request, 'tokens.html', { 'tokens': tokens })

@login_required
def token(request):
    return render(request, 'token.html')

@login_required
def stats(request):
    return render(request, 'stats.html')

@login_required
@csrf_exempt
def results(request):
    query = request.GET.get('q')
    if query.startswith('#'):
        query = query[1:]

    user = request.user.twitterprofile
    twitter = Twython(settings.TWITTER_KEY, settings.TWITTER_SECRET, user.oauth_token, user.oauth_secret)

    req = urllib2.Request('http://kanga-jagd1g11.ecs.soton.ac.uk/api/hashtag/{0}?num={1}'.format(query, 10))
    opener = urllib2.build_opener()
    f = opener.open(req)
    expjson = simplejson.load(f)
    expansions = [e[0] for e in expjson]
    expansion = ' '.join(expansions)

    results = twitter.search(q=u'{0}'.format(expansion), count=25)

    return render(request, 'results.html', { 'query': query, 'expansions': expansions, 'results': results['statuses'] })
