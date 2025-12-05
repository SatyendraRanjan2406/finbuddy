# Delete User Completely - API Documentation

## Overview

API endpoint to completely delete a user and all related records from all tables. This is an **admin-only** endpoint for security.

## Endpoint

**POST** `/api/auth/delete-user-cascade/`

## Authentication

**Required**: Admin user with valid JWT token

**Permission**: `IsAdminUser` - Only admin users can delete users

## Request Body

```json
{
    "identifier": "username_or_phone_or_id",
    "skip_aws": false  // optional, default: false
}
```

### Parameters

- **identifier** (required): Username, phone number, or user ID (UUID)
- **skip_aws** (optional): Boolean, skip AWS Rekognition face deletion (default: false)

## Response

### Success Response (200 OK)

```json
{
    "success": true,
    "message": "User john_doe and all related data deleted successfully",
    "deleted_user": {
        "username": "john_doe",
        "id": "ae661a6b-1be4-4c5d-b571-13876308beba",
        "phone": "+919876543210"
    },
    "deletion_summary": {
        "aws_rekognition_face": 1,
        "chat_attachments": 5,
        "chat_messages": 23,
        "chat_sessions": 3,
        "face_profiles": 1,
        "financial_behavior": 1,
        "financial_literacy": 1,
        "income_employment": 1,
        "income_stability": 1,
        "notifications": 2,
        "onboarding_progress": 1,
        "personal_demographic": 1,
        "phone_otps": 3,
        "premium_payments": 4,
        "product_purchases": 1,
        "protection_readiness": 1,
        "reliability_tenure": 1,
        "training_answers": 12,
        "training_progress": 5,
        "uhfs_scores": 1,
        "user": 1,
        "user_products": 2
    },
    "warnings": []  // optional, if any warnings occurred
}
```

### Error Responses

#### User Not Found (404)

```json
{
    "error": "User not found: invalid_username"
}
```

#### Unauthorized (401)

```json
{
    "detail": "Authentication credentials were not provided."
}
```

#### Forbidden (403)

```json
{
    "detail": "You do not have permission to perform this action."
}
```

#### Server Error (500)

```json
{
    "error": "Failed to delete user",
    "message": "Detailed error message",
    "partial_deletion": {
        // Records that were deleted before error occurred
    }
}
```

## Curl Examples

### Delete User by Username

```bash
curl --location 'http://localhost:8000/api/auth/delete-user-cascade/' \
--header 'Authorization: Bearer YOUR_ADMIN_JWT_TOKEN' \
--header 'Content-Type: application/json' \
--data '{
    "identifier": "john_doe"
}'
```

### Delete User by Phone Number

```bash
curl --location 'http://localhost:8000/api/auth/delete-user-cascade/' \
--header 'Authorization: Bearer YOUR_ADMIN_JWT_TOKEN' \
--header 'Content-Type: application/json' \
--data '{
    "identifier": "+919876543210"
}'
```

### Delete User by UUID

```bash
curl --location 'http://localhost:8000/api/auth/delete-user-cascade/' \
--header 'Authorization: Bearer YOUR_ADMIN_JWT_TOKEN' \
--header 'Content-Type: application/json' \
--data '{
    "identifier": "ae661a6b-1be4-4c5d-b571-13876308beba"
}'
```

### Delete User and Skip AWS Rekognition

```bash
curl --location 'http://localhost:8000/api/auth/delete-user-cascade/' \
--header 'Authorization: Bearer YOUR_ADMIN_JWT_TOKEN' \
--header 'Content-Type: application/json' \
--data '{
    "identifier": "john_doe",
    "skip_aws": true
}'
```

## What Gets Deleted

The API deletes data in the following order:

1. **AWS Rekognition Face Data** (if enrolled and `skip_aws=false`)
2. **Chat Data**: Attachments → Messages → Sessions
3. **Training Data**: Answers → Progress
4. **Finance Data**: 
   - Notifications
   - Premium Payments
   - User Products
   - Product Purchases
   - Onboarding Progress
   - UHFS Scores
   - Financial Literacy
   - Protection Readiness
   - Reliability & Tenure
   - Financial Behavior
   - Income Stability
   - Income Employment
   - Personal Demographic
5. **Account Data**: Face Profiles → OTP Records
6. **User Record**: Finally, the user itself

## Security Features

1. **Admin-Only**: Only users with `is_staff=True` can access this endpoint
2. **Transaction Safety**: All deletions happen in a database transaction
3. **Error Handling**: If any error occurs, the transaction is rolled back
4. **Detailed Logging**: All operations are logged for audit purposes

## Important Notes

⚠️ **WARNING**: This operation is **IRREVERSIBLE**. Once a user is deleted, all their data is permanently removed.

- The API uses database transactions to ensure data integrity
- If any error occurs during deletion, the transaction is rolled back
- AWS Rekognition face deletion may fail if credentials are invalid - use `skip_aws=true` if needed
- The endpoint returns a detailed summary of all deleted records

## GDPR Compliance

This API helps with GDPR "Right to be Forgotten" compliance by:
- Completely removing all user data
- Deleting data from external services (AWS Rekognition)
- Providing audit trail through detailed response
- Ensuring no orphaned records remain

## Testing

### Test with Admin User

1. **Get Admin JWT Token**:
```bash
# Login as admin user first
curl --location 'http://localhost:8000/api/auth/verify-otp/' \
--header 'Content-Type: application/json' \
--data '{
    "phone_number": "+919876543210",
    "otp_code": "123456"
}'
```

2. **Delete User**:
```bash
curl --location 'http://localhost:8000/api/auth/delete-user-cascade/' \
--header 'Authorization: Bearer YOUR_ADMIN_TOKEN' \
--header 'Content-Type: application/json' \
--data '{
    "identifier": "test_user"
}'
```

### Verify Deletion

```bash
# Try to get user (should return 404)
curl --location 'http://localhost:8000/api/auth/verify-otp/' \
--header 'Content-Type: application/json' \
--data '{
    "phone_number": "+919876543210",
    "otp_code": "123456"
}'
```

## Error Scenarios

### Scenario 1: Non-Admin User
```json
{
    "detail": "You do not have permission to perform this action."
}
```
**Solution**: Use an admin user account

### Scenario 2: User Not Found
```json
{
    "error": "User not found: invalid_username"
}
```
**Solution**: Check the identifier (username, phone, or UUID)

### Scenario 3: AWS Credentials Error
```json
{
    "success": true,
    "message": "User deleted successfully",
    "warnings": [
        "Could not delete from AWS Rekognition: An error occurred..."
    ]
}
```
**Solution**: Use `skip_aws: true` in the request, or fix AWS credentials

## Related Commands

For command-line usage, see the management command:
```bash
python manage.py delete_user_completely <identifier> [--dry-run] [--skip-aws]
```

