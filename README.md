# Jarvis AI Assistant

An AI desktop assistant with a Python FastAPI backend and React-based Electron frontend.

## Features

- Natural language chat using LLaMA
- Text-to-Speech using macOS 'say' command
- Speech-to-Text using Whisper
- Passive listening with wake word detection ("Hey Jarvis")

## Project Structure

```
jarvis/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── services/
│   │   └── utils/
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── styles/
│   │   └── utils/
│   └── package.json
└── docs/
    └── API.md
```

## Setup

### Backend

1. Create and activate virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

3. Set up environment variables in `.env`:

```
LLAMA_CPP_PATH=/path/to/llama.cpp
MODEL_PATH=/path/to/model.gguf
```

4. Start the backend server:

```bash
uvicorn app.main:app --reload
```

### Frontend

1. Install dependencies:

```bash
cd frontend
npm install
```

2. Start the development server:

```bash
npm start
```

## API Documentation

The API documentation is available in multiple formats:

1. **Interactive Documentation**:

   - Swagger UI: `http://localhost:8000/api/docs`
   - ReDoc: `http://localhost:8000/api/redoc`

2. **Markdown Documentation**:
   - See `docs/API.md` for comprehensive API documentation

## Development

- Backend API is built with FastAPI
- Frontend is built with React and Electron
- Uses Whisper for speech recognition
- Uses LLaMA for natural language processing
- Uses Porcupine for wake word detection

## License

MIT License - see LICENSE file for details
