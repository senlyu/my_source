# Design Document: Key Manager Standalone Server (KMS)

## 1. Introduction
The Key Manager Standalone Server (KMS) is a centralized HTTP service designed to manage API keys, enforce rate limits, and provide a unified interface for LLM requests (starting with Gemini). By decoupling this from the main application, we enable better scalability, centralized resource management, and shared caching across multiple client instances.

## 2. Motivation
- **Decoupling:** Current logic is spread across `GeminiConnect` and `KeyManager`, mixing business logic (report generation) with infrastructure logic (key rotation).
- **Global Rate Limiting:** Multiple bot instances currently compete for the same keys without coordination, leading to `429 RESOURCE_EXHAUSTED` errors.
- **Shared Cache:** A centralized server allows multiple clients to benefit from a single cache, reducing costs and latency.
- **Resource Protection:** API keys are centralized in one secure environment rather than being distributed across all client deployments.

## 3. Architecture Overview

### 3.1 Components
- **HTTP API Layer (FastAPI):** Handles incoming requests and provides standardized JSON responses.
- **Key Manager Core:** An evolved version of the current `KeyManager` using `asyncio` to manage key rotation and wait-time logic.
- **Model Connector:** Standardized wrappers for calling LLM APIs (e.g., Google GenAI).
- **Caching Layer:** A file-based cache for storing model responses.
    - **Retention Policy:** Files are stored as `YYYY-MM-DD_hash.json`. A background cleanup process runs on server startup to delete files older than 30 days.

### 3.2 Request Flow
1. Client sends a POST request to KMS with `prompt`, `context`, and optional `model`.
2. KMS generates a hash of the request (prompt + context + model).
3. **Cache Check:** If a cached response exists and is valid, return it immediately.
4. **Key Selection:** If no cache, KMS waits for an available API key based on RPM (Requests Per Minute) limits.
5. **API Call:** KMS executes the request to the LLM provider.
6. **Persistence:** Response is cached.
7. **Response:** Cached or fresh result is returned to the client.

### 3.3 Project Structure
The KMS will reside in a standalone directory to ensure isolation from the main application.

```text
my_source/
├── kms/                # Centralized Key Manager Server
│   ├── main.py         # FastAPI Entrypoint
│   ├── key_manager.py  # Refactored rotation logic
│   ├── config.py       # KMS specific settings (API keys, RPM)
│   ├── Dockerfile      # Independent build context
│   └── requirements.txt
└── src/                # Existing bot logic
```

### 3.4 Deployment Strategy
- **Container Isolation:** KMS will run in its own Docker container, separate from the `my_source` bot runner. 
- **Rationale:** 
    - **Resource Independence:** KMS is an infrastructure utility that should remain alive even if the bot is restarting or updating.
    - **Dependency Decoupling:** KMS requires FastAPI/Uvicorn, which are not needed by the bot. This keeps the bot's image slim.
    - **Global Utility:** Other services (not just `my_source`) can eventually use the KMS for LLM access.

## 4. API Specification

### Endpoint: `POST /v1/chat/completions`

**Request Body:**
```json
{
  "prompt": "String: The primary instruction",
  "context": ["String array: Background data or history"],
  "model_type": "String: 'expensive' | 'standard' | 'flash' (optional)",
  "force_refresh": false
}
```

**Response Body (Success):**
```json
{
  "status": "success",
  "data": {
    "text": "The model response...",
    "usage": {
      "prompt_tokens": 123,
      "candidates_tokens": 456,
      "total_tokens": 579
    },
    "model_used": "gemini-2.0-flash",
    "cached": false
  },
  "error_code": "RESOURCE_EXHAUSTED | API_ERROR | KEY_ERROR | INTERNAL_ERROR",
  "error_text": "Detailed error message..."
}
```

## 5. Implementation Strategy

### 5.1 Technology Stack
- **Framework:** FastAPI (Python) for high-performance asynchronous handling.
- **Client (for testing/integration):** `httpx` is preferred over `requests` because the main application uses `asyncio`. `httpx` provides an async interface that prevents blocking the event loop during model calls.
- **Storage:** Initial implementation will use a local filesystem cache (similar to current `history/` logic).

### 5.2 Implementation Strategy
- **Phase 1 (Server):** Implement the FastAPI server with the existing `KeyManager` rotation logic.
- **Phase 2 (Validation):** Create `test-post.py` to simulate client requests and verify rate limiting, rotation, and caching.
- **Phase 3 (Integration):** (Deferred) Update the main application's `GeminiConnect` to call the KMS.

## 6. Benefits
- **Stability:** Clients won't crash due to uncoordinated rate limit hits.
- **Efficiency:** Parallel requests from `ReportJob` are queued and managed centrally.

## 7. Future Considerations
- **Monitoring:** Focused strictly on tracking **token usage per day** to manage costs and quotas.
- **Advanced Throttling:** Token-based bucket limits and Key Health monitoring (if keys start failing).
