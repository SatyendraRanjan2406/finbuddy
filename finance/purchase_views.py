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

from .models import ProductPurchase, Product, UserProduct, UserPremiumPayment
from .serializers import (
    ProductPurchaseSerializer, 
    ProductSerializer, 
    OTPVerifySerializer,
    ProductPurchaseInitiateSerializer,
    UserProductSerializer,
    UserPremiumPaymentSerializer,
    ProductPurchaseDetailSerializer
)

from .tasks import (
    run_ocr_and_notify, 
    send_sms_otp,
    run_notification_for_admin_decision,
    handle_partner_payload
)  # Celery tasks
from datetime import date, timedelta
from django.utils import timezone

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


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser, JSONParser])
@permission_classes([IsAuthenticated])
def initiate_product_purchase(request):
    """
    Initiate product purchase - creates records in ProductPurchase, UserProduct, and UserPremiumPayment
    with status = INITIATED.
    
    Accepts both JSON and multipart/form-data (for file uploads).
    
    Body (JSON or form-data): {
        "product_id": <int>,
        "premium_amount": <decimal>,
        "premium_frequency": "MONTHLY|QUARTERLY|HALF_YEARLY|YEARLY",
        "tenure_years": <int> (optional),
        "auto_renew": <bool> (default: True),
        "policy_number": <string> (optional),
        "maturity_date": "YYYY-MM-DD" (optional),
        "next_premium_due": "YYYY-MM-DD" (optional),
        "id_proof": <file> (optional),
        "address_proof": <file> (optional),
        "video_verification": <file> (optional),
        "full_name": <string> (optional),
        "email": <email> (optional),
        "phone": <string> (optional)
    }
    """
    serializer = ProductPurchaseInitiateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    
    product_id = serializer.validated_data["product_id"]
    premium_amount = serializer.validated_data["premium_amount"]
    premium_frequency = serializer.validated_data["premium_frequency"]
    tenure_years = serializer.validated_data.get("tenure_years")
    auto_renew = serializer.validated_data.get("auto_renew", True)
    policy_number = serializer.validated_data.get("policy_number")
    provided_maturity_date = serializer.validated_data.get("maturity_date")
    provided_next_premium_due = serializer.validated_data.get("next_premium_due")
    
    # KYC file fields
    id_proof = serializer.validated_data.get("id_proof")
    address_proof = serializer.validated_data.get("address_proof")
    video_verification = serializer.validated_data.get("video_verification")
    
    # Additional user info (optional, will use authenticated user if not provided)
    provided_full_name = serializer.validated_data.get("full_name")
    provided_email = serializer.validated_data.get("email")
    provided_phone = serializer.validated_data.get("phone")
    
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)
    
    user = request.user
    
    # Calculate next premium due date based on frequency (if not provided)
    today = date.today()
    if provided_next_premium_due:
        next_due = provided_next_premium_due
    else:
        if premium_frequency == "MONTHLY":
            next_due = today + timedelta(days=30)
        elif premium_frequency == "QUARTERLY":
            next_due = today + timedelta(days=90)
        elif premium_frequency == "HALF_YEARLY":
            next_due = today + timedelta(days=180)
        else:  # YEARLY
            next_due = today + timedelta(days=365)
    
    # Calculate maturity date if tenure is provided (if not explicitly provided)
    maturity_date = provided_maturity_date
    if not maturity_date and tenure_years:
        maturity_date = today + timedelta(days=365 * tenure_years)
    
    # Create ProductPurchase with INITIATED status
    # Use provided values or fall back to authenticated user's data
    purchase = ProductPurchase.objects.create(
        product=product,
        user=user,
        full_name=provided_full_name or (user.get_full_name() or user.username),
        email=provided_email or (user.email or ""),
        phone=provided_phone or (user.phone or ""),
        id_proof=id_proof,
        address_proof=address_proof,
        video_verification=video_verification,
        status="INITIATED"
    )
    
    # Create UserProduct with INITIATED status
    user_product = UserProduct.objects.create(
        user=user,
        product=product,
        purchase_date=timezone.now(),
        premium_amount=premium_amount,
        premium_frequency=premium_frequency,
        next_premium_due=next_due,
        tenure_years=tenure_years,
        maturity_date=maturity_date,
        auto_renew=auto_renew,
        policy_number=policy_number,
        status="INITIATED"
    )
    
    # Create UserPremiumPayment with INITIATED status
    premium_payment = UserPremiumPayment.objects.create(
        user_product=user_product,
        premium_amount=premium_amount,
        premium_date=next_due,
        payment_status="INITIATED"
    )
    
    return Response({
        "message": "Product purchase initiated successfully",
        "purchase_id": purchase.id,
        "user_product_id": user_product.id,
        "premium_payment_id": premium_payment.id,
        "status": "INITIATED"
    }, status=201)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_purchases(request):
    """
    GET /api/finance/purchase/
    Get all product purchases for the authenticated user.
    
    Query Parameters (optional):
    - status: Filter by status (e.g., ?status=INITIATED)
    - product_id: Filter by product ID (e.g., ?product_id=1)
    """
    user = request.user
    purchases = ProductPurchase.objects.filter(user=user).order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.query_params.get('status')
    if status_filter:
        purchases = purchases.filter(status=status_filter)
    
    # Filter by product_id if provided
    product_id_filter = request.query_params.get('product_id')
    if product_id_filter:
        try:
            purchases = purchases.filter(product_id=int(product_id_filter))
        except ValueError:
            return Response({"error": "Invalid product_id"}, status=400)
    
    serializer = ProductPurchaseDetailSerializer(purchases, many=True)
    return Response({
        "count": len(serializer.data),
        "purchases": serializer.data
    }, status=200)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_purchase_detail(request, purchase_id):
    """
    GET /api/finance/purchase/<purchase_id>/
    Get detailed information about a specific product purchase for the authenticated user.
    """
    try:
        purchase = ProductPurchase.objects.get(id=purchase_id, user=request.user)
    except ProductPurchase.DoesNotExist:
        return Response({"error": "Purchase not found"}, status=404)
    
    serializer = ProductPurchaseDetailSerializer(purchase)
    return Response(serializer.data, status=200)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def complete_product_purchase(request, purchase_id):
    """
    Complete product purchase - updates status to SUCCESS for ProductPurchase, UserProduct, and UserPremiumPayment.
    
    This endpoint should be called after payment is confirmed.
    """
    try:
        purchase = ProductPurchase.objects.get(id=purchase_id, user=request.user)
    except ProductPurchase.DoesNotExist:
        return Response({"error": "Purchase not found"}, status=404)
    
    # Update ProductPurchase status to SUCCESS
    purchase.status = "SUCCESS"
    purchase.save(update_fields=["status"])
    
    # Find associated UserProduct and update status
    try:
        user_product = UserProduct.objects.get(
            user=request.user,
            product=purchase.product,
            status="INITIATED"
        )
        user_product.status = "SUCCESS"
        user_product.save(update_fields=["status"])
        
        # Update associated premium payment
        premium_payment = UserPremiumPayment.objects.filter(
            user_product=user_product,
            payment_status="INITIATED"
        ).first()
        
        if premium_payment:
            premium_payment.payment_status = "SUCCESS"
            premium_payment.paid_on = timezone.now()
            premium_payment.save(update_fields=["payment_status", "paid_on"])
        
        return Response({
            "message": "Product purchase completed successfully",
            "purchase_id": purchase.id,
            "user_product_id": user_product.id,
            "status": "SUCCESS"
        }, status=200)
    except UserProduct.DoesNotExist:
        return Response({"error": "UserProduct not found"}, status=404)
