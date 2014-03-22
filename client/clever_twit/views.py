from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from twython import Twython

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