# EVA-Dev API Documentation

EVA-Dev provides a RESTful API for voice-enabled EV charging support. The API is built with FastAPI and includes comprehensive OpenAPI documentation.

## Base URLs

- **Development**: `http://localhost:8000`
- **Production**: `https://api.fixverse.se`

## Authentication

Currently, the API uses rate limiting but does not require authentication. Future versions may include API key authentication.

## Rate Limiting

- **General endpoints**: 60 requests per minute per IP
- **Voice endpoints**: 10 requests per minute per IP (due to processing overhead)

## API Endpoints

### Health Check

#### GET /health
Basic health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "environment": "production",
  "version": "1.0.0"
}
```

#### GET /api/v1/health/detailed
Detailed health check with service status.

**Response:**
```json
{
  "status": "healthy",
  "environment": "production",
  "version": "1.0.0",
  "services": {
    "api": "healthy",
    "azure_speech": "healthy",
    "claude_api": "healthy",
    "redis": "healthy"
  }
}
```

### Chat Endpoints

#### POST /api/v1/chat
Send a text message and receive a response from EVA-Dev.

**Request Body:**
```json
{
  "message": "How do I troubleshoot a CCS charging issue?",
  "session_id": "optional-session-id",
  "stream": false
}
```

**Response:**
```json
{
  "response": "To troubleshoot a CCS charging issue, first check...",
  "session_id": "uuid-session-id",
  "message_id": "uuid-message-id"
}
```

#### POST /api/v1/chat/stream
Send a text message and receive a streaming response.

**Request Body:**
```json
{
  "message": "Explain Level 2 charging",
  "session_id": "optional-session-id",
  "stream": true
}
```

**Response:** Server-Sent Events (SSE) stream
```
data: Level 2 charging is...
data: It typically provides...
data: [DONE]
```

#### GET /api/v1/chat/history/{session_id}
Retrieve chat history for a session.

**Response:**
```json
[
  {
    "id": "msg-uuid",
    "role": "user",
    "content": "What is CCS?",
    "timestamp": "2024-01-01T12:00:00Z",
    "type": "text"
  },
  {
    "id": "msg-uuid",
    "role": "assistant", 
    "content": "CCS stands for Combined Charging System...",
    "timestamp": "2024-01-01T12:00:01Z",
    "type": "text"
  }
]
```

#### DELETE /api/v1/chat/history/{session_id}
Clear chat history for a session.

**Response:**
```json
{
  "message": "Chat history cleared successfully"
}
```

### Voice Endpoints

#### POST /api/v1/voice/speech-to-text
Convert audio to text using Azure Speech Services.

**Request:** Multipart form data
- `audio_file`: Audio file (WAV, MP3, WebM, OGG)

**Response:**
```json
{
  "transcription": "How do I charge my Tesla at a CCS station?",
  "confidence": 0.95,
  "language": "en-US"
}
```

#### POST /api/v1/voice/text-to-speech
Convert text to speech audio.

**Request Body:**
```json
{
  "text": "Level 2 charging provides AC power at 240V",
  "voice": "en-US-AriaNeural"
}
```

**Response:** Audio file (WAV format)

#### POST /api/v1/voice/voice-chat
Complete voice interaction: speech-to-text, AI response, text-to-speech.

**Request Body:**
```json
{
  "audio_data": "base64-encoded-audio-data",
  "session_id": "optional-session-id",
  "format": "webm"
}
```

**Response:**
```json
{
  "transcription": "What's the difference between CCS1 and CCS2?",
  "response_text": "CCS1 and CCS2 are different versions...",
  "response_audio": "base64-encoded-audio-response",
  "session_id": "uuid-session-id",
  "message_id": "uuid-message-id"
}
```

#### GET /api/v1/voice/test-services
Test voice service connectivity.

**Response:**
```json
{
  "azure_speech": "healthy",
  "claude_api": "healthy",
  "overall_status": "healthy"
}
```

## Error Handling

The API uses standard HTTP status codes and returns detailed error information.

### Error Response Format
```json
{
  "error": "Error description",
  "code": "ERROR_CODE",
  "details": {
    "additional": "information"
  }
}
```

### Common Status Codes

- **200**: Success
- **400**: Bad Request (invalid input)
- **429**: Too Many Requests (rate limited)
- **500**: Internal Server Error
- **503**: Service Unavailable

### Error Examples

#### Rate Limit Exceeded
```json
{
  "error": "Rate limit exceeded",
  "code": "RATE_LIMIT_EXCEEDED",
  "details": {
    "limit": "60 requests per minute",
    "retry_after": 30
  }
}
```

#### Invalid Audio Format
```json
{
  "error": "Invalid audio file type",
  "code": "INVALID_AUDIO_FORMAT",
  "details": {
    "supported_formats": ["wav", "mp3", "webm", "ogg"]
  }
}
```

## Audio Requirements

### Supported Formats
- **Input**: WAV, MP3, WebM, OGG
- **Output**: WAV (16kHz, 16-bit, mono)

### Limitations
- **Max file size**: 10MB
- **Max duration**: 60 seconds
- **Sample rate**: Automatically converted to 16kHz

## Session Management

Sessions are managed automatically using Redis for storage:

- **Session duration**: 1 hour of inactivity
- **Session ID**: UUID format
- **Storage**: Conversation history and context

## WebSocket Support

Real-time communication is supported for streaming responses:

**Connection:** `wss://api.fixverse.se/ws`

**Message Format:**
```json
{
  "type": "chat_message",
  "data": {
    "message": "Your question here",
    "session_id": "optional-session-id"
  }
}
```

## SDK Examples

### Python
```python
import requests

# Text chat
response = requests.post(
    "https://api.fixverse.se/api/v1/chat",
    json={
        "message": "How do I use a CHAdeMO connector?",
        "session_id": "my-session"
    }
)
print(response.json()["response"])

# Voice chat
with open("audio.wav", "rb") as f:
    response = requests.post(
        "https://api.fixverse.se/api/v1/voice/speech-to-text",
        files={"audio_file": f}
    )
print(response.json()["transcription"])
```

### JavaScript
```javascript
// Text chat
const response = await fetch('https://api.fixverse.se/api/v1/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'What is Type 2 charging?',
    session_id: 'my-session'
  })
});
const data = await response.json();
console.log(data.response);

// Streaming chat
const response = await fetch('https://api.fixverse.se/api/v1/chat/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'Explain DC fast charging',
    stream: true
  })
});

const reader = response.body.getReader();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const chunk = new TextDecoder().decode(value);
  console.log(chunk);
}
```

### cURL
```bash
# Text chat
curl -X POST "https://api.fixverse.se/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I charge at a Tesla Supercharger?"}'

# Voice transcription
curl -X POST "https://api.fixverse.se/api/v1/voice/speech-to-text" \
  -F "audio_file=@recording.wav"

# Health check
curl "https://api.fixverse.se/health"
```

## Interactive Documentation

When running in development mode, interactive API documentation is available at:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

These interfaces allow you to test API endpoints directly from your browser.

## Changelog

### v1.0.0
- Initial release
- Text and voice chat capabilities
- Azure Speech Services integration
- Claude AI integration
- Session management
- Rate limiting
- Health monitoring
