# Jarvis - Local LLM Assistant with Gmail Integration

Jarvis is an AI assistant that runs locally using LLaMA 2, featuring Gmail integration through an MCP (Model-Controller-Provider) server architecture. The system allows natural language interaction for sending emails and will soon support Google Drive file operations.

## Features

### Current Features

- **Local LLM Integration**

  - Runs LLaMA 2 model locally for privacy and offline use
  - Natural language processing for chat interactions
  - Customizable model parameters and response generation

- **Gmail Integration**
  - MCP server architecture for email operations
  - Natural language email commands
  - Secure OAuth2 authentication
  - Real-time email status feedback
  - Support for multiple email formats:
    ```
    send email to example@email.com "Subject" "Message"
    send an email to example@email.com with subject "Subject" saying "Message"
    ```

### Coming Soon

- **Google Drive Integration**
  - File access and management through natural language
  - Document search and retrieval
  - File sharing capabilities
  - Folder organization

## Technical Architecture

### Frontend

- React-based chat interface
- Real-time message updates
- Gmail command processing
- Visual feedback for email operations

### Backend

- FastAPI server
- LLaMA 2 model integration
- MCP server for Gmail operations
- OAuth2 authentication

### Components

1. **Chat System**

   - Natural language processing
   - Command recognition
   - Response generation

2. **Gmail Service**

   - MCP server implementation
   - Email sending capabilities
   - Status tracking and error handling

3. **Authentication**
   - Google OAuth2 integration
   - Secure token management
   - Automatic token refresh

## Setup

### Prerequisites

- Python 3.8+
- Node.js 14+
- Google Cloud Platform account
- LLaMA 2 model files

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/jarvis.git
   cd jarvis
   ```

2. Set up the backend:

   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure environment variables:

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Set up the frontend:

   ```bash
   cd frontend
   npm install
   ```

5. Start the development servers:

   ```bash
   # Terminal 1 - Backend
   cd backend
   uvicorn app.main:app --reload

   # Terminal 2 - Frontend
   cd frontend
   npm start
   ```

## Usage

1. Start a chat session by typing in the input box
2. Use natural language to interact with the assistant
3. Send emails using commands like:
   ```
   send email to example@email.com "Subject" "Message"
   ```

## Development Roadmap

### Phase 1: Core LLM Integration ✅

- [x] Local LLaMA 2 setup
- [x] Basic chat interface
- [x] Natural language processing

### Phase 2: Gmail Integration ✅

- [x] MCP server implementation
- [x] Email command processing
- [x] OAuth2 authentication
- [x] Email status feedback

### Phase 3: Google Drive Integration (In Progress)

- [ ] File access implementation
- [ ] Document search functionality
- [ ] File sharing capabilities
- [ ] Folder management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- LLaMA 2 team for the open-source model
- FastAPI for the backend framework
- React team for the frontend framework
