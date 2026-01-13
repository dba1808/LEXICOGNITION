"""
FastAPI Backend - REST API for AI Viva Voce Examiner
"""
import shutil
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

from backend.config import settings
from backend.pdf_processor import get_pdf_processor
from backend.vector_store import get_vector_store
from backend.question_generator import get_question_generator
from backend.evaluation_engine import get_evaluation_engine
from backend.voice_engine import get_voice_engine
from backend.session_manager import (
    SessionManager, 
    create_session, 
    get_session
)


# ========== FastAPI App ==========

app = FastAPI(
    title="AI Viva Voce Examiner",
    description="RAG-based academic examination system with voice support",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== Request/Response Models ==========

class SessionCreateRequest(BaseModel):
    voice_enabled: bool = False


class SessionResponse(BaseModel):
    session_id: str
    status: str
    message: str


class SubmitAnswerRequest(BaseModel):
    session_id: str
    answer: str
    question_number: Optional[int] = None


class EvaluationResponse(BaseModel):
    question: str
    student_answer: str
    semantic_score: float
    keyword_score: float
    final_score: int
    evaluation: str
    missing_concepts: List[str]
    feedback: str


class QuestionResponse(BaseModel):
    question_number: int
    question_text: str
    difficulty: str
    total_questions: int


# ========== Endpoints ==========

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "AI Viva Voce Examiner",
        "version": "1.0.0"
    }


@app.post("/session/create")
async def create_new_session(request: SessionCreateRequest):
    """
    Create a new examination session
    """
    session = create_session(voice_enabled=request.voice_enabled)
    
    return SessionResponse(
        session_id=session.session_id,
        status="created",
        message="Session created successfully. Upload a PDF to continue."
    )


@app.get("/session/{session_id}")
async def get_session_status(session_id: str):
    """
    Get session status and details
    """
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session.to_dict()


@app.post("/upload_pdf")
async def upload_pdf(
    session_id: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Upload a PDF research paper for examination
    """
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Validate file
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Save uploaded file
    upload_path = settings.upload_dir / session_id
    upload_path.mkdir(parents=True, exist_ok=True)
    
    pdf_path = upload_path / file.filename
    
    try:
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
    
    # Process PDF
    try:
        processor = get_pdf_processor()
        chunks = processor.process_pdf(pdf_path)
        
        # Create vector index
        vector_store = get_vector_store(session_id)
        vector_store.create_index(chunks)
        
        # Update session
        session.pdf_filename = file.filename
        session.pdf_path = pdf_path
        session.status = "pdf_uploaded"
        
        return {
            "status": "success",
            "message": f"PDF '{file.filename}' processed successfully",
            "chunks_created": len(chunks),
            "session_id": session_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF processing failed: {e}")


@app.post("/generate_questions")
async def generate_questions(
    session_id: str = Form(...),
    num_questions: int = Form(5)
):
    """
    Generate viva-style questions from the uploaded PDF
    """
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.status not in ["pdf_uploaded", "in_progress"]:
        raise HTTPException(
            status_code=400, 
            detail="Upload a PDF first"
        )
    
    try:
        generator = get_question_generator(session_id)
        questions = generator.generate_questions(num_questions)
        
        session.total_questions = len(questions)
        session.current_question = 0
        session.status = "in_progress"
        
        return {
            "status": "success",
            "questions_generated": len(questions),
            "questions": [
                {
                    "number": q.question_number,
                    "question": q.question_text,
                    "difficulty": q.difficulty
                }
                for q in questions
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Question generation failed: {e}")


@app.get("/ask_question/{session_id}")
async def ask_question(session_id: str):
    """
    Get the next question for the viva
    """
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        generator = get_question_generator(session_id)
        question = generator.get_next_question()
        
        response = QuestionResponse(
            question_number=question.question_number,
            question_text=question.question_text,
            difficulty=question.difficulty,
            total_questions=session.total_questions
        )
        
        # Add voice if enabled
        if session.voice_enabled:
            voice_engine = get_voice_engine()
            audio_path, audio_bytes = voice_engine.speak_question(
                question.question_text
            )
            response_dict = response.dict()
            response_dict["audio_base64"] = voice_engine.audio_to_base64(audio_bytes)
            return response_dict
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/submit_answer")
async def submit_answer(request: SubmitAnswerRequest):
    """
    Submit an answer for evaluation
    """
    session = get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        # Get current question
        generator = get_question_generator(request.session_id)
        question = generator.get_current_question()
        
        # Evaluate answer
        evaluator = get_evaluation_engine(request.session_id)
        result = evaluator.evaluate_answer(
            question=question.question_text,
            student_answer=request.answer
        )
        
        # Record in session
        session.add_answer(
            question=question.question_text,
            answer=request.answer,
            score=result.final_score,
            feedback=result.feedback
        )
        
        response = EvaluationResponse(
            question=result.question,
            student_answer=result.student_answer,
            semantic_score=result.semantic_score,
            keyword_score=result.keyword_score,
            final_score=result.final_score,
            evaluation=result.llm_evaluation,
            missing_concepts=result.missing_concepts,
            feedback=result.feedback
        )
        
        # Add voice feedback if enabled
        if session.voice_enabled:
            voice_engine = get_voice_engine()
            _, audio_bytes = voice_engine.speak_feedback(
                result.final_score, 
                result.feedback
            )
            response_dict = response.dict()
            response_dict["audio_base64"] = voice_engine.audio_to_base64(audio_bytes)
            return response_dict
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {e}")


@app.post("/submit_voice_answer")
async def submit_voice_answer(
    session_id: str = Form(...),
    audio: UploadFile = File(...)
):
    """
    Submit a voice recording as answer
    """
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not session.voice_enabled:
        raise HTTPException(status_code=400, detail="Voice mode not enabled")
    
    try:
        # Save audio file
        audio_path = settings.audio_dir / f"{session_id}_answer.wav"
        with open(audio_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
        
        # Transcribe
        voice_engine = get_voice_engine()
        transcribed_text = voice_engine.transcribe_audio(audio_path)
        
        # Submit for evaluation
        return await submit_answer(SubmitAnswerRequest(
            session_id=session_id,
            answer=transcribed_text
        ))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice processing failed: {e}")


@app.get("/get_report/{session_id}")
async def get_report(session_id: str):
    """
    Get final examination report
    """
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session.get_final_report()


@app.post("/save_report/{session_id}")
async def save_report(session_id: str):
    """
    Save examination report to file
    """
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    report_path = SessionManager.save_session_report(session_id)
    
    if report_path:
        return {
            "status": "success",
            "report_path": str(report_path)
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to save report")


@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a session and its data
    """
    from backend.vector_store import VectorStoreManager
    
    success = SessionManager.delete_session(session_id)
    VectorStoreManager.delete_store(session_id)
    
    # Clean up files
    upload_dir = settings.upload_dir / session_id
    if upload_dir.exists():
        shutil.rmtree(upload_dir)
    
    if success:
        return {"status": "deleted", "session_id": session_id}
    else:
        raise HTTPException(status_code=404, detail="Session not found")


@app.get("/context_search/{session_id}")
async def search_context(session_id: str, query: str):
    """
    Search the document context (for debugging/exploration)
    """
    vector_store = get_vector_store(session_id)
    results = vector_store.search(query, top_k=5)
    
    return {
        "query": query,
        "results": [
            {
                "content": chunk.content,
                "page": chunk.page_number,
                "score": score
            }
            for chunk, score in results
        ]
    }


# ========== Server Entry Point ==========

if __name__ == "__main__":
    import uvicorn
    
    print("🎓 Starting AI Viva Voce Examiner Server...")
    
    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
