# Delete User Completely - Management Command Guide

## Overview

This management command completely deletes a user and all related records from all tables in the database, including:
- Account data (face profiles, OTP records)
- Finance data (questionnaire responses, UHFS scores, product purchases, etc.)
- Training data (progress, answers)
- Chat data (sessions, messages, attachments)
- AWS Rekognition face data (if enrolled)

## Usage

### Basic Usage

```bash
python manage.py delete_user_completely <username_or_phone_or_id>
```

### Options

- `--dry-run`: Preview what would be deleted without actually deleting
- `--skip-aws`: Skip AWS Rekognition face deletion (useful if AWS credentials are not available)

### Examples

#### Delete by Username
```bash
python manage.py delete_user_completely john_doe
```

#### Delete by Phone Number
```bash
python manage.py delete_user_completely +919876543210
```

#### Delete by User ID (UUID)
```bash
python manage.py delete_user_completely ae661a6b-1be4-4c5d-b571-13876308beba
```

#### Dry Run (Preview Only)
```bash
python manage.py delete_user_completely john_doe --dry-run
```

#### Skip AWS Rekognition
```bash
python manage.py delete_user_completely john_doe --skip-aws
```

## What Gets Deleted

The command deletes data in the following order to respect foreign key constraints:

### 1. AWS Rekognition Face Data
- Deletes face from AWS Rekognition collection (if enrolled)
- Deletes `UserFaceProfile` record

### 2. Chat Data
- `ChatAttachment` records (files attached to messages)
- `ChatMessage` records (all chat messages)
- `ChatSession` records (all chat sessions)

### 3. Training Data
- `TrainingUserAnswer` records (user's quiz answers)
- `UserTrainingProgress` records (training progress)

### 4. Finance Data
- `UserNotification` records
- `UserPremiumPayment` records (premium payments)
- `UserProduct` records (user's products)
- `ProductPurchase` records (purchase applications)
- `OnboardingProgress` records
- `UHFSScore` records
- `UserFinancialLiteracy` records
- `ProtectionReadiness` records
- `ReliabilityTenure` records
- `FinancialBehavior` records
- `IncomeStability` records
- `IncomeEmployment` records
- `PersonalDemographic` records

### 5. Account Data
- `UserFaceProfile` records
- `PhoneOTP` records (OTP verification records)

### 6. User Record
- Finally, the `User` record itself

## Example Output

```
============================================================
User to delete: john_doe
  ID: ae661a6b-1be4-4c5d-b571-13876308beba
  Phone: +919876543210
  Email: john@example.com
============================================================

✓ Deleted face from AWS Rekognition
✓ Deleted 5 chat attachment(s)
✓ Deleted 23 chat message(s)
✓ Deleted 3 chat session(s)
✓ Deleted 12 training answer(s)
✓ Deleted 5 training progress record(s)
✓ Deleted 2 notification(s)
✓ Deleted 4 premium payment(s)
✓ Deleted 2 user product(s)
✓ Deleted 1 product purchase(s)
✓ Deleted 1 onboarding progress record(s)
✓ Deleted 1 UHFS score(s)
✓ Deleted 1 financial literacy record(s)
✓ Deleted 1 protection readiness record(s)
✓ Deleted 1 reliability & tenure record(s)
✓ Deleted 1 financial behavior record(s)
✓ Deleted 1 income stability record(s)
✓ Deleted 1 income employment record(s)
✓ Deleted 1 personal demographic record(s)
✓ Deleted 1 face profile(s)
✓ Deleted 3 OTP record(s)
✓ Deleted User: john_doe

============================================================
DELETION SUMMARY
============================================================
  aws_rekognition_face: 1
  chat_attachments: 5
  chat_messages: 23
  chat_sessions: 3
  face_profiles: 1
  financialbehavior: 1
  incomeemployment: 1
  incomestability: 1
  onboardingprogress: 1
  personaldemographic: 1
  phone_otps: 3
  productpurchase: 1
  protectionreadiness: 1
  reliabilitytenure: 1
  training_answers: 12
  training_progress: 5
  uhfsscore: 1
  user: 1
  userfinancialliteracy: 1
  usernotification: 2
  userpremiumpayment: 4
  userproduct: 2
============================================================

✓ User john_doe and all related data deleted successfully!
```

## Safety Features

1. **Dry Run Mode**: Always test with `--dry-run` first to see what will be deleted
2. **Transaction Safety**: All deletions happen in a database transaction - if anything fails, nothing is deleted
3. **Detailed Logging**: Shows exactly what is being deleted
4. **Summary Report**: Provides a complete summary of all deleted records

## Important Notes

⚠️ **WARNING**: This operation is **IRREVERSIBLE**. Once a user is deleted, all their data is permanently removed.

- The command uses database transactions to ensure data integrity
- If any error occurs during deletion, the transaction is rolled back
- AWS Rekognition face deletion may fail if credentials are invalid - use `--skip-aws` if needed
- Some records may have `on_delete=models.SET_NULL` which means they won't be deleted but will have their user reference set to NULL

## Error Handling

If an error occurs:
- The transaction is rolled back
- No data is deleted
- An error message is displayed
- Check the error message for details

Common errors:
- **User not found**: Check the identifier (username, phone, or ID)
- **AWS credentials error**: Use `--skip-aws` flag
- **Database constraint error**: Check for any custom constraints or triggers

## Verification

After deletion, verify the user is completely removed:

```bash
# Using Django shell
python manage.py shell
>>> from accounts.models import User
>>> User.objects.filter(username='john_doe').exists()
False
```

## GDPR Compliance

This command helps with GDPR "Right to be Forgotten" compliance by:
- Completely removing all user data
- Deleting data from external services (AWS Rekognition)
- Providing audit trail through detailed logging
- Ensuring no orphaned records remain

