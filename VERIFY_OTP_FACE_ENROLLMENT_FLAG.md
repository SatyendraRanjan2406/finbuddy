# Verify OTP API - Face Enrollment Flag

## Overview

The `verify-otp` and `face/login` APIs now return a `has_face_enrollment` flag indicating whether the user has enrolled for face authentication login.

## Updated Endpoints

### 1. Verify OTP API

**Endpoint:** `POST /api/auth/verify-otp/`

**Response now includes:**
```json
{
    "detail": "OTP verified.",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
        "id": "ae661a6b-1be4-4c5d-b571-13876308beba",
        "phone_number": "+919876543210",
        "full_name": "Rajesh Kumar",
        "age": 32,
        "gender": "Male",
        "state": "Maharashtra",
        "city_district": "Mumbai"
    },
    "onboarding": {
        "is_completed": false,
        "completed_steps": ["personal_demographic"],
        "completed_count": 1,
        "total_steps": 7,
        "next_step": "income_employment",
        "current_step": "income_employment",
        "progress_percentage": 14.29
    },
    "has_face_enrollment": true
}
```

### 2. Face Login API

**Endpoint:** `POST /api/auth/face/login/`

**Response now includes:**
```json
{
    "detail": "Face recognized successfully (similarity: 95.23%).",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
        "id": "ae661a6b-1be4-4c5d-b571-13876308beba",
        "phone_number": "+919876543210",
        "full_name": "Rajesh Kumar",
        "age": 32,
        "gender": "Male",
        "state": "Maharashtra",
        "city_district": "Mumbai"
    },
    "onboarding": {
        "is_completed": false,
        "completed_steps": ["personal_demographic"],
        "completed_count": 1,
        "total_steps": 7,
        "next_step": "income_employment",
        "current_step": "income_employment",
        "progress_percentage": 14.29
    },
    "has_face_enrollment": true,
    "face_match": {
        "similarity": 95.23,
        "face_id": "abc123-def456-ghi789"
    }
}
```

## Field Description

### `has_face_enrollment`

- **Type**: Boolean
- **Description**: Indicates whether the user has enrolled for face authentication login
- **Values**:
  - `true`: User has enrolled their face and can use face login
  - `false`: User has not enrolled their face yet

## Usage Examples

### Verify OTP - Check Face Enrollment Status

```bash
curl --location 'http://localhost:8000/api/auth/verify-otp/' \
--header 'Content-Type: application/json' \
--data '{
    "phone_number": "+919876543210",
    "otp_code": "123456"
}'
```

**Response:**
```json
{
    "detail": "OTP verified.",
    "access": "...",
    "refresh": "...",
    "user": {...},
    "onboarding": {...},
    "has_face_enrollment": false
}
```

If `has_face_enrollment` is `false`, the frontend can prompt the user to enroll their face.

### Face Login - Always Returns True

When a user successfully logs in via face recognition, `has_face_enrollment` will always be `true` since they must have enrolled to use this login method.

## Frontend Integration

The frontend can use this flag to:

1. **Show/Hide Face Login Option**: If `has_face_enrollment: false`, hide the face login button
2. **Prompt Enrollment**: After OTP login, if `has_face_enrollment: false`, show a prompt to enroll face
3. **Skip Enrollment Prompt**: If `has_face_enrollment: true`, skip enrollment prompts

### Example Frontend Logic

```javascript
// After verify-otp response
if (response.has_face_enrollment === false) {
    // Show enrollment prompt
    showFaceEnrollmentPrompt();
} else {
    // User already enrolled, show face login option
    enableFaceLoginButton();
}
```

## Notes

- The flag is based on `UserFaceProfile.is_enrolled` field
- If the user has not enrolled, `UserFaceProfile` may not exist, so the flag will be `false`
- The flag is checked in real-time, so it reflects the current enrollment status
- For `face/login` API, the flag will typically be `true` since the user must be enrolled to use face login

