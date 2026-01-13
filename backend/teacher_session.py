"""
Teacher & Student Session Management
Handles exam creation by teachers and student joining
"""
import uuid
import random
import string
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class ExamMode(Enum):
    """Exam input modes"""
    VOICE_ONLY = "voice_only"
    TEXT_ONLY = "text_only"
    BOTH = "both"


@dataclass
class ExamConfig:
    """Configuration for an exam session"""
    subject: str
    teacher_name: str
    num_questions: int = 5
    time_per_question: int = 120  # seconds
    mode: ExamMode = ExamMode.BOTH
    allow_paste: bool = False
    voice_enabled: bool = True
    auto_advance: bool = False
    show_feedback: bool = True
    

@dataclass
class TeacherSession:
    """A teacher-created exam session"""
    session_id: str
    join_code: str
    teacher_name: str
    subject: str
    pdf_filename: Optional[str] = None
    config: ExamConfig = None
    created_at: datetime = None
    status: str = "created"  # created, active, paused, completed
    questions: List[Dict[str, Any]] = field(default_factory=list)
    enrolled_students: List[str] = field(default_factory=list)
    active_students: Dict[str, 'StudentSession'] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.config is None:
            self.config = ExamConfig(
                subject=self.subject,
                teacher_name=self.teacher_name
            )
    
    def generate_join_code(self) -> str:
        """Generate a unique 6-character join code"""
        chars = string.ascii_uppercase + string.digits
        code = ''.join(random.choices(chars, k=6))
        return code
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "join_code": self.join_code,
            "teacher_name": self.teacher_name,
            "subject": self.subject,
            "pdf_filename": self.pdf_filename,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "num_questions": len(self.questions),
            "enrolled_students": len(self.enrolled_students),
            "active_students": len(self.active_students),
            "config": {
                "mode": self.config.mode.value,
                "allow_paste": self.config.allow_paste,
                "voice_enabled": self.config.voice_enabled,
                "time_per_question": self.config.time_per_question
            }
        }


@dataclass
class StudentSession:
    """A student's exam session"""
    student_id: str
    student_name: str
    teacher_session_id: str
    join_code: str
    joined_at: datetime = None
    status: str = "joined"  # joined, in_progress, completed
    current_question: int = 0
    answers: List[Dict[str, Any]] = field(default_factory=list)
    scores: List[int] = field(default_factory=list)
    total_score: float = 0.0
    
    def __post_init__(self):
        if self.joined_at is None:
            self.joined_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "student_id": self.student_id,
            "student_name": self.student_name,
            "teacher_session_id": self.teacher_session_id,
            "status": self.status,
            "current_question": self.current_question,
            "questions_answered": len(self.answers),
            "scores": self.scores,
            "total_score": self.total_score,
            "joined_at": self.joined_at.isoformat()
        }


class TeacherSessionManager:
    """Manages teacher exam sessions"""
    
    _sessions: Dict[str, TeacherSession] = {}
    _join_codes: Dict[str, str] = {}  # join_code -> session_id
    
    @classmethod
    def create_session(
        cls,
        teacher_name: str,
        subject: str,
        config: ExamConfig = None
    ) -> TeacherSession:
        """Create a new teacher session"""
        session_id = str(uuid.uuid4())[:8].upper()
        
        # Generate unique join code
        join_code = cls._generate_unique_code()
        
        session = TeacherSession(
            session_id=session_id,
            join_code=join_code,
            teacher_name=teacher_name,
            subject=subject,
            config=config or ExamConfig(subject=subject, teacher_name=teacher_name)
        )
        
        cls._sessions[session_id] = session
        cls._join_codes[join_code] = session_id
        
        print(f"✅ Created teacher session: {session_id} (Join Code: {join_code})")
        return session
    
    @classmethod
    def _generate_unique_code(cls) -> str:
        """Generate a unique 6-char code"""
        chars = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(random.choices(chars, k=6))
            if code not in cls._join_codes:
                return code
    
    @classmethod
    def get_session(cls, session_id: str) -> Optional[TeacherSession]:
        return cls._sessions.get(session_id)
    
    @classmethod
    def get_by_join_code(cls, join_code: str) -> Optional[TeacherSession]:
        session_id = cls._join_codes.get(join_code.upper())
        if session_id:
            return cls._sessions.get(session_id)
        return None
    
    @classmethod
    def update_session(cls, session_id: str, **kwargs) -> Optional[TeacherSession]:
        session = cls.get_session(session_id)
        if session:
            for key, value in kwargs.items():
                if hasattr(session, key):
                    setattr(session, key, value)
        return session
    
    @classmethod
    def list_sessions(cls) -> List[Dict[str, Any]]:
        return [s.to_dict() for s in cls._sessions.values()]


class StudentSessionManager:
    """Manages student exam sessions"""
    
    _students: Dict[str, StudentSession] = {}
    
    @classmethod
    def join_exam(
        cls,
        student_name: str,
        join_code: str
    ) -> Optional[StudentSession]:
        """Student joins an exam via join code"""
        teacher_session = TeacherSessionManager.get_by_join_code(join_code)
        
        if not teacher_session:
            return None
        
        if teacher_session.status not in ["created", "active"]:
            return None
        
        student_id = str(uuid.uuid4())[:8].upper()
        
        student = StudentSession(
            student_id=student_id,
            student_name=student_name,
            teacher_session_id=teacher_session.session_id,
            join_code=join_code.upper()
        )
        
        cls._students[student_id] = student
        teacher_session.active_students[student_id] = student
        teacher_session.enrolled_students.append(student_name)
        
        print(f"✅ Student '{student_name}' joined exam {teacher_session.session_id}")
        return student
    
    @classmethod
    def get_student(cls, student_id: str) -> Optional[StudentSession]:
        return cls._students.get(student_id)
    
    @classmethod
    def get_teacher_session_for_student(
        cls, 
        student_id: str
    ) -> Optional[TeacherSession]:
        student = cls.get_student(student_id)
        if student:
            return TeacherSessionManager.get_session(student.teacher_session_id)
        return None
    
    @classmethod
    def update_student(cls, student_id: str, **kwargs) -> Optional[StudentSession]:
        student = cls.get_student(student_id)
        if student:
            for key, value in kwargs.items():
                if hasattr(student, key):
                    setattr(student, key, value)
        return student


# Helper functions
def create_teacher_session(teacher_name: str, subject: str) -> TeacherSession:
    return TeacherSessionManager.create_session(teacher_name, subject)


def join_exam(student_name: str, join_code: str) -> Optional[StudentSession]:
    return StudentSessionManager.join_exam(student_name, join_code)


def get_exam_config(session_id: str) -> Optional[ExamConfig]:
    session = TeacherSessionManager.get_session(session_id)
    return session.config if session else None
