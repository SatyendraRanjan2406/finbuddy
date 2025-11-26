from celery import shared_task
import pytesseract
from PIL import Image
import requests
from django.conf import settings
from .models import ProductPurchase

@shared_task
def send_sms_otp(purchase_id, phone, otp):
    from twilio.rest import Client
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    body = f"Your verification OTP is {otp}. It expires in 10 minutes."
    client.messages.create(body=body, from_=settings.TWILIO_FROM_NUMBER, to=phone)
    return True

@shared_task
def run_ocr_and_notify(purchase_id):
    # fetch purchase
    p = ProductPurchase.objects.get(id=purchase_id)
    # Best-effort OCR: use Tesseract on the downloaded files (only for image/pdf preconverted)
    ocr_result = {}
    try:
        # download id_proof file to temp
        id_url = p.id_proof.url
        r = requests.get(id_url, stream=True)
        tmp_path = f"/tmp/id_proof_{p.id}.img"
        with open(tmp_path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)

        text = pytesseract.image_to_string(Image.open(tmp_path))
        ocr_result["id_proof_text"] = text

        # naive PAN regex
        import re
        pan_match = re.search(r"[A-Z]{5}[0-9]{4}[A-Z]", text)
        if pan_match:
            p.pan_number = pan_match.group(0)

        aadhaar_match = re.search(r"\b\d{4}\s?\d{4}\s?\d{4}\b", text)
        if aadhaar_match:
            p.aadhaar_number = aadhaar_match.group(0).replace(" ", "")

    except Exception as e:
        ocr_result["error"] = str(e)

    p.ocr_data = ocr_result
    p.status = "KYC_IN_PROGRESS"
    p.save(update_fields=["ocr_data", "status", "pan_number", "aadhaar_number"])

    # Optionally call 3rd party KYC provider here and update status
    # notify admins via email/sms to review
    run_notification_for_new_application.delay(p.id)
    return True

@shared_task
def run_notification_for_new_application(purchase_id):
    # send email to admin & applicant
    p = ProductPurchase.objects.get(id=purchase_id)
    # Using SendGrid SDK (or django.core.mail)
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=[p.email, "admin@example.com"],
        subject="New KYC Application - Please review",
        html_content=f"<p>Application {p.id} is ready for review. Product: {p.product.name}</p>"
    )
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        sg.send(message)
    except Exception:
        pass

@shared_task
def run_notification_for_admin_decision(purchase_id):
    p = ProductPurchase.objects.get(id=purchase_id)
    # notify applicant
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    msg = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=p.email,
        subject=f"Application {p.id} - {p.status}",
        html_content=f"<p>Your application status is now: {p.status}. Comments: {p.admin_comments}</p>"
    )
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        sg.send(msg)
    except Exception:
        pass

@shared_task
def handle_partner_payload(data):
    # implement mapping and actions
    # e.g., update ProductPurchase by external id
    return True
