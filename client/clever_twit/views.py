from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response


def index(request):
    if not request.user.is_authenticated():
        return render_to_response('cover.html')

    return render_to_response('index.html')


def tweet(request):
    if not request.user.is_authenticated():
        return render_to_response('cover.html')

    return render_to_response('tweet.html')
