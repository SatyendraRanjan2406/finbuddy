from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.views import (
    SendOTPView,
    VerifyOTPView,
    FaceEnrollmentView,
    FaceLoginView,
)

urlpatterns = [
    # OTP-based authentication (existing, backward compatible)
    path("send-otp/", SendOTPView.as_view(), name="send-otp"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    
    # Facial recognition authentication (new)
    path("face/enroll/", FaceEnrollmentView.as_view(), name="face-enroll"),
    path("face/login/", FaceLoginView.as_view(), name="face-login"),
    
    # Token refresh (works for both OTP and face login)
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

