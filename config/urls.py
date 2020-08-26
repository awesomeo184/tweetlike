from django.contrib import admin
from django.urls import path

from tweets import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view),
    path('tweet/<int:tweet_id>', views.tweet_detail_view),

]
