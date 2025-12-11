from django.urls import path

from .views import WatsonInitView, WatsonChatView

urlpatterns = [
    path("watson/init/", WatsonInitView.as_view(), name="watson-init"),
    path("watson/chat/", WatsonChatView.as_view(), name="watson-chat"),
]

