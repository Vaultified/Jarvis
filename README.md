# Jarvis - AI Desktop Assistant

A powerful, privacy-focused AI desktop assistant that runs entirely on your local machine. Built with FastAPI, Electron, and local LLMs, Jarvis provides a seamless voice and text interface for your daily tasks.

## 🌟 Features

- **Voice Interface**

  - Wake word detection ("Hey Jarvis")
  - Natural voice input/output
  - British English female voice (Karen)
  - Passive listening mode
  - 5-second quick recording mode

- **Local AI Processing**

  - Runs entirely on your machine
  - No data sent to external servers
  - Powered by Mistral-7B model
  - Fast response times
  - Privacy-focused design

- **Modern UI**
  - Clean, responsive interface
  - Real-time chat display
  - Voice activity indicators
  - Dark/light mode support
  - Cross-platform compatibility

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+ and npm
- macOS (for voice features)
- 8GB+ RAM recommended

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/jarvis.git
cd jarvis
```

2. **Backend Setup**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or .\\venv\\Scripts\\activate on Windows
pip install -r requirements.txt
```

3. **Frontend Setup**

```bash
cd frontend
npm install
```

4. **Environment Setup**
   Create a `.env` file in the backend directory:

```env
MODEL_PATH=llama.cpp/models/mistral-7b-v0.1.Q4_0.gguf
PORCUPINE_ACCESS_KEY=your_porcupine_key
```

### Running the Application

1. **Start the Backend**

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

2. **Start the Frontend**

```bash
cd frontend
npm run electron-dev
```

## 🔮 Roadmap

### Phase 1: Core Features (Current)

- [x] Local LLM chat integration
- [x] Voice input/output
- [x] Wake word detection
- [x] Basic UI/UX

### Phase 2: MCP Server Integration (Next)

- [ ] Multiple MCP server support
- [ ] Server health monitoring
- [ ] Load balancing
- [ ] Failover handling
- [ ] Server configuration UI

### Phase 3: Enhanced Features

- [ ] Plugin system for custom skills
- [ ] Custom wake word training
- [ ] Voice customization
- [ ] Advanced conversation memory
- [ ] Task scheduling and reminders

### Phase 4: Enterprise Features

- [ ] Multi-user support
- [ ] Role-based access control
- [ ] Audit logging
- [ ] API documentation
- [ ] Deployment guides

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**

```bash
git checkout -b feature/amazing-feature
```

3. **Commit your changes**

```bash
git commit -m 'Add amazing feature'
```

4. **Push to the branch**

```bash
git push origin feature/amazing-feature
```

5. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript for frontend code
- Write tests for new features
- Update documentation
- Keep commits atomic and well-described

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Mistral AI](https://mistral.ai/) for the LLM
- [Picovoice](https://picovoice.ai/) for wake word detection
- [Whisper](https://github.com/openai/whisper) for speech recognition
- [FastAPI](https://fastapi.tiangolo.com/) for the backend
- [Electron](https://www.electronjs.org/) for the desktop app

## 📞 Support

- Open an issue for bugs
- Start a discussion for feature requests
- Join our Discord community (coming soon)

---

**Note:** All AI processing is done locally. No data is sent to external servers unless you configure additional MCP servers.
