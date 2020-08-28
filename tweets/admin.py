from django.contrib import admin
from .models import Tweet


class TweetAdmin(admin.ModelAdmin):
    list_display = ['content', 'user']
    search_fields = ['user__username']

    class Meta:
        model = Tweet


admin.site.register(Tweet, TweetAdmin)
