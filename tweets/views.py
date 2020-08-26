from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render
from .models import Tweet


def home_view(request):
    return HttpResponse("<h1>Hello World</h1>")


def tweet_detail_view(request, tweet_id):
    data = {
        'id': tweet_id,
    }
    status = 200
    try:
        tweet = Tweet.objects.get(id=tweet_id)
        data['content'] = tweet.content
    except:
        data['message'] = "Not Found"
        status = 404

    return JsonResponse(data, status=status)