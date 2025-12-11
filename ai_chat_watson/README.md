# ai_chat_watson

Watson-powered variant of the FinMate chatbot using IBM Watson AI Orchestration.

## Configuration
- `WATSON_ORCHESTRATION_API_KEY`
- `WATSON_ORCHESTRATION_URL` (e.g., `https://{region}.ai.cloud.ibm.com`)
- `WATSON_ORCHESTRATION_PROJECT_ID`
- `WATSON_ORCHESTRATION_AGENT_ID`

## Endpoints
- `GET /api/ai_chat_watson/watson/init/` — create a session and return UHFS + suggested products.
- `POST /api/ai_chat_watson/watson/chat/` — send a message (supports multipart for attachments).

## Notes
- RAG uses the existing `rag_index.jsonl` via `aichat.rag_retriever` if available.
- Schema mirrors the `aichat` app so existing UI flows can be reused.

