## OTP Login Backend

Python Django backend that handles phone-number based login via OTP delivered with Twilio. The service exposes REST endpoints to request and verify an OTP, creating an authenticated session via DRF tokens.

### Features
- Request OTP: `POST /api/auth/send-otp/` with `phone_number`
- Verify OTP: `POST /api/auth/verify-otp/` with `phone_number` and `otp_code`
- Twilio SMS delivery using messaging service or phone number
- DRF token returned after verification for subsequent authenticated requests

### Prerequisites
- Python 3.12+
- Twilio account with Messaging Service SID or SMS-capable phone number

### Setup
```bash
cd /Users/satyendra/otp_twilio_backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # then populate with Twilio credentials
python manage.py migrate
python manage.py runserver
```

### Environment Variables
See `.env.example` for all configurable entries:
- `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`
- `OTP_EXPIRATION_MINUTES`
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`
- `TWILIO_MESSAGING_SERVICE_SID` or `DEFAULT_FROM_PHONE_NUMBER`

### Testing
```bash
source .venv/bin/activate
python manage.py test
```

### API Usage
1. **Request OTP**
   ```bash
   curl -X POST http://localhost:8000/api/auth/send-otp/ \
     -H "Content-Type: application/json" \
     -d '{"phone_number":"+15551234567"}'
   ```
2. **Verify OTP**
   ```bash
   curl -X POST http://localhost:8000/api/auth/verify-otp/ \
     -H "Content-Type: application/json" \
     -d '{"phone_number":"+15551234567","otp_code":"123456"}'
   ```
   Successful verification returns `{ "token": "<drf-token>", "user": { ... } }`.

