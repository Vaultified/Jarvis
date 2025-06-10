# Jarvis - Local LLM Assistant with MCP (Model Context Protocol) Integration

Jarvis is an AI assistant that runs locally using LLaMA 2, featuring seamless integration with Gmail, Google Drive, and real-time Weather through the MCP (Model Context Protocol) server architecture. The system allows natural language interaction for sending emails, managing files, and getting live weather updates. More personal productivity tools can be added as needed.

## Features

### Current Features

- **Local LLM Integration**
  - Runs LLaMA 2 model locally for privacy and offline use
  - Natural language processing for chat interactions
  - Customizable model parameters and response generation

- **Gmail Integration (via MCP)**
  - MCP (Model Context Protocol) server architecture for email operations
  - Natural language email commands
  - Secure OAuth2 authentication
  - Real-time email status feedback
  - Example commands:
    ```
    send an email to example@email.com about "Subject" saying "Message"
    ```

- **Google Drive Integration (via MCP)**
  - List folders and files in your Drive
  - Search for files and folders using natural language
  - Example commands:
    - `list all folders in my Drive`
    - `list files in my Drive in "FolderName"`
    - `search my Drive for "report"`

- **Weather Integration (via MCP)**
  - Real-time weather data using Open-Meteo API
  - Supports city names and coordinates
  - Example commands:
    - `what's the weather in London?`
    - `weather update for Paris`
    - `weather in 37.7749,-122.4194`

### Coming Soon

- **Calendar Integration (via MCP)**
  - Manage events and reminders using natural language
- **Other Personal MCP Servers**
  - Integrate additional services as needed for personal productivity

## Technical Architecture

### Frontend
- React-based chat interface
- Real-time message updates
- Visual feedback for email, Drive, and weather operations

### Backend
- FastAPI server
- LLaMA 2 model integration
- MCP (Model Context Protocol) servers for Gmail, Google Drive, and Weather
- OAuth2 authentication

### Components
1. **Chat System**
   - Natural language processing
   - Command recognition
   - Response generation
2. **Gmail Service (MCP)**
   - Email sending via MCP (Model Context Protocol) server
   - Status tracking and error handling
3. **Google Drive Service (MCP)**
   - File and folder management via MCP (Model Context Protocol) server
   - Search and retrieval
4. **Weather Service (MCP)**
   - Real-time weather data via MCP (Model Context Protocol) server
   - City name and coordinate support
5. **Authentication**
   - Google OAuth2 integration
   - Secure token management
   - Automatic token refresh
6. **Extensible MCP Integration**
   - Easily add new MCP (Model Context Protocol) servers for personal use (Calendar, etc.)

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
3. Send emails, manage Drive, and get weather using commands like:
   ```
   send an email to someone@email.com about "Subject" saying "Message"
   list all folders in my Drive
   search my Drive for "project"
   what's the weather in Kirklees?
   weather in 40.7128,-74.0060
   ```

## Development Roadmap
- [x] Local LLaMA 2 setup
- [x] Gmail MCP (Model Context Protocol) integration
- [x] Google Drive MCP (Model Context Protocol) integration
- [x] Weather MCP (Model Context Protocol) integration
- [ ] Calendar MCP (Model Context Protocol) integration
- [ ] Additional personal MCP (Model Context Protocol) servers as needed

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
- Google for Gmail and Drive APIs
- Open-Meteo for weather data
