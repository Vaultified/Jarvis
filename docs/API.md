# Jarvis AI Assistant API Documentation

## Overview

The Jarvis AI Assistant API provides a comprehensive set of endpoints for natural language interaction, speech recognition, and text-to-speech capabilities. The API is built using FastAPI and provides both REST endpoints and WebSocket support for real-time communication.

## Base URL

```
http://localhost:8000/api
```

## Interactive Documentation

The API provides two interactive documentation interfaces:

- Swagger UI: `/api/docs`
- ReDoc: `/api/redoc`

## Authentication

Currently, the API does not require authentication. In production, you should implement proper authentication mechanisms.

## Endpoints

### Chat

#### POST /chat

Send a prompt to the LLaMA model and receive its response.

**Request Body:**

```json
{
  "prompt": "What is the capital of France?"
}
```

**Response:**

```json
{
  "response": "The capital of France is Paris."
}
```

### Text-to-Speech

#### POST /speak

Convert text to speech using macOS's `say` command.

**Request Body:**

```json
{
  "text": "Hello, I am Jarvis."
}
```

**Response:**

```json
{
  "status": "ok"
}
```

### Speech-to-Text (5-second Recording)

#### POST /listen

Record audio for 5 seconds and transcribe it using Whisper.

**Request Body:**
None required

**Response:**

```json
{
  "text": "Transcribed text from the audio recording"
}
```

### Passive Listening

#### POST /passive-listen

Listen for the wake word "Hey Jarvis" and then record until 2 seconds of silence.

**Request Body:**
None required

**Response:**

```json
{
  "text": "Transcribed text after wake word detection"
}
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- 200: Success
- 400: Bad Request
- 408: Request Timeout
- 500: Internal Server Error

Error responses include a detailed message:

```json
{
  "detail": "Error message description"
}
```

## Technical Details

### Audio Specifications

- Sample Rate: 16kHz
- Channels: 1 (Mono)
- Format: 16-bit PCM

### Models Used

- Whisper: "base" model for speech recognition
- LLaMA: For natural language processing
- Porcupine: For wake word detection

### Dependencies

- FastAPI
- Whisper
- SoundDevice
- NumPy
- macOS 'say' command (for TTS)

## Rate Limiting

Currently, there are no rate limits implemented. In production, you should implement appropriate rate limiting based on your requirements.

## CORS

CORS is enabled for all origins in development. In production, you should configure it to allow only specific origins.

## Health Check

#### GET /api/health

Check the API's health status.

**Response:**

```json
{
  "status": "healthy"
}
```

## Best Practices

1. Always handle errors appropriately in your client code
2. Implement retry logic for failed requests
3. Use appropriate timeouts for long-running operations
4. Monitor API response times and implement caching where appropriate

## Support

For issues and feature requests, please visit our GitHub repository: [Jarvis AI Assistant](https://github.com/yourusername/jarvis)
