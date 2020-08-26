from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render
from .models import Tweet


def home_view(request, *args, **kwargs):
    return render(request, 'page/home.html', context={})


def tweet_list_view(request, *args, **kwargs):
    query_set = Tweet.objects.all()
    tweet_list = [{'id': tweet.id, 'content': tweet.content} for tweet in query_set]
    data = {
        'response': tweet_list
    }
    return JsonResponse(data)


def tweet_detail_view(request, tweet_id, *args, **kwargs):
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