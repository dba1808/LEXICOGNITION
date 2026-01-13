"""
Session Manager - Manages viva examination sessions
"""
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from pathlib import Path
import json

from backend.config import settings


@dataclass
class ExaminationSession:
    """Represents a viva examination session"""
    session_id: str
    created_at: datetime
    pdf_filename: Optional[str] = None
    pdf_path: Optional[Path] = None
    total_questions: int = 0
    current_question: int = 0
    scores: List[int] = field(default_factory=list)
    answers: List[Dict[str, Any]] = field(default_factory=list)
    voice_enabled: bool = False
    status: str = "initialized"  # initialized, pdf_uploaded, in_progress, completed
    
    @property
    def average_score(self) -> float:
        """Calculate average score"""
        if not self.scores:
            return 0.0
        return sum(self.scores) / len(self.scores)
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage"""
        if self.total_questions == 0:
            return 0.0
        return (self.current_question / self.total_questions) * 100
    
    def add_answer(
        self, 
        question: str, 
        answer: str, 
        score: int, 
        feedback: str
    ):
        """Record an answer"""
        self.answers.append({
            "question_number": self.current_question,
            "question": question,
            "answer": answer,
            "score": score,
            "feedback": feedback,
            "timestamp": datetime.now().isoformat()
        })
        self.scores.append(score)
        self.current_question += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "pdf_filename": self.pdf_filename,
            "total_questions": self.total_questions,
            "current_question": self.current_question,
            "scores": self.scores,
            "answers": self.answers,
            "voice_enabled": self.voice_enabled,
            "status": self.status,
            "average_score": self.average_score,
            "progress_percentage": self.progress_percentage
        }
    
    def get_final_report(self) -> Dict[str, Any]:
        """Generate final examination report"""
        return {
            "session_id": self.session_id,
            "pdf_filename": self.pdf_filename,
            "examination_date": self.created_at.isoformat(),
            "total_questions": self.total_questions,
            "questions_answered": len(self.answers),
            "individual_scores": self.scores,
            "average_score": round(self.average_score, 2),
            "performance_grade": self._calculate_grade(),
            "detailed_answers": self.answers,
            "recommendations": self._generate_recommendations()
        }
    
    def _calculate_grade(self) -> str:
        """Calculate letter grade based on average score"""
        avg = self.average_score
        if avg >= 9:
            return "A+ (Excellent)"
        elif avg >= 8:
            return "A (Very Good)"
        elif avg >= 7:
            return "B (Good)"
        elif avg >= 6:
            return "C (Satisfactory)"
        elif avg >= 5:
            return "D (Needs Improvement)"
        else:
            return "F (Fail)"
    
    def _generate_recommendations(self) -> List[str]:
        """Generate study recommendations based on performance"""
        recommendations = []
        avg = self.average_score
        
        if avg < 5:
            recommendations.append("Focus on understanding core concepts from the paper")
            recommendations.append("Re-read the methodology and findings sections")
        elif avg < 7:
            recommendations.append("Review sections where you scored the lowest")
            recommendations.append("Practice explaining concepts in your own words")
        else:
            recommendations.append("Good understanding demonstrated")
            recommendations.append("Continue exploring related research")
        
        # Find weak areas
        for answer in self.answers:
            if answer.get("score", 10) < 5:
                recommendations.append(
                    f"Review: {answer.get('question', 'N/A')[:50]}..."
                )
        
        return recommendations[:5]  # Limit recommendations


class SessionManager:
    """
    Manages examination sessions
    """
    
    _sessions: Dict[str, ExaminationSession] = {}
    
    @classmethod
    def create_session(cls, voice_enabled: bool = False) -> ExaminationSession:
        """Create a new examination session"""
        session_id = str(uuid.uuid4())[:8]
        
        session = ExaminationSession(
            session_id=session_id,
            created_at=datetime.now(),
            voice_enabled=voice_enabled
        )
        
        cls._sessions[session_id] = session
        print(f"✅ Created session: {session_id}")
        
        return session
    
    @classmethod
    def get_session(cls, session_id: str) -> Optional[ExaminationSession]:
        """Get a session by ID"""
        return cls._sessions.get(session_id)
    
    @classmethod
    def update_session(
        cls, 
        session_id: str, 
        **kwargs
    ) -> Optional[ExaminationSession]:
        """Update session attributes"""
        session = cls.get_session(session_id)
        if session:
            for key, value in kwargs.items():
                if hasattr(session, key):
                    setattr(session, key, value)
        return session
    
    @classmethod
    def delete_session(cls, session_id: str) -> bool:
        """Delete a session"""
        if session_id in cls._sessions:
            del cls._sessions[session_id]
            return True
        return False
    
    @classmethod
    def list_sessions(cls) -> List[Dict[str, Any]]:
        """List all active sessions"""
        return [
            session.to_dict() 
            for session in cls._sessions.values()
        ]
    
    @classmethod
    def save_session_report(
        cls, 
        session_id: str, 
        output_dir: Path = None
    ) -> Optional[Path]:
        """Save session report to file"""
        session = cls.get_session(session_id)
        if not session:
            return None
        
        output_dir = output_dir or settings.base_dir / "reports"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        report = session.get_final_report()
        output_path = output_dir / f"report_{session_id}.json"
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Saved report: {output_path}")
        return output_path


def create_session(voice_enabled: bool = False) -> ExaminationSession:
    """Create a new examination session"""
    return SessionManager.create_session(voice_enabled)


def get_session(session_id: str) -> Optional[ExaminationSession]:
    """Get a session by ID"""
    return SessionManager.get_session(session_id)
