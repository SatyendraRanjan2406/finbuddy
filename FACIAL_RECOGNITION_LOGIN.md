# Facial Recognition Login with AWS Rekognition

## Overview

Facial recognition login has been added to the FinMate app using AWS Rekognition. **This feature is fully backward compatible** - users can still use OTP phone login, or they can enroll their face and use facial recognition login.

## Architecture

### Database Changes

- **New Model**: `UserFaceProfile`
  - Stores AWS Rekognition face ID
  - Links to `User` via OneToOne relationship
  - Tracks enrollment status and timestamps
  - Optional `phone_number` field for lookup during face login

### Backward Compatibility

- ✅ **OTP login still works** - existing `/api/auth/send-otp` and `/api/auth/verify-otp` endpoints unchanged
- ✅ **Users can choose** - enroll face OR continue using OTP
- ✅ **No breaking changes** - existing OTP flow remains identical

## Setup

### 1. AWS Rekognition Configuration

Ensure these are set in your `.env` or `settings.py`:

```python
AWS_ACCESS_KEY_ID = "your-access-key"
AWS_SECRET_ACCESS_KEY = "your-secret-key"
AWS_S3_REGION_NAME = "ap-south-1"  # or your preferred region
```

### 2. Run Migration

```bash
python manage.py migrate accounts
```

This creates the `UserFaceProfile` table.

### 3. AWS Rekognition Collection

The collection `"finmate-users"` is automatically created on first face enrollment. No manual setup needed.

## API Endpoints

### 1. Face Enrollment (Register Face)

**POST** `/api/auth/face/enroll/`

**Authentication**: Required (user must be logged in via OTP first)

**Request** (multipart/form-data):
```
face_image: <image file> (JPEG/PNG, max 15MB)
phone_number: <optional string>
```

**Response** (200 OK):
```json
{
  "detail": "Face enrolled successfully. You can now login using facial recognition.",
  "face_profile": {
    "is_enrolled": true,
    "enrolled_at": "2024-01-15T10:30:00Z"
  }
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8000/api/auth/face/enroll/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "face_image=@/path/to/face.jpg" \
  -F "phone_number=+1234567890"
```

### 2. Face Login (Authenticate with Face)

**POST** `/api/auth/face/login/`

**Authentication**: Not required (this is the login endpoint)

**Request** (multipart/form-data):
```
face_image: <image file> (JPEG/PNG, max 15MB)
phone_number: <optional string> (for additional verification)
```

**Response** (200 OK):
```json
{
  "detail": "Face recognized successfully (similarity: 95.23%).",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "uuid-here",
    "phone_number": "+1234567890"
  },
  "onboarding": { ... },
  "face_match": {
    "similarity": 95.23,
    "face_id": "rekognition-face-id"
  }
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8000/api/auth/face/login/ \
  -F "face_image=@/path/to/face.jpg" \
  -F "phone_number=+1234567890"
```

## User Flow

### Option 1: OTP Login (Existing, Unchanged)
1. User requests OTP: `POST /api/auth/send-otp`
2. User verifies OTP: `POST /api/auth/verify-otp`
3. Receives JWT tokens

### Option 2: Face Login (New)
1. **First time**: User logs in via OTP, then enrolls face: `POST /api/auth/face/enroll/`
2. **Subsequent logins**: User uploads face image: `POST /api/auth/face/login/`
3. Receives JWT tokens (same format as OTP login)

### Option 3: Hybrid (User Choice)
- User can enroll face but still use OTP login anytime
- User can use face login if enrolled, or fall back to OTP

## Technical Details

### AWS Rekognition Operations

1. **Collection Management**
   - Collection ID: `"finmate-users"`
   - Auto-created on first enrollment
   - One collection for all users

2. **Face Indexing** (Enrollment)
   - Uses `index_faces` API
   - Stores face with `ExternalImageId` = user UUID
   - Returns `FaceId` stored in `UserFaceProfile.rekognition_face_id`

3. **Face Search** (Login)
   - Uses `search_faces_by_image` API
   - 80% similarity threshold (configurable)
   - Returns matched `FaceId` and similarity score

4. **Face Deletion**
   - When re-enrolling, old face is deleted from Rekognition
   - Prevents duplicate faces per user

### Security Considerations

- **Face Match Threshold**: 80% (configurable in `search_face_in_rekognition`)
- **Image Validation**: Max 15MB, JPEG/PNG only
- **Phone Verification**: Optional phone number check during face login
- **JWT Tokens**: Same token format as OTP login (fully compatible)

### Error Handling

- **No face detected**: Returns 400 with clear message
- **Face not recognized**: Returns 401 (user not enrolled or wrong face)
- **Image too large**: Returns 400 with size limit info
- **Invalid format**: Returns 400 with allowed formats
- **AWS errors**: Logged and returned as user-friendly messages

## Database Schema

```python
UserFaceProfile:
  - user (OneToOne to User, nullable for backward compat)
  - rekognition_face_id (CharField, unique)
  - collection_id (CharField, default="finmate-users")
  - is_enrolled (Boolean, default=False)
  - enrolled_at (DateTime, nullable)
  - phone_number (CharField, nullable, indexed)
  - created_at, updated_at (auto timestamps)
```

## Testing

### Test Face Enrollment
```bash
# 1. Login via OTP first
curl -X POST http://localhost:8000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890", "otp_code": "123456"}'

# 2. Use access token to enroll face
curl -X POST http://localhost:8000/api/auth/face/enroll/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "face_image=@test_face.jpg"
```

### Test Face Login
```bash
curl -X POST http://localhost:8000/api/auth/face/login/ \
  -F "face_image=@test_face.jpg" \
  -F "phone_number=+1234567890"
```

## Notes

- **Backward Compatible**: All existing OTP endpoints work exactly as before
- **Optional Feature**: Users are not forced to enroll face
- **Same JWT Format**: Face login returns same token structure as OTP login
- **Onboarding Progress**: Face login includes onboarding details (same as OTP)
- **Phone Lookup**: Optional phone number can be used to narrow down face search

