from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import PhoneOTP


class OTPFlowTests(APITestCase):
    def test_send_otp_success(self):
        with patch("accounts.views.send_otp_via_twilio", return_value=(True, "sent")):
            response = self.client.post(
                reverse("send-otp"), {"phone_number": "+15551234567"}, format="json"
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(PhoneOTP.objects.count(), 1)

    def test_verify_otp_success(self):
        PhoneOTP.objects.create(
            phone_number="+15551234567", otp_code="123456", is_verified=False
        )

        response = self.client.post(
            reverse("verify-otp"),
            {"phone_number": "+15551234567", "otp_code": "123456"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get("token"))
