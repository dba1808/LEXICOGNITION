# AI Viva Voce Examiner

🎓 A RAG-powered AI examination system for academic viva voce evaluation.

## Features

- **PDF Processing**: Upload research papers and extract content using pdfplumber
- **RAG-based Questions**: Generate conceptual viva-style questions from documents
- **Hybrid Evaluation**: Combines semantic similarity + keyword matching for fair scoring
- **Voice Mode**: Speech-to-Text (Whisper) and Text-to-Speech (gTTS) support
- **Real-time Feedback**: Instant scoring with detailed academic feedback

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and add your API keys:

```bash
copy .env.example .env
```

Edit `.env` and add your API key:
- For Google Gemini: `GOOGLE_API_KEY=your_key_here`
- For OpenAI: `OPENAI_API_KEY=your_key_here`

### 3. Start the Backend Server

```bash
python -m backend.main
```

The API server will start at `http://localhost:8000`

### 4. Start the Frontend

In a new terminal:

```bash
streamlit run frontend/app.py
```

The UI will open at `http://localhost:8501`

## 📁 Project Structure

```
LEXICOGNITION/
├── backend/
│   ├── __init__.py
│   ├── config.py           # Configuration settings
│   ├── main.py            # FastAPI endpoints
│   ├── pdf_processor.py   # PDF extraction & chunking
│   ├── embeddings.py      # Sentence Transformers embeddings
│   ├── vector_store.py    # FAISS vector database
│   ├── llm_engine.py      # OpenAI/Gemini integration
│   ├── prompts.py         # System prompts
│   ├── question_generator.py  # RAG question generation
│   ├── evaluation_engine.py   # Hybrid answer evaluation
│   ├── voice_engine.py    # STT/TTS processing
│   └── session_manager.py # Session handling
├── frontend/
│   └── app.py             # Streamlit UI
├── requirements.txt
├── .env.example
└── README.md
```

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/session/create` | POST | Create new examination session |
| `/upload_pdf` | POST | Upload PDF for processing |
| `/generate_questions` | POST | Generate viva questions |
| `/ask_question/{session_id}` | GET | Get next question |
| `/submit_answer` | POST | Submit answer for evaluation |
| `/submit_voice_answer` | POST | Submit voice recording |
| `/get_report/{session_id}` | GET | Get final report |

## 📊 Evaluation System

The system uses a **hybrid scoring approach**:

```
Final Score = 0.6 × Semantic Similarity + 0.4 × Keyword Coverage
```

- **Semantic Similarity**: Uses sentence embeddings to measure conceptual understanding
- **Keyword Coverage**: Checks for important technical terms from the paper
- **LLM Evaluation**: Additional detailed feedback from the language model

### Scoring Criteria

| Score | Description |
|-------|-------------|
| 1-3 | Incorrect or irrelevant |
| 4-6 | Partially correct, missing core concepts |
| 7-8 | Correct with minor gaps |
| 9-10 | Fully correct with clear reasoning |

## 🎙️ Voice Mode

When enabled, the system can:
- Speak questions aloud using Google TTS
- Accept voice answers via Whisper transcription
- Provide audio feedback on scores

## 🛠️ Technology Stack

- **Backend**: FastAPI, Python 3.10+
- **RAG**: LangChain, FAISS, Sentence Transformers
- **LLM**: OpenAI GPT-4 or Google Gemini
- **PDF**: pdfplumber
- **Voice**: Whisper (STT), gTTS (TTS)
- **Frontend**: Streamlit

## 📝 License

MIT License
