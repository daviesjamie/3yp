from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
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
def graphs(request):
    return render(request, 'graphs.html')

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
