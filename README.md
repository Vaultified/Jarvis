# AI Desktop Assistant

A modern desktop assistant built with Python (FastAPI) backend and React-based Electron frontend.

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/        # API endpoints
│   │   ├── core/       # Core functionality
│   │   ├── models/     # Data models
│   │   ├── services/   # Business logic
│   │   └── utils/      # Utility functions
│   ├── requirements.txt
│   └── .env
└── frontend/
    ├── src/
    │   ├── components/ # React components
    │   ├── pages/      # Page components
    │   ├── styles/     # CSS/styling
    │   └── utils/      # Frontend utilities
    └── package.json
```

## Setup Instructions

### Backend Setup

1. Create and activate virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Run the backend server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. Install dependencies:

   ```bash
   cd frontend
   npm install
   ```

2. Start development server:
   ```bash
   npm run dev
   ```

## Development

- Backend API runs on: http://localhost:8000
- Frontend dev server runs on: http://localhost:3000
- API documentation available at: http://localhost:8000/docs

## Building for Production

1. Build the frontend:

   ```bash
   cd frontend
   npm run build
   ```

2. Package the application:
   ```bash
   npm run package
   ```
