# Watson Chat API - Postman Collection Guide

This guide explains how to use the Postman collection for testing the IBM Watson-powered chat APIs.

## Files Included

1. **Watson_Chat_API.postman_collection.json** - Postman collection with all API endpoints
2. **Watson_Chat_API.postman_environment.json** - Postman environment variables

## Setup Instructions

### 1. Import Collection and Environment

1. Open Postman
2. Click **Import** button (top left)
3. Import both files:
   - `Watson_Chat_API.postman_collection.json`
   - `Watson_Chat_API.postman_environment.json`
4. Select the environment "FinMate Watson Chat API - Environment" from the dropdown (top right)

### 2. Configure Environment Variables

Update the following variables in the environment:

- **base_url**: Your API base URL (default: `http://localhost:8000`)
  - For production: `https://your-domain.com`
  - For staging: `https://staging.your-domain.com`

- **jwt_token**: Your JWT authentication token
  - Get this by logging in via `/api/auth/login/` endpoint
  - Copy the `access` token from the response
  - Paste it here (it will be automatically used in Authorization header)

- **session_id**: (Optional) Will be auto-populated after creating a session
  - You can manually set this if you want to continue an existing session

### 3. Get JWT Token

If you don't have a JWT token yet:

1. Use the authentication endpoint to login:
   ```bash
   POST /api/auth/login/
   Body: {
     "phone": "your_phone_number",
     "otp": "your_otp"
   }
   ```

2. Copy the `access` token from the response

3. Update the `jwt_token` variable in Postman environment

## Available Endpoints

### 1. Initialize Chat Session
**GET** `/api/ai_chat_watson/watson/init/`

- Creates a new chat session
- Calculates/retrieves UHFS score
- Fetches suggested products
- Returns session details

**Response includes:**
- Session ID (save this for subsequent requests)
- UHFS score and components
- Suggested products snapshot

### 2. Send Chat Message (JSON)
**POST** `/api/ai_chat_watson/watson/chat/`

**Request Body (JSON):**
```json
{
  "session_id": 1,  // Optional: omit to create new session
  "message": "I want to improve my UHFS score"
}
```

**Response includes:**
- Updated session details
- User message
- Watson assistant reply

### 3. Send Chat Message (Multipart with File)
**POST** `/api/ai_chat_watson/watson/chat/`

**Request (form-data):**
- `session_id`: (Optional) Existing session ID
- `message`: Your chat message text
- `file`: (Optional) File attachment

**Supported file types:**
- Images: `.jpg`, `.png`, `.gif`, etc.
- Documents: `.pdf`, `.doc`, `.docx`, etc.

### 4. Send Message (New Session)
**POST** `/api/ai_chat_watson/watson/chat/`

Same as endpoint #2, but omit `session_id` to automatically create a new session.

## Usage Workflow

### Basic Chat Flow

1. **Initialize Session**
   - Run "Watson Chat - Initialize Session"
   - Copy the `session.id` from response
   - Update `session_id` variable in environment (or use it directly in requests)

2. **Send Messages**
   - Use "Watson Chat - Send Message (JSON)" for text-only messages
   - Use "Watson Chat - Send Message (Multipart with File)" for messages with attachments
   - Continue using the same `session_id` to maintain conversation context

3. **Start New Conversation**
   - Omit `session_id` in request, or
   - Run "Initialize Session" again to get a new session

## Example cURL Commands

### Initialize Session
```bash
curl -X GET "http://localhost:8000/api/ai_chat_watson/watson/init/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Send Message
```bash
curl -X POST "http://localhost:8000/api/ai_chat_watson/watson/chat/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": 1,
    "message": "I want to improve my UHFS score"
  }'
```

### Send Message with File
```bash
curl -X POST "http://localhost:8000/api/ai_chat_watson/watson/chat/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "session_id=1" \
  -F "message=Can you review this document?" \
  -F "file=@/path/to/document.pdf"
```

## Response Examples

### Success Response (200 OK)
```json
{
  "session": {
    "id": 1,
    "title": "Watson chat 2025-01-15",
    "uhfs_score": 65,
    "uhfs_components": {...},
    "suggested_products_snapshot": [...]
  },
  "user_message": {
    "id": 1,
    "role": "user",
    "content": "Hello",
    "created_at": "2025-01-15T10:30:00Z"
  },
  "assistant_message": {
    "id": 2,
    "role": "assistant",
    "content": "Hello! How can I help you...",
    "created_at": "2025-01-15T10:30:01Z"
  }
}
```

### Error Responses

**404 - Session Not Found**
```json
{
  "error": "Session not found"
}
```

**400 - Validation Error**
```json
{
  "message": ["This field is required."]
}
```

**401 - Unauthorized**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

## Troubleshooting

### Authentication Issues
- Ensure JWT token is valid and not expired
- Check that token is properly set in environment variable
- Verify Authorization header format: `Bearer YOUR_TOKEN`

### Session Issues
- Session IDs are user-specific (cannot access other users' sessions)
- Sessions expire based on your Django session settings
- Create a new session if existing one is not found

### Watson API Issues
- Verify Watson Orchestration credentials are configured in Django settings:
  - `WATSON_ORCHESTRATION_API_KEY`
  - `WATSON_ORCHESTRATION_URL`
  - `WATSON_ORCHESTRATION_PROJECT_ID`
  - `WATSON_ORCHESTRATION_AGENT_ID`
- Check Django logs for Watson API errors

### File Upload Issues
- Ensure file size is within limits (check Django settings)
- Verify file type is supported
- Check S3/storage configuration if using file storage

## Additional Notes

- All endpoints require JWT authentication
- Sessions are user-specific and cannot be shared between users
- RAG (Retrieval-Augmented Generation) is automatically used when available
- UHFS scores are calculated/retrieved automatically for each user
- Suggested products are based on UHFS score

## Support

For issues or questions:
1. Check Django server logs
2. Verify Watson Orchestration API configuration
3. Review Postman console for request/response details
4. Ensure all environment variables are correctly set

