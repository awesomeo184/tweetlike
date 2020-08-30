from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render, redirect
from django.utils.http import is_safe_url
from django.conf import settings

from rest_framework.decorators import api_view, authentication_classes ,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response

from .models import Tweet
from .forms import TweetForm
from .serializers import TweetSerializer, TweetActionSerializer

ALLOWED_HOSTS = settings.ALLOWED_HOSTS


def home_view(request, *args, **kwargs):
    return render(request, 'page/home.html', context={})


@api_view(['GET'])
def tweet_list_view(request, *args, **kwargs):
    query_set = Tweet.objects.all()
    serializer = TweetSerializer(query_set, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def tweet_create_view(request, *args, **kwargs):
    serializer = TweetSerializer(data=request.POST)
    if serializer.is_valid(raise_exception=True):
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)
    return Response({}, status=400)


@api_view(['DELETE', 'POST'])
@permission_classes([IsAuthenticated])
def tweet_delete_view(request, tweet_id, *args, **kwargs):
    tweet = Tweet.objects.filter(id=tweet_id)
    if not tweet.exists():
        return Response({}, status=404)

    tweet = tweet.filter(user=request.user)
    if not tweet.exists():
        return Response({"message": "You cannot delete this tweet"}, status=401)
    obj = tweet.first()
    obj.delete()
    return Response({"message": "Tweet removed"}, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tweet_action_view(request, *args, **kwargs):
    """
    id is required.
    Action options are: like, unlike, retweet
    """
    serializer = TweetActionSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        data = serializer.validated_data
        tweet_id = data.get("id")
        action = data.get("action")

        tweet = Tweet.objects.filter(id=tweet_id)
        if not tweet.exists():
            return Response({}, status=404)
        obj = tweet.first()
        if action == 'like':
            obj.likes.add(request.user)
            serializer = TweetSerializer(obj)
            return Response(serializer.data, status=200)
        elif action == 'unlike':
            obj.likes.remove(request.user)
        elif action == 'retweet':
            # TODO retweet logic
            pass
    return Response({}, status=200)

@api_view(['GET'])
def tweet_detail_view(request, tweet_id, *args, **kwargs):
    tweet = Tweet.objects.filter(id=tweet_id)
    if not tweet.exists():
        return Response({}, status=404)
    obj = tweet.first()
    serializer = TweetSerializer(obj)
    return Response(serializer.data, status=200)


def tweet_list_view_pure_django(request, *args, **kwargs):
    query_set = Tweet.objects.all()
    tweet_list = [tweet.serialize() for tweet in query_set]
    data = {
        'response': tweet_list
    }
    return JsonResponse(data)


def tweet_create_view_pure_django(request, *args, **kwargs):
    user = request.user
    if not request.user.is_authenticated:
        user = None
        if request.is_ajax():
            return JsonResponse({}, status=401)
        return redirect(settings.LOGIN_URL)
    form = TweetForm(request.POST or None)
    next_url = request.POST.get("next") or None
    if form.is_valid():
        obj = form.save(commit=False)
        obj.user = user
        obj.save()
        if request.is_ajax():
            return JsonResponse(obj.serialize(), status=201)
        if next_url != None and is_safe_url(next_url, ALLOWED_HOSTS):
            return redirect(next_url)
        form = TweetForm()
    if form.errors:
        if request.is_ajax():
            return JsonResponse(form.errors, status=400)
    return render(request, 'components/form.html', context={'form': form})


def tweet_detail_view_pure_django(request, tweet_id, *args, **kwargs):
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
