## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+ and npm

### 1. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or .\\venv\\Scripts\\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run electron-dev
```

### 3. Usage

- Start both the backend and frontend as above.
- The Electron app will open as a desktop window.
- Type your message in the chat box and interact with the local AI model.

## Roadmap

- [x] Local LLM chat with FastAPI and Electron
- [ ] Add support for multiple MCP servers
- [ ] Voice input/output
- [ ] Plugin system for custom skills
- [ ] Settings and personalization

## Contributing

Pull requests and suggestions are welcome! Please open an issue to discuss your ideas.

## License

[MIT](LICENSE)

---

**Note:** All AI processing is done locally. No data is sent to external servers unless you configure additional MCP servers in the future.
