from django.conf import settings
from django.shortcuts import render
from twython import Twython

def index(request):
    if not request.user.is_authenticated():
        return render(request, 'cover.html')

    return render(request, 'index.html')


def tweet(request):
    if not request.user.is_authenticated():
        return render(request, 'cover.html')

    posted = False
    errors = []

    if request.method == "POST":
        status = request.POST.get('status')

        if len(status) > 140:
            errors.append("Tweet was too long!")
        else:
            user = request.user.twitterprofile
            twitter = Twython(settings.TWITTER_KEY, settings.TWITTER_SECRET, user.oauth_token, user.oauth_secret)

            twitter.update_status(status=status)
            posted = True


    return render(request, 'tweet.html', { 'posted': posted, 'errors': errors })
