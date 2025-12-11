# Test Account Feature - Phone: 999999999

## Overview

A special test account has been configured for testing onboarding and platform features. When a user logs in with phone number `999999999` (or `+999999999`), the system will:

1. **Delete the old user** and all related data completely
2. **Create a new user** for fresh testing
3. **Use default OTP** `000000` (no need to send via Twilio)

## Test Account Details

- **Phone Number**: `999999999` or `+999999999`
- **Default OTP**: `000000`
- **Alternative OTP**: `999999` (also accepted for backward compatibility)

## How It Works

### 1. Send OTP API

**Endpoint:** `POST /api/auth/send-otp/`

**Request:**
```bash
curl --location 'http://localhost:8000/api/auth/send-otp/' \
--header 'Content-Type: application/json' \
--data '{
    "phone_number": "999999999"
}'
```

**Response:**
```json
{
    "detail": "OTP sent (test account - OTP: 000000).",
    "otp_id": 123,
    "otp_code": "000000"
}
```

**Behavior:**
- Automatically sets OTP to `000000` (no random generation)
- Does NOT send OTP via Twilio (skips SMS)
- Returns OTP code in response for testing

### 2. Verify OTP API

**Endpoint:** `POST /api/auth/verify-otp/`

**Request:**
```bash
curl --location 'http://localhost:8000/api/auth/verify-otp/' \
--header 'Content-Type: application/json' \
--data '{
    "phone_number": "999999999",
    "otp_code": "000000"
}'
```

**Behavior:**
1. **Accepts OTP**: `000000` or `999999`
2. **Deletes Old User**: If a user with this phone number exists, it:
   - Deletes all chat data (sessions, messages, attachments)
   - Deletes all training data (progress, answers)
   - Deletes all finance data (questionnaire responses, UHFS scores, products, purchases, etc.)
   - Deletes all account data (face profiles, OTP records)
   - Deletes AWS Rekognition face data (if enrolled)
   - Finally deletes the user record
3. **Creates New User**: Creates a fresh user account with no data
4. **Returns JWT Tokens**: Normal login response with access and refresh tokens

**Response:**
```json
{
    "detail": "OTP verified.",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
        "id": "new-uuid-here",
        "phone_number": "+999999999",
        "full_name": null,
        "age": null,
        "gender": null,
        "state": null,
        "city_district": null
    },
    "onboarding": {
        "is_completed": false,
        "completed_steps": [],
        "completed_count": 0,
        "total_steps": 7,
        "next_step": "personal_demographic",
        "current_step": null,
        "progress_percentage": 0
    },
    "has_face_enrollment": false
}
```

## Complete Test Flow

### Step 1: Send OTP (Test Account)
```bash
curl --location 'http://localhost:8000/api/auth/send-otp/' \
--header 'Content-Type: application/json' \
--data '{
    "phone_number": "999999999"
}'
```

### Step 2: Verify OTP (Deletes Old User, Creates New)
```bash
curl --location 'http://localhost:8000/api/auth/verify-otp/' \
--header 'Content-Type: application/json' \
--data '{
    "phone_number": "999999999",
    "otp_code": "000000"
}'
```

### Step 3: Start Fresh Onboarding
Now you can test the complete onboarding flow with a fresh user account.

## What Gets Deleted

When logging in with test account, the following data is completely deleted:

1. **Chat Data**:
   - Chat attachments
   - Chat messages
   - Chat sessions

2. **Training Data**:
   - Training user answers
   - User training progress

3. **Finance Data**:
   - Personal demographic
   - Income employment
   - Income stability
   - Financial behavior
   - Reliability & tenure
   - Protection readiness
   - User financial literacy
   - UHFS scores
   - Product purchases
   - User products
   - Premium payments
   - Notifications
   - Onboarding progress

4. **Account Data**:
   - User face profiles
   - Phone OTP records
   - AWS Rekognition face data (if enrolled)

5. **User Record**: The user account itself

## Benefits

- **Fresh Testing**: Each login creates a completely fresh user
- **No Data Pollution**: Old test data doesn't interfere with new tests
- **Quick Reset**: No need to manually delete data or use admin commands
- **Easy Onboarding Testing**: Perfect for testing the complete onboarding flow repeatedly
- **No SMS Costs**: OTP is hardcoded, no Twilio charges

## Security Notes

⚠️ **Important**: This is a test-only feature. In production:
- Consider disabling this feature
- Or restrict it to specific environments (development/staging only)
- The test account should NOT be used in production

## Example: Complete Test Cycle

```bash
# 1. Send OTP
curl --location 'http://localhost:8000/api/auth/send-otp/' \
--header 'Content-Type: application/json' \
--data '{"phone_number": "999999999"}'

# 2. Verify OTP (creates fresh user)
curl --location 'http://localhost:8000/api/auth/verify-otp/' \
--header 'Content-Type: application/json' \
--data '{"phone_number": "999999999", "otp_code": "000000"}'

# 3. Complete onboarding (example - personal demographic)
curl --location 'http://localhost:8000/api/finance/personal-demographic/' \
--header 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
--header 'Content-Type: application/json' \
--data '{
    "full_name": "Test User",
    "age": 30,
    "gender": "Male",
    "state": "Maharashtra",
    "city_district": "Mumbai",
    "occupation_type": "Gig worker",
    "marital_status": "Single",
    "children": "No",
    "dependents": 0,
    "education_level": "Graduate"
}'

# 4. When done testing, login again to reset
curl --location 'http://localhost:8000/api/auth/verify-otp/' \
--header 'Content-Type: application/json' \
--data '{"phone_number": "999999999", "otp_code": "000000"}'
```

## Notes

- The test account accepts both `000000` and `999999` as OTP codes
- The phone number can be provided as `999999999` or `+999999999`
- All deletions happen in a database transaction (atomic)
- If any error occurs during deletion, the transaction is rolled back
- The new user is created with `is_active=True` and phone number set


## Overview

A special test account has been configured for testing onboarding and platform features. When a user logs in with phone number `999999999` (or `+999999999`), the system will:

1. **Delete the old user** and all related data completely
2. **Create a new user** for fresh testing
3. **Use default OTP** `000000` (no need to send via Twilio)

## Test Account Details

- **Phone Number**: `999999999` or `+999999999`
- **Default OTP**: `000000`
- **Alternative OTP**: `999999` (also accepted for backward compatibility)

## How It Works

### 1. Send OTP API

**Endpoint:** `POST /api/auth/send-otp/`

**Request:**
```bash
curl --location 'http://localhost:8000/api/auth/send-otp/' \
--header 'Content-Type: application/json' \
--data '{
    "phone_number": "999999999"
}'
```

**Response:**
```json
{
    "detail": "OTP sent (test account - OTP: 000000).",
    "otp_id": 123,
    "otp_code": "000000"
}
```

**Behavior:**
- Automatically sets OTP to `000000` (no random generation)
- Does NOT send OTP via Twilio (skips SMS)
- Returns OTP code in response for testing

### 2. Verify OTP API

**Endpoint:** `POST /api/auth/verify-otp/`

**Request:**
```bash
curl --location 'http://localhost:8000/api/auth/verify-otp/' \
--header 'Content-Type: application/json' \
--data '{
    "phone_number": "999999999",
    "otp_code": "000000"
}'
```

**Behavior:**
1. **Accepts OTP**: `000000` or `999999`
2. **Deletes Old User**: If a user with this phone number exists, it:
   - Deletes all chat data (sessions, messages, attachments)
   - Deletes all training data (progress, answers)
   - Deletes all finance data (questionnaire responses, UHFS scores, products, purchases, etc.)
   - Deletes all account data (face profiles, OTP records)
   - Deletes AWS Rekognition face data (if enrolled)
   - Finally deletes the user record
3. **Creates New User**: Creates a fresh user account with no data
4. **Returns JWT Tokens**: Normal login response with access and refresh tokens

**Response:**
```json
{
    "detail": "OTP verified.",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
        "id": "new-uuid-here",
        "phone_number": "+999999999",
        "full_name": null,
        "age": null,
        "gender": null,
        "state": null,
        "city_district": null
    },
    "onboarding": {
        "is_completed": false,
        "completed_steps": [],
        "completed_count": 0,
        "total_steps": 7,
        "next_step": "personal_demographic",
        "current_step": null,
        "progress_percentage": 0
    },
    "has_face_enrollment": false
}
```

## Complete Test Flow

### Step 1: Send OTP (Test Account)
```bash
curl --location 'http://localhost:8000/api/auth/send-otp/' \
--header 'Content-Type: application/json' \
--data '{
    "phone_number": "999999999"
}'
```

### Step 2: Verify OTP (Deletes Old User, Creates New)
```bash
curl --location 'http://localhost:8000/api/auth/verify-otp/' \
--header 'Content-Type: application/json' \
--data '{
    "phone_number": "999999999",
    "otp_code": "000000"
}'
```

### Step 3: Start Fresh Onboarding
Now you can test the complete onboarding flow with a fresh user account.

## What Gets Deleted

When logging in with test account, the following data is completely deleted:

1. **Chat Data**:
   - Chat attachments
   - Chat messages
   - Chat sessions

2. **Training Data**:
   - Training user answers
   - User training progress

3. **Finance Data**:
   - Personal demographic
   - Income employment
   - Income stability
   - Financial behavior
   - Reliability & tenure
   - Protection readiness
   - User financial literacy
   - UHFS scores
   - Product purchases
   - User products
   - Premium payments
   - Notifications
   - Onboarding progress

4. **Account Data**:
   - User face profiles
   - Phone OTP records
   - AWS Rekognition face data (if enrolled)

5. **User Record**: The user account itself

## Benefits

- **Fresh Testing**: Each login creates a completely fresh user
- **No Data Pollution**: Old test data doesn't interfere with new tests
- **Quick Reset**: No need to manually delete data or use admin commands
- **Easy Onboarding Testing**: Perfect for testing the complete onboarding flow repeatedly
- **No SMS Costs**: OTP is hardcoded, no Twilio charges

## Security Notes

⚠️ **Important**: This is a test-only feature. In production:
- Consider disabling this feature
- Or restrict it to specific environments (development/staging only)
- The test account should NOT be used in production

## Example: Complete Test Cycle

```bash
# 1. Send OTP
curl --location 'http://localhost:8000/api/auth/send-otp/' \
--header 'Content-Type: application/json' \
--data '{"phone_number": "999999999"}'

# 2. Verify OTP (creates fresh user)
curl --location 'http://localhost:8000/api/auth/verify-otp/' \
--header 'Content-Type: application/json' \
--data '{"phone_number": "999999999", "otp_code": "000000"}'

# 3. Complete onboarding (example - personal demographic)
curl --location 'http://localhost:8000/api/finance/personal-demographic/' \
--header 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
--header 'Content-Type: application/json' \
--data '{
    "full_name": "Test User",
    "age": 30,
    "gender": "Male",
    "state": "Maharashtra",
    "city_district": "Mumbai",
    "occupation_type": "Gig worker",
    "marital_status": "Single",
    "children": "No",
    "dependents": 0,
    "education_level": "Graduate"
}'

# 4. When done testing, login again to reset
curl --location 'http://localhost:8000/api/auth/verify-otp/' \
--header 'Content-Type: application/json' \
--data '{"phone_number": "999999999", "otp_code": "000000"}'
```

## Notes

- The test account accepts both `000000` and `999999` as OTP codes
- The phone number can be provided as `999999999` or `+999999999`
- All deletions happen in a database transaction (atomic)
- If any error occurs during deletion, the transaction is rolled back
- The new user is created with `is_active=True` and phone number set



