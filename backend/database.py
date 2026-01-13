"""
LexiCognition Database Models
SQLite database for users, exams, and results
"""
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import hashlib
import uuid
import json

# Database path
DB_PATH = Path(__file__).parent.parent / "data" / "lexicognition.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize database with all tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Users table (teachers and students)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('teacher', 'student')),
        class_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active INTEGER DEFAULT 1
    )
    """)
    
    # Subjects table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        code TEXT UNIQUE NOT NULL,
        description TEXT
    )
    """)
    
    # Classes table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS classes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT
    )
    """)
    
    # Exams table (created by teachers)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_id TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        teacher_id TEXT NOT NULL,
        subject_id INTEGER NOT NULL,
        class_id INTEGER,
        join_code TEXT UNIQUE NOT NULL,
        pdf_filename TEXT,
        questions TEXT,
        num_questions INTEGER DEFAULT 5,
        voice_only INTEGER DEFAULT 0,
        allow_paste INTEGER DEFAULT 0,
        status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'active', 'closed')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (teacher_id) REFERENCES users(user_id),
        FOREIGN KEY (subject_id) REFERENCES subjects(id),
        FOREIGN KEY (class_id) REFERENCES classes(id)
    )
    """)
    
    # Exam Access table (which students can access which exams)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exam_access (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_id TEXT NOT NULL,
        student_id TEXT NOT NULL,
        granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'started', 'completed')),
        FOREIGN KEY (exam_id) REFERENCES exams(exam_id),
        FOREIGN KEY (student_id) REFERENCES users(user_id),
        UNIQUE(exam_id, student_id)
    )
    """)
    
    # Exam Results table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exam_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        result_id TEXT UNIQUE NOT NULL,
        exam_id TEXT NOT NULL,
        student_id TEXT NOT NULL,
        answers TEXT,
        scores TEXT,
        total_score REAL,
        feedback TEXT,
        started_at TIMESTAMP,
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (exam_id) REFERENCES exams(exam_id),
        FOREIGN KEY (student_id) REFERENCES users(user_id)
    )
    """)
    
    # Notifications table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        notification_id TEXT UNIQUE NOT NULL,
        user_id TEXT NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        exam_id TEXT,
        is_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (exam_id) REFERENCES exams(exam_id)
    )
    """)
    
    conn.commit()
    
    # Insert default subjects
    default_subjects = [
        ("Machine Learning", "ML101", "Introduction to Machine Learning"),
        ("Deep Learning", "DL101", "Neural Networks and Deep Learning"),
        ("Natural Language Processing", "NLP101", "Text and Language Processing"),
        ("Computer Vision", "CV101", "Image and Video Analysis"),
        ("Data Science", "DS101", "Data Analysis and Statistics"),
        ("Artificial Intelligence", "AI101", "AI Fundamentals"),
        ("Python Programming", "PY101", "Python Basics and Advanced"),
        ("Database Systems", "DB101", "SQL and NoSQL Databases"),
        ("Web Development", "WEB101", "Frontend and Backend Development"),
        ("Cloud Computing", "CC101", "AWS, Azure, GCP"),
    ]
    
    for name, code, desc in default_subjects:
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO subjects (name, code, description) VALUES (?, ?, ?)",
                (name, code, desc)
            )
        except:
            pass
    
    # Insert default classes
    default_classes = [
        ("Class 10", "10th Grade"),
        ("Class 11", "11th Grade"),
        ("Class 12", "12th Grade"),
        ("BTech Year 1", "First Year Engineering"),
        ("BTech Year 2", "Second Year Engineering"),
        ("BTech Year 3", "Third Year Engineering"),
        ("BTech Year 4", "Final Year Engineering"),
        ("MTech Year 1", "First Year Masters"),
        ("MTech Year 2", "Second Year Masters"),
        ("PhD", "Doctoral Program"),
    ]
    
    for name, desc in default_classes:
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO classes (name, description) VALUES (?, ?)",
                (name, desc)
            )
        except:
            pass
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")


def hash_password(password: str) -> str:
    """Hash password with SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_id() -> str:
    """Generate unique ID"""
    return str(uuid.uuid4())[:8].upper()


# ============ USER FUNCTIONS ============

def create_user(name: str, email: str, password: str, role: str, class_name: str = None) -> Optional[Dict]:
    """Create a new user (teacher or student)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    user_id = generate_id()
    password_hash = hash_password(password)
    
    try:
        cursor.execute("""
            INSERT INTO users (user_id, name, email, password_hash, role, class_name)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, name, email, password_hash, role, class_name))
        conn.commit()
        
        return {
            "user_id": user_id,
            "name": name,
            "email": email,
            "role": role,
            "class_name": class_name
        }
    except sqlite3.IntegrityError as e:
        if "email" in str(e):
            return {"error": "Email already exists"}
        return {"error": str(e)}
    finally:
        conn.close()


def authenticate_user(email: str, password: str) -> Optional[Dict]:
    """Authenticate user by email and password"""
    conn = get_connection()
    cursor = conn.cursor()
    
    password_hash = hash_password(password)
    
    cursor.execute("""
        SELECT user_id, name, email, role, class_name
        FROM users
        WHERE email = ? AND password_hash = ? AND is_active = 1
    """, (email, password_hash))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def get_user(user_id: str) -> Optional[Dict]:
    """Get user by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT user_id, name, email, role, class_name, created_at
        FROM users WHERE user_id = ?
    """, (user_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None


def get_all_students() -> List[Dict]:
    """Get all students"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT user_id, name, email, class_name
        FROM users WHERE role = 'student' AND is_active = 1
        ORDER BY name
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_students_by_class(class_name: str) -> List[Dict]:
    """Get students by class"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT user_id, name, email, class_name
        FROM users WHERE role = 'student' AND class_name = ? AND is_active = 1
        ORDER BY name
    """, (class_name,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


# ============ SUBJECT & CLASS FUNCTIONS ============

def get_all_subjects() -> List[Dict]:
    """Get all subjects"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, code, description FROM subjects ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_all_classes() -> List[Dict]:
    """Get all classes"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, description FROM classes ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


# ============ EXAM FUNCTIONS ============

def create_exam(teacher_id: str, title: str, subject_id: int, class_id: int = None,
                num_questions: int = 5, voice_only: bool = False, allow_paste: bool = False) -> Dict:
    """Create a new exam"""
    conn = get_connection()
    cursor = conn.cursor()
    
    exam_id = generate_id()
    join_code = ''.join([chr(ord('A') + (hash(exam_id + str(i)) % 26)) for i in range(6)])
    
    cursor.execute("""
        INSERT INTO exams (exam_id, title, teacher_id, subject_id, class_id, num_questions, join_code, voice_only, allow_paste)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (exam_id, title, teacher_id, subject_id, class_id, num_questions, join_code, voice_only, allow_paste))
    
    conn.commit()
    conn.close()
    
    return {
        "exam_id": exam_id,
        "title": title,
        "join_code": join_code,
        "status": "draft"
    }


def update_exam_pdf(exam_id: str, pdf_filename: str):
    """Update exam with PDF filename"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE exams SET pdf_filename = ? WHERE exam_id = ?", (pdf_filename, exam_id))
    conn.commit()
    conn.close()


def update_exam_questions(exam_id: str, questions: List[Dict]):
    """Update exam with generated questions"""
    conn = get_connection()
    cursor = conn.cursor()
    
    questions_json = json.dumps(questions)
    cursor.execute("""
        UPDATE exams SET questions = ?, num_questions = ?, status = 'active'
        WHERE exam_id = ?
    """, (questions_json, len(questions), exam_id))
    
    conn.commit()
    conn.close()


def get_exam(exam_id: str) -> Optional[Dict]:
    """Get exam by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT e.*, s.name as subject_name, c.name as class_name, u.name as teacher_name
        FROM exams e
        LEFT JOIN subjects s ON e.subject_id = s.id
        LEFT JOIN classes c ON e.class_id = c.id
        LEFT JOIN users u ON e.teacher_id = u.user_id
        WHERE e.exam_id = ?
    """, (exam_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        exam = dict(row)
        if exam.get('questions'):
            exam['questions'] = json.loads(exam['questions'])
        return exam
    return None


def get_teacher_exams(teacher_id: str) -> List[Dict]:
    """Get all exams by a teacher"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT e.*, s.name as subject_name,
               (SELECT COUNT(*) FROM exam_access WHERE exam_id = e.exam_id) as student_count
        FROM exams e
        LEFT JOIN subjects s ON e.subject_id = s.id
        WHERE e.teacher_id = ?
        ORDER BY e.created_at DESC
    """, (teacher_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def activate_exam(exam_id: str):
    """Activate exam for students"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE exams SET status = 'active' WHERE exam_id = ?", (exam_id,))
    conn.commit()
    conn.close()


def close_exam(exam_id: str):
    """Close exam"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE exams SET status = 'closed' WHERE exam_id = ?", (exam_id,))
    conn.commit()
    conn.close()


# ============ EXAM ACCESS FUNCTIONS ============

def grant_exam_access(exam_id: str, student_ids: List[str]):
    """Grant multiple students access to an exam"""
    conn = get_connection()
    cursor = conn.cursor()
    
    exam = get_exam(exam_id)
    
    for student_id in student_ids:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO exam_access (exam_id, student_id)
                VALUES (?, ?)
            """, (exam_id, student_id))
            
            # Create notification for student
            notification_id = generate_id()
            cursor.execute("""
                INSERT INTO notifications (notification_id, user_id, title, message, exam_id)
                VALUES (?, ?, ?, ?, ?)
            """, (
                notification_id,
                student_id,
                f"New Exam Available: {exam.get('title', 'Untitled')}",
                f"You have been granted access to take the exam. Join Code: {exam.get('join_code', 'N/A')}",
                exam_id
            ))
        except:
            pass
    
    conn.commit()
    conn.close()


def revoke_exam_access(exam_id: str, student_id: str):
    """Revoke student access to an exam"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM exam_access WHERE exam_id = ? AND student_id = ?", (exam_id, student_id))
    conn.commit()
    conn.close()


def get_exam_students(exam_id: str) -> List[Dict]:
    """Get all students with access to an exam"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT u.user_id, u.name, u.email, u.class_name, ea.status, ea.granted_at
        FROM exam_access ea
        JOIN users u ON ea.student_id = u.user_id
        WHERE ea.exam_id = ?
        ORDER BY u.name
    """, (exam_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_student_exams(student_id: str) -> List[Dict]:
    """Get all exams a student has access to"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT e.exam_id, e.title, e.join_code, e.status as exam_status, e.voice_only, e.num_questions,
               s.name as subject_name, u.name as teacher_name, ea.status as access_status
        FROM exam_access ea
        JOIN exams e ON ea.exam_id = e.exam_id
        LEFT JOIN subjects s ON e.subject_id = s.id
        LEFT JOIN users u ON e.teacher_id = u.user_id
        WHERE ea.student_id = ? AND e.status = 'active'
        ORDER BY ea.granted_at DESC
    """, (student_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def update_access_status(exam_id: str, student_id: str, status: str):
    """Update student's exam access status"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE exam_access SET status = ? WHERE exam_id = ? AND student_id = ?
    """, (status, exam_id, student_id))
    
    conn.commit()
    conn.close()


# ============ NOTIFICATION FUNCTIONS ============

def get_user_notifications(user_id: str, unread_only: bool = False) -> List[Dict]:
    """Get notifications for a user"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT notification_id, title, message, exam_id, is_read, created_at
        FROM notifications
        WHERE user_id = ?
    """
    if unread_only:
        query += " AND is_read = 0"
    query += " ORDER BY created_at DESC"
    
    cursor.execute(query, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def mark_notification_read(notification_id: str):
    """Mark notification as read"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE notifications SET is_read = 1 WHERE notification_id = ?", (notification_id,))
    conn.commit()
    conn.close()


def get_unread_count(user_id: str) -> int:
    """Get unread notification count"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM notifications WHERE user_id = ? AND is_read = 0", (user_id,))
    count = cursor.fetchone()[0]
    conn.close()
    
    return count


# ============ RESULT FUNCTIONS ============

def save_exam_result(exam_id: str, student_id: str, answers: List[Dict], 
                     scores: List[float], total_score: float, feedback: str = ""):
    """Save exam result"""
    conn = get_connection()
    cursor = conn.cursor()
    
    result_id = generate_id()
    
    cursor.execute("""
        INSERT INTO exam_results (result_id, exam_id, student_id, answers, scores, total_score, feedback)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (result_id, exam_id, student_id, json.dumps(answers), json.dumps(scores), total_score, feedback))
    
    # Update access status
    cursor.execute("""
        UPDATE exam_access SET status = 'completed' WHERE exam_id = ? AND student_id = ?
    """, (exam_id, student_id))
    
    conn.commit()
    conn.close()
    
    return result_id


def get_student_result(exam_id: str, student_id: str) -> Optional[Dict]:
    """Get student's result for an exam"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM exam_results WHERE exam_id = ? AND student_id = ?
    """, (exam_id, student_id))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        result = dict(row)
        result['answers'] = json.loads(result['answers']) if result['answers'] else []
        result['scores'] = json.loads(result['scores']) if result['scores'] else []
        return result
    return None


def get_exam_results(exam_id: str) -> List[Dict]:
    """Get all results for an exam"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT er.*, u.name as student_name, u.email as student_email
        FROM exam_results er
        JOIN users u ON er.student_id = u.user_id
        WHERE er.exam_id = ?
        ORDER BY er.total_score DESC
    """, (exam_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        r = dict(row)
        r['answers'] = json.loads(r['answers']) if r['answers'] else []
        r['scores'] = json.loads(r['scores']) if r['scores'] else []
        results.append(r)
    
    return results


# Initialize database on import
init_database()
