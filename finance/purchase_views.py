import datetime
import hashlib
import hmac
import os
import random

from django.conf import settings
from django.utils import timezone
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import ProductPurchase, Product
from .serializers import ProductPurchaseSerializer, ProductSerializer, OTPVerifySerializer

from .tasks import run_ocr_and_notify, send_sms_otp  # Celery tasks

# Mobile-friendly upload: allow large files, multipart/form-data
@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([AllowAny])
def apply_for_product(request):
    """
    User applies to buy a product. Files (id_proof, address_proof, video_verification)
    uploaded via multipart/form-data.
    This creates a ProductPurchase and sends an OTP to verify the phone.
    """
    serializer = ProductPurchaseSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    purchase = serializer.save(status="PENDING")

    # generate OTP and store
    otp = f"{random.randint(100000, 999999)}"
    purchase.otp_code = otp
    purchase.otp_created_at = timezone.now()
    purchase.save(update_fields=["otp_code", "otp_created_at"])

    # send OTP async (sms)
    send_sms_otp.delay(purchase.id, purchase.phone, otp)

    return Response({
        "message": "Application received. OTP sent to phone. verify with /apply/verify-otp/",
        "application_id": purchase.id
    }, status=200)

@api_view(["POST"])
@permission_classes([AllowAny])
def verify_otp(request):
    """
    Verify OTP. Body: { "application_id": <int>, "otp": "123456" }
    On success, mark otp_verified True and enqueue OCR & KYC tasks.
    """
    serializer = OTPVerifySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    application_id = serializer.validated_data["application_id"]
    otp = serializer.validated_data["otp"]

    try:
        purchase = ProductPurchase.objects.get(id=application_id)
    except ProductPurchase.DoesNotExist:
        return Response({"error": "Application not found"}, status=404)

    # basic expiry check: 10 minutes
    if not purchase.otp_code or purchase.otp_code != otp:
        return Response({"error": "Invalid OTP"}, status=400)

    if purchase.otp_created_at + datetime.timedelta(minutes=10) < timezone.now():
        return Response({"error": "OTP expired"}, status=400)

    purchase.otp_verified = True
    purchase.status = "OTP_VERIFIED"
    purchase.save(update_fields=["otp_verified", "status"])

    # enqueue OCR & KYC tasks
    run_ocr_and_notify.delay(purchase.id)

    return Response({"message": "OTP verified. KYC started.", "application_id": purchase.id}, status=200)

@api_view(["GET"])
@permission_classes([AllowAny])
def application_status(request, application_id):
    """
    GET /api/applications/<id>/status/
    """
    try:
        p = ProductPurchase.objects.get(id=application_id)
    except ProductPurchase.DoesNotExist:
        return Response({"error": "not found"}, status=404)

    return Response({
        "id": p.id,
        "status": p.status,
        "product": ProductSerializer(p.product).data,
        "created_at": p.created_at,
        "otp_verified": p.otp_verified,
        "admin_comments": p.admin_comments,
    }, status=200)

# Admin APIs
@api_view(["POST"])
@permission_classes([IsAdminUser])
def admin_approve(request, application_id):
    """
    Admin approves the application.
    Body: { "action": "approve", "comments": "..." } or {"action": "reject", "comments": "..."}
    """
    action = request.data.get("action")
    comments = request.data.get("comments", "")

    try:
        p = ProductPurchase.objects.get(id=application_id)
    except ProductPurchase.DoesNotExist:
        return Response({"error": "not found"}, status=404)

    if action == "approve":
        p.status = "APPROVED"
    elif action == "reject":
        p.status = "REJECTED"
    else:
        return Response({"error": "invalid action"}, status=400)

    p.admin_comments = comments
    p.save(update_fields=["status", "admin_comments"])

    # Notify user (email + sms)
    run_notification_for_admin_decision.delay(p.id)

    return Response({"message": f"Application {p.status}"}, status=200)

# Webhook integration endpoint (for partner callbacks)
@api_view(["POST"])
@permission_classes([AllowAny])
@parser_classes([JSONParser])
def partner_webhook(request):
    """
    Verify HMAC signature, process payload.
    Clients must set X-Signature: sha256=<hex>
    """
    signature = request.META.get("HTTP_X_SIGNATURE")
    payload = request.body  # raw bytes

    if not signature:
        return Response({"error": "missing signature"}, status=400)

    secret = settings.WEBHOOK_SECRET.encode()
    computed = hmac.new(secret, payload, hashlib.sha256).hexdigest()
    expected = f"sha256={computed}"
    if not hmac.compare_digest(expected, signature):
        return Response({"error": "invalid signature"}, status=403)

    data = request.data
    # process partner data asynchronously
    handle_partner_payload.delay(data)
    return Response({"message": "accepted"}, status=200)
