from django.urls import path

from .views import FinMateInitView, FinMateChatView, voice_to_finance


urlpatterns = [
    path("finmate/init/", FinMateInitView.as_view(), name="finmate-init"),
    path("finmate/chat/", FinMateChatView.as_view(), name="finmate-chat"),
    path("voice/ask", voice_to_finance, name="voice-to-finance"),
]


