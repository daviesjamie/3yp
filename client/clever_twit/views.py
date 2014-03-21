from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response


def tweet(request):
    if not request.user.is_authenticated():
        HttpResponseRedirect(settings.LOGIN_URL)

    return render_to_response('tweet.html')
