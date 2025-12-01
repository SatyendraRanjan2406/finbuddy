from django.urls import path

from .views import FinMateInitView, FinMateChatView


urlpatterns = [
    path("finmate/init/", FinMateInitView.as_view(), name="finmate-init"),
    path("finmate/chat/", FinMateChatView.as_view(), name="finmate-chat"),
]


