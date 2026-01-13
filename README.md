# 🎓 ORION - AI Viva Voce System

An intelligent AI-powered viva examination system with real-time voice interaction, camera proctoring, and PDF-based question generation.

## ✨ Features

- **AI Examiner** - Powered by Google Gemini
- **Voice Interaction** - Real-time speech-to-text and text-to-speech
- **PDF Analysis** - RAG-based question generation from study materials
- **Camera Proctoring** - Webcam monitoring during exams
- **Smart Evaluation** - Hybrid semantic + keyword scoring
- **Beautiful UI** - Enterprise dark theme with KLAXON-style design

## 🚀 Quick Start (One Command!)

### Prerequisites
- Python 3.9+ (Python 3.10+ recommended)
- A Google Gemini API Key ([Get one free here](https://aistudio.google.com/apikey))

### Installation & Run

```bash
# 1. Clone the repository
git clone https://github.com/your-username/ORION.git
cd ORION

# 2. Run the application (automatically sets up everything!)
python run.py
```

**That's it!** The script will automatically:
- ✅ Create a virtual environment
- ✅ Install all dependencies
- ✅ Set up the database
- ✅ Create .env file (you just need to add your API key)
- ✅ Start the application

### Add Your API Key

After the first run, edit the `.env` file:
```
GOOGLE_API_KEY=your_actual_api_key_here
```

Then run again:
```bash
python run.py
```

### Access the Application
- **Frontend:** http://localhost:8501
- **Backend API:** http://localhost:8000

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
│   └── database.py         # SQLite database
├── assets/
│   ├── orion_logo.png      # ORION logo
│   └── ai_examiner.png     # AI avatar
├── data/                   # Database and uploads
├── .env.example            # Environment template
├── requirements.txt        # Python dependencies
└── run.py                  # ⭐ One-command setup & run script
```

## 🔧 Manual Setup (Alternative)

If you prefer manual setup:

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and edit .env
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Run
streamlit run frontend/app.py
```

## 🔧 Troubleshooting

### "Streamlit not connected" Error
1. Make sure Python 3.9+ is installed
2. Delete `.venv` folder and run `python run.py` again
3. Check if `.env` file has a valid API key

### PyAudio Issues (for voice features)

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
