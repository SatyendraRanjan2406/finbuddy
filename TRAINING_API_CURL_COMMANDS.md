# Training API - cURL Commands Reference

This document provides cURL commands for all training-related APIs.

**Base URL:** `http://localhost:8000`

**Authentication:** Some endpoints require a JWT access token in the Authorization header:
```
Authorization: Bearer <your_access_token_here>
```

---

## Table of Contents

1. [Import Training Data from Google Sheets](#1-import-training-data-from-google-sheets)
2. [Get Training Sections List](#2-get-training-sections-list)
3. [Get Training Section Detail](#3-get-training-section-detail)
4. [Get User Training Progress](#4-get-user-training-progress)

---

## 1. Import Training Data from Google Sheets

Import training sections, questions, and options from Google Sheets. This endpoint reads from the configured Google Spreadsheet and populates the database.

**Endpoint:** `POST /api/training/import/`

**Authentication:** Required (Admin only)

**CURL Command:**
```bash
curl -X POST http://localhost:8000/api/training/import/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Training data imported successfully",
  "sections_created": 5,
  "questions_created": 25,
  "options_created": 100
}
```

**Error Response (400):**
```json
{
  "success": false,
  "message": "Error importing data: <error_message>"
}
```

**Note:**
- This endpoint requires admin authentication
- It reads from Google Sheets: `https://docs.google.com/spreadsheets/d/1gufHMamzNEWC9t1GvhqhDlBlr4LG8aNQ01sN839bGU8/edit`
- It clears all existing training data and replaces it with data from the spreadsheet
- The spreadsheet should have three sheets: `training_sections`, `training_questions`, `training_options`

---

## 2. Get Training Sections List

Get a list of all active training sections (without questions for better performance).

**Endpoint:** `GET /api/training/sections/`

**Authentication:** Not required (public endpoint)

**CURL Command:**
```bash
curl -X GET http://localhost:8000/api/training/sections/ \
  -H "Content-Type: application/json"
```

**Query Parameters (optional):**
- `language`: Filter by language (e.g., `?language=en`, `?language=hi`)
- `content_type`: Filter by content type (e.g., `?content_type=video`, `?content_type=text`)

**Examples with filters:**
```bash
# Get sections in English
curl -X GET "http://localhost:8000/api/training/sections/?language=en" \
  -H "Content-Type: application/json"

# Get video sections
curl -X GET "http://localhost:8000/api/training/sections/?content_type=video" \
  -H "Content-Type: application/json"

# Combine filters
curl -X GET "http://localhost:8000/api/training/sections/?language=en&content_type=video" \
  -H "Content-Type: application/json"
```

**Success Response (200):**
```json
{
  "count": 5,
  "sections": [
    {
      "id": 1,
      "title": "Basics of Banking",
      "description": "Understanding savings accounts & UPI",
      "content_type": "mixed",
      "language": "en",
      "video_url": "https://example.com/video.mp4",
      "audio_url": "https://example.com/audio.mp3",
      "text_content": "Banking basics content...",
      "is_active": true,
      "score": 10.0,
      "order": 1,
      "questions_count": 5,
      "available_content_types": ["video", "audio", "text"],
      "has_video": true,
      "has_audio": true,
      "has_text": true,
      "created_at": "2024-12-01T10:00:00Z",
      "updated_at": "2024-12-01T10:00:00Z"
    },
    {
      "id": 2,
      "title": "Digital Payments & Safety",
      "description": "Safe digital transactions",
      "content_type": "video",
      "language": "en",
      "video_url": "https://example.com/video.mp4",
      "audio_url": null,
      "text_content": null,
      "is_active": true,
      "score": 15.0,
      "order": 2,
      "questions_count": 3,
      "available_content_types": ["video"],
      "has_video": true,
      "has_audio": false,
      "has_text": false,
      "created_at": "2024-12-01T10:00:00Z",
      "updated_at": "2024-12-01T10:00:00Z"
    }
  ]
}
```

**Note:**
- A training section can have multiple content types simultaneously (video, audio, and/or text)
- `content_type` field shows the primary type or "mixed" if multiple types are present
- `available_content_types` array shows all content types available in the section
- `has_video`, `has_audio`, `has_text` are boolean flags indicating which content types are available

---

## 3. Get Training Section Detail

Get detailed information about a specific training section including all questions and options. Returns content in ordered array (video, text, audio) and questions with options for MCQ types.

**Endpoint:** `GET /api/training/sections/<id>/`

**Authentication:** Not required (public endpoint)

**CURL Command:**
```bash
curl -X GET http://localhost:8000/api/training/sections/1/ \
  -H "Content-Type: application/json"
```

**Success Response (200):**
```json
{
  "id": 1,
  "title": "Basics of Banking",
  "description": "Understanding savings accounts & UPI",
  "content_type": "mixed",
  "language": "en",
  "video_url": "https://example.com/video.mp4",
  "audio_url": "https://example.com/audio.mp3",
  "text_content": "Banking basics content...",
  "is_active": true,
  "score": 10.0,
  "order": 1,
  "questions_count": 5,
  "available_content_types": ["video", "audio", "text"],
  "has_video": true,
  "has_audio": true,
  "has_text": true,
  "ordered_content": [
    {
      "type": "video",
      "url": "https://example.com/video.mp4",
      "order": 1
    },
    {
      "type": "text",
      "content": "Banking basics content...",
      "order": 2
    },
    {
      "type": "audio",
      "url": "https://example.com/audio.mp3",
      "order": 3
    }
  ],
  "questions": [
    {
      "id": 1,
      "training": 1,
      "question_text": "What is a minimum balance?",
      "question_type": "mcq_single",
      "order": 1,
      "language": "en",
      "options": [
        {
          "id": 1,
          "option_text": "The maximum amount you can deposit",
          "is_correct": false,
          "created_at": "2024-12-01T10:00:00Z",
          "updated_at": "2024-12-01T10:00:00Z"
        },
        {
          "id": 2,
          "option_text": "The minimum amount you must keep in your account",
          "is_correct": true,
          "created_at": "2024-12-01T10:00:00Z",
          "updated_at": "2024-12-01T10:00:00Z"
        },
        {
          "id": 3,
          "option_text": "The interest rate on your account",
          "is_correct": false,
          "created_at": "2024-12-01T10:00:00Z",
          "updated_at": "2024-12-01T10:00:00Z"
        },
        {
          "id": 4,
          "option_text": "The transaction limit per day",
          "is_correct": false,
          "created_at": "2024-12-01T10:00:00Z",
          "updated_at": "2024-12-01T10:00:00Z"
        }
      ],
      "created_at": "2024-12-01T10:00:00Z",
      "updated_at": "2024-12-01T10:00:00Z"
    },
    {
      "id": 2,
      "training": 1,
      "question_text": "Which of the following are features of a savings account?",
      "question_type": "mcq_multiple",
      "order": 2,
      "language": "en",
      "options": [
        {
          "id": 5,
          "option_text": "Interest on deposits",
          "is_correct": true,
          "created_at": "2024-12-01T10:00:00Z",
          "updated_at": "2024-12-01T10:00:00Z"
        },
        {
          "id": 6,
          "option_text": "Unlimited withdrawals",
          "is_correct": false,
          "created_at": "2024-12-01T10:00:00Z",
          "updated_at": "2024-12-01T10:00:00Z"
        },
        {
          "id": 7,
          "option_text": "Debit card facility",
          "is_correct": true,
          "created_at": "2024-12-01T10:00:00Z",
          "updated_at": "2024-12-01T10:00:00Z"
        },
        {
          "id": 8,
          "option_text": "No minimum balance requirement",
          "is_correct": false,
          "created_at": "2024-12-01T10:00:00Z",
          "updated_at": "2024-12-01T10:00:00Z"
        }
      ],
      "created_at": "2024-12-01T10:00:00Z",
      "updated_at": "2024-12-01T10:00:00Z"
    },
    {
      "id": 3,
      "training": 1,
      "question_text": "Explain in your own words: Why is it important to maintain a minimum balance in your savings account?",
      "question_type": "input",
      "order": 3,
      "language": "en",
      "options": [],
      "created_at": "2024-12-01T10:00:00Z",
      "updated_at": "2024-12-01T10:00:00Z"
    },
    {
      "id": 4,
      "training": 1,
      "question_text": "Upload a screenshot of your UPI transaction history",
      "question_type": "file",
      "order": 4,
      "language": "en",
      "options": [],
      "created_at": "2024-12-01T10:00:00Z",
      "updated_at": "2024-12-01T10:00:00Z"
    }
  ],
  "created_at": "2024-12-01T10:00:00Z",
  "updated_at": "2024-12-01T10:00:00Z"
}
```

**Response Fields Explanation:**

- **`ordered_content`**: Array of content items in play order (video → text → audio)
  - Each item has: `type` (video/audio/text), `url` or `content`, and `order`
  - Use this array to play content in sequence

- **`questions`**: Array of questions with:
  - **`question_type`**: 
    - `mcq_single` - Single choice MCQ (options included)
    - `mcq_multiple` - Multiple choice MCQ (options included)
    - `input` - Text input question (no options)
    - `file` - File upload question (no options)
  - **`options`**: Array of options (only for MCQ types)
    - Each option has: `id`, `option_text`, `is_correct` (boolean)

**Error Response (404):**
```json
{
  "error": "Training section not found"
}
```

---

## 4. Get User Training Progress

Get training progress for the authenticated user.

**Endpoint:** `GET /api/training/progress/`

**Authentication:** Required

**CURL Command:**
```bash
curl -X GET http://localhost:8000/api/training/progress/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

---

## 5. Update Training Progress

Mark training progress (start, complete video, start questions, complete questions, etc.)

**Endpoint:** `POST /api/training/progress/`

**Authentication:** Required

### Start Training Section
```bash
curl -X POST http://localhost:8000/api/training/progress/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "training_id": 1,
    "action": "start"
  }'
```

### Mark Video as Completed
```bash
curl -X POST http://localhost:8000/api/training/progress/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "training_id": 1,
    "action": "video_completed",
    "current_video_index": 1
  }'
```

### Start Questions
```bash
curl -X POST http://localhost:8000/api/training/progress/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "training_id": 1,
    "action": "questions_started"
  }'
```

### Mark All Questions as Completed
```bash
curl -X POST http://localhost:8000/api/training/progress/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "training_id": 1,
    "action": "questions_completed"
  }'
```

### Complete Entire Training Section
```bash
curl -X POST http://localhost:8000/api/training/progress/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "training_id": 1,
    "action": "complete"
  }'
```

**Request Body Fields:**
- `training_id` (Integer, required): ID of the training section
- `action` (String, required): Action to perform
  - `"start"` - Start the training section
  - `"video_completed"` - Mark video as completed
  - `"questions_started"` - Mark questions as started
  - `"questions_completed"` - Mark all questions as completed
  - `"complete"` - Complete entire training section
- `current_video_index` (Integer, optional): Current video index (for video_completed action)
- `current_question_index` (Integer, optional): Current question index

**Success Response (200):**
```json
{
  "message": "Training started",
  "progress": {
    "id": 1,
    "user": "ae661a6b-1be4-4c5d-b571-13876308beba",
    "training": 1,
    "is_started": true,
    "videos_completed": false,
    "questions_started": false,
    "questions_completed": false,
    "current_question_index": 1,
    "score": 0.0,
    "is_completed": false
  }
}
```

---

## 6. Submit Training Answer

Submit answer to a training question (MCQ, input, or file upload).

**Endpoint:** `POST /api/training/submit-answer/`

**Authentication:** Required

### Submit MCQ Answer (Single Choice)
```bash
curl -X POST http://localhost:8000/api/training/submit-answer/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "training_id": 1,
    "question_id": 1,
    "selected_options": [2]
  }'
```

### Submit MCQ Answer (Multiple Choice)
```bash
curl -X POST http://localhost:8000/api/training/submit-answer/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "training_id": 1,
    "question_id": 2,
    "selected_options": [5, 7]
  }'
```

### Submit Text Input Answer
```bash
curl -X POST http://localhost:8000/api/training/submit-answer/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "training_id": 1,
    "question_id": 3,
    "input_text": "Digital banking allows me to manage my finances 24/7 from anywhere."
  }'
```

### Submit File Upload Answer
```bash
curl -X POST http://localhost:8000/api/training/submit-answer/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -F "training_id=1" \
  -F "question_id=4" \
  -F "uploaded_file=@/path/to/file.pdf"
```

**Request Body Fields:**
- `training_id` (Integer, required): ID of the training section
- `question_id` (Integer, required): ID of the question
- `selected_options` (Array of Integers, optional): Selected option IDs (for MCQ questions)
- `input_text` (String, optional): Text input (for input type questions)
- `uploaded_file` (File, optional): File upload (for file type questions)

**Success Response (200):**
```json
{
  "message": "Answer submitted successfully",
  "is_correct": true,
  "answer_id": 1,
  "progress": {
    "id": 1,
    "user": "ae661a6b-1be4-4c5d-b571-13876308beba",
    "training": 1,
    "is_started": true,
    "questions_started": true,
    "questions_completed": false,
    "current_question_index": 2,
    "score": 3.33,
    "is_completed": false
  }
}
```

**Success Response (200):**
```json
{
  "count": 2,
  "progress": [
    {
      "id": 1,
      "user": "ae661a6b-1be4-4c5d-b571-13876308beba",
      "training": 1,
      "training_details": {
        "id": 1,
        "title": "Basics of Banking",
        "description": "Understanding savings accounts & UPI",
        "content_type": "text",
        "language": "en",
        "questions_count": 5
      },
      "current_video_index": 1,
      "videos_completed": false,
      "questions_started": true,
      "questions_completed": false,
      "total_questions": 5,
      "current_question_index": 3,
      "score": 0.0,
      "is_started": true,
      "is_completed": false,
      "score_added_to_uhfs": false,
      "created_at": "2024-12-01T10:00:00Z",
      "updated_at": "2024-12-01T11:00:00Z"
    }
  ]
}
```

---

## Complete Workflow Example

### Step 1: Import Training Data (Admin Only)
```bash
# First, get admin access token
curl -X POST http://localhost:8000/api/auth/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1234567890",
    "otp_code": "123456"
  }'

# Extract access token from response and set it
export ACCESS_TOKEN="your_access_token_here"

# Import training data from Google Sheets
curl -X POST http://localhost:8000/api/training/import/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

### Step 2: Get All Training Sections
```bash
curl -X GET http://localhost:8000/api/training/sections/ \
  -H "Content-Type: application/json"
```

### Step 3: Get Specific Training Section with Questions
```bash
curl -X GET http://localhost:8000/api/training/sections/1/ \
  -H "Content-Type: application/json"
```

### Step 4: Start Training Section
```bash
curl -X POST http://localhost:8000/api/training/progress/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "training_id": 1,
    "action": "start"
  }'
```

### Step 5: Mark Video as Completed
```bash
curl -X POST http://localhost:8000/api/training/progress/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "training_id": 1,
    "action": "video_completed",
    "current_video_index": 1
  }'
```

### Step 6: Start Questions
```bash
curl -X POST http://localhost:8000/api/training/progress/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "training_id": 1,
    "action": "questions_started"
  }'
```

### Step 7: Submit Answers to Questions
```bash
# Submit MCQ single choice answer
curl -X POST http://localhost:8000/api/training/submit-answer/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "training_id": 1,
    "question_id": 1,
    "selected_options": [2]
  }'

# Submit MCQ multiple choice answer
curl -X POST http://localhost:8000/api/training/submit-answer/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "training_id": 1,
    "question_id": 2,
    "selected_options": [5, 7]
  }'

# Submit text input answer
curl -X POST http://localhost:8000/api/training/submit-answer/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "training_id": 1,
    "question_id": 3,
    "input_text": "My answer here..."
  }'
```

### Step 8: Complete Training Section
```bash
curl -X POST http://localhost:8000/api/training/progress/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "training_id": 1,
    "action": "complete"
  }'
```

### Step 9: Get User Progress
```bash
curl -X GET http://localhost:8000/api/training/progress/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

---

## Notes

1. **Google Sheets Structure:**
   The import endpoint expects three sheets in the Google Spreadsheet:
   - `training_sections`: Contains section data (id, title, description, content_type, language, etc.)
   - `training_questions`: Contains question data (id, training_id, question_text, question_type, order, language)
   - `training_options`: Contains option data (id, question_id, option_text, is_correct)

2. **Service Account File:**
   The import endpoint requires a Google Service Account JSON file at:
   `{BASE_DIR}/graphic-mason-479110-d6-a120ba88825f.json`

3. **Question Types:**
   - `mcq_single`: Single choice multiple choice question
   - `mcq_multiple`: Multiple choice question (can select multiple options)
   - `input`: Text input question
   - `file`: File upload question

4. **Content Types:**
   - A training section can have **multiple content types** simultaneously (video, audio, and/or text)
   - `content_type` field can be: `video`, `audio`, `text`, or `mixed` (when multiple types are present)
   - The API response includes:
     - `available_content_types`: Array of all content types in the section (e.g., `["video", "audio", "text"]`)
     - `has_video`, `has_audio`, `has_text`: Boolean flags indicating which content types are available
   - All three fields (`video_url`, `audio_url`, `text_content`) can be populated in a single section

5. **Base URL:** Replace `http://localhost:8000` with your actual server URL in production.

