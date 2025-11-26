# API CURL Commands

This document contains all available API endpoints with example curl commands.

**Base URL:** `http://localhost:8000` (or your server URL)

---

## Authentication APIs

### 1. Send OTP

Send an OTP to a phone number.

**Endpoint:** `POST /api/auth/send-otp/`

**Request Body:**
```json
{
  "phone_number": "+1234567890"
}
```

**CURL Command:**
```bash
curl -X POST http://localhost:8000/api/auth/send-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1234567890"
  }'
```

**Success Response (200):**
```json
{
  "detail": "OTP sent.",
  "otp_id": 1
}
```

**Error Response (502 - Twilio Error):**
```json
{
  "detail": "Error message from Twilio"
}
```

**Example with different phone number:**
```bash
curl -X POST http://localhost:8000/api/auth/send-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+919876543210"
  }'
```

**Note:** Phone number format:
- Must be 10-15 digits
- Should include country code (e.g., +1 for US, +91 for India)
- Can omit the `+` prefix (it will be added automatically)
- Example: `+1234567890` or `1234567890` (for US)
- Example: `+919876543210` or `919876543210` (for India)

---

### 2. Verify OTP

Verify the OTP code and authenticate the user.

**Endpoint:** `POST /api/auth/verify-otp/`

**Request Body:**
```json
{
  "phone_number": "+1234567890",
  "otp_code": "123456"
}
```

**CURL Command:**
```bash
curl -X POST http://localhost:8000/api/auth/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1234567890",
    "otp_code": "123456"
  }'
```

**Success Response (200):**
```json
{
  "detail": "OTP verified.",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "phone_number": "+1234567890"
  }
}
```

**Note:** 
- `access`: JWT access token (valid for 1 day) - use this for API authentication
- `refresh`: JWT refresh token (valid for 7 days) - use this to get a new access token when it expires
- Use the `access` token in the Authorization header as: `Authorization: Bearer <access_token>`

**Error Responses:**

**404 - OTP not requested:**
```bash
curl -X POST http://localhost:8000/api/auth/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+9999999999",
    "otp_code": "123456"
  }'
```
```json
{
  "detail": "OTP not requested for this phone number."
}
```

**400 - OTP expired:**
```json
{
  "detail": "OTP expired. Please request a new one."
}
```

**400 - Invalid OTP:**
```json
{
  "detail": "Invalid OTP code."
}
```

**Example with authentication token usage:**
After verifying OTP, you'll receive JWT tokens. Use the access token in subsequent requests:

```bash
# Store the access token from verify-otp response
ACCESS_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# Use the access token in authenticated requests
curl -X GET http://localhost:8000/api/some-protected-endpoint/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

**Refresh Token Usage:**
When the access token expires, use the refresh token to get a new access token:

```bash
# Store the refresh token
REFRESH_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# Get new access token
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d "{\"refresh\": \"$REFRESH_TOKEN\"}"
```

**Success Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## Complete Authentication Flow Example

Here's a complete example of the authentication flow:

```bash
# Step 1: Send OTP
curl -X POST http://localhost:8000/api/auth/send-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1234567890"
  }'

# Step 2: Verify OTP (use the OTP code received via SMS)
curl -X POST http://localhost:8000/api/auth/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1234567890",
    "otp_code": "123456"
  }'
```

---

## Django Admin

The Django admin interface is available at:

**URL:** `http://localhost:8000/admin/`

**Note:** This is a web interface, not an API endpoint. You'll need to:
1. Create a superuser: `python manage.py createsuperuser`
2. Log in via the web browser
3. Manage models through the admin interface

---

## Environment Variables Required

Make sure your `.env` file contains:

```env
# Twilio Configuration (required for OTP sending)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_MESSAGING_SERVICE_SID=your_messaging_service_sid
DEFAULT_FROM_PHONE_NUMBER=your_phone_number

# OTP Settings
OTP_EXPIRATION_MINUTES=5
```

---

## Testing Tips

### 1. Start the Django development server:
```bash
python manage.py runserver
```

### 2. Pretty-print JSON responses:
```bash
curl -X POST http://localhost:8000/api/auth/send-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890"}' | python -m json.tool
```

### 3. Save response to variable:
```bash
RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/send-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890"}')
echo $RESPONSE
```

### 4. Verbose output for debugging:
```bash
curl -v -X POST http://localhost:8000/api/auth/send-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890"}'
```

---

## Future Endpoints

The following endpoints are not yet implemented but could be added:

- **GET /api/finance/products/** - List all financial products
- **GET /api/finance/products/{id}/** - Get product details
- **POST /api/finance/products/** - Create a product (admin only)
- **PATCH /api/finance/products/{id}/** - Update a product (admin only)
- **DELETE /api/finance/products/{id}/** - Delete a product (admin only)

To implement these, you would need to:
1. Create serializers in `finance/serializers.py`
2. Create views in `finance/views.py`
3. Create URL patterns in `finance/urls.py`
4. Include finance URLs in `otp_service/urls.py`


