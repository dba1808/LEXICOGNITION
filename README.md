# 🎓 ORION - AI Viva Voce System

An intelligent AI-powered viva examination system with real-time voice interaction, camera proctoring, and PDF-based question generation.

## ✨ Features

- **AI Examiner** - Powered by Gemini 3 Flash Preview
- **Voice Interaction** - Real-time speech-to-text and text-to-speech
- **PDF Analysis** - RAG-based question generation from study materials
- **Camera Proctoring** - Webcam monitoring during exams
- **Smart Evaluation** - Hybrid semantic + keyword scoring
- **Beautiful UI** - Retro dark theme with golden accents

## 🚀 Quick Start

### Prerequisites

- Python 3.9+ (Python 3.10+ recommended)
- A Google Gemini API Key ([Get one here](https://aistudio.google.com/apikey))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/ORION.git
   cd ORION
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your API key
   # GOOGLE_API_KEY=your_api_key_here
   ```

5. **Run the application**
   ```bash
   # Simple single command (starts both backend and frontend)
   python run.py
   
   # OR run frontend only
   streamlit run frontend/app.py --server.port 8501
   ```

6. **Open in browser**
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000

## 📁 Project Structure

```
ORION/
├── frontend/
│   ├── app.py              # Main Streamlit application
│   └── live_conversation.py # Viva interface components
├── backend/
│   ├── main.py             # FastAPI backend
│   ├── llm_engine.py       # Gemini AI integration
│   ├── question_generator.py # RAG-based question generation
│   ├── evaluation_engine.py  # Answer evaluation
│   ├── voice_engine.py     # TTS/STT functionality
│   └── database.py         # SQLite database
├── assets/
│   ├── orion_logo.png      # ORION logo
│   └── ai_examiner.png     # AI avatar
├── data/                   # Database and uploads
├── .env.example            # Environment template
├── requirements.txt        # Python dependencies
└── run.py                  # Simple startup script
```

## 🔧 Troubleshooting

### "Streamlit not connected" Error

1. Make sure you have installed all dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Verify the `.env` file exists with your API key:
   ```bash
   # Check if .env exists
   ls .env
   
   # If not, copy from example
   cp .env.example .env
   ```

3. Try running with a different port:
   ```bash
   streamlit run frontend/app.py --server.port 8505
   ```

### Dependencies Issues

If you encounter dependency conflicts:
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### PyAudio Installation (for voice features)

**Windows:**
```bash
pip install pipwin
pipwin install pyaudio
```

**Linux:**
```bash
sudo apt-get install portaudio19-dev
pip install pyaudio
```

**Mac:**
```bash
brew install portaudio
pip install pyaudio
```

## 🔐 User Roles

- **Teacher**: Create exams, upload PDFs, assign to students, view results
- **Student**: Take assigned exams, voice-based viva interaction

## 📝 License

MIT License

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.
