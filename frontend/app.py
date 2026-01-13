"""
ORION - Professional AI Viva Voce System
Complete UI with all features
"""
import streamlit as st
import requests
import time
import sys
from pathlib import Path
import base64
from datetime import datetime, timedelta
import cv2
import numpy as np
import threading

# Try to import WebRTC components - they're optional for basic exam functionality
WEBRTC_AVAILABLE = False
try:
    import av
    from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, WebRtcMode
    WEBRTC_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ WebRTC not available: {e}. Video proctoring will be disabled.")
    # Create dummy classes for compatibility
    class VideoTransformerBase:
        pass
    WebRtcMode = None
    webrtc_streamer = None

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import (
    create_user, authenticate_user, get_user,
    get_all_subjects, get_all_classes, get_all_students, get_students_by_class,
    create_exam, update_exam_pdf, update_exam_questions, get_exam,
    get_teacher_exams, activate_exam, close_exam,
    grant_exam_access, get_exam_students, get_student_exams, update_access_status,
    get_user_notifications, mark_notification_read, get_unread_count,
    save_exam_result, get_exam_results, get_student_result
)

from backend.question_generator import get_question_generator
from backend.llm_engine import get_llm_engine
from backend.voice_engine import get_voice_engine
from backend.evaluation_engine import evaluate_answer as backend_evaluate
from backend.pdf_processor import get_pdf_processor
from backend.vector_store import get_vector_store
from backend.config import settings

# Page configuration
st.set_page_config(
    page_title="ORION - AI Viva Examiner",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)

API_BASE_URL = "http://localhost:8000"

# Convert image to base64 for embedding
def get_base64_image(path):
    try:
        with open(path, "rb") as image_file:
            image_data = image_file.read()
            return base64.b64encode(image_data).decode('utf-8')
    except Exception as e:
        print(f"⚠️ Error loading image {path}: {e}")
        return ""

# Use relative paths from project root for portability
PROJECT_ROOT = Path(__file__).parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
IMAGE_PATH = ASSETS_DIR / "ai_examiner.png"
ORION_LOGO_PATH = ASSETS_DIR / "orion_logo.png"
base64_img = get_base64_image(IMAGE_PATH)

# ========== RETRO PROFESSIONAL DARK UI ==========
st.markdown(f"""
<style>
    /* ===== IMPORTS ===== */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&family=JetBrains+Mono:wght@300;400;500;600;700&display=swap');
    
    /* ===== CSS VARIABLES ===== */
    :root {{
        --bg-primary: #0a0a12;
        --bg-secondary: #12121a;
        --bg-card: #16161f;
        --bg-hover: #1e1e28;
        --border-color: #2a2a3a;
        --border-hover: #3a3a4a;
        --text-primary: #f5f0dc;
        --text-secondary: #e8e3c8;
        --text-muted: #9a9585;
        --accent-gold: #d4a853;
        --accent-amber: #c9a227;
        --accent-cyan: #5ac8d8;
        --accent-green: #7dd87d;
        --accent-red: #e85d5d;
        --glow-gold: rgba(212, 168, 83, 0.15);
        --glow-cyan: rgba(90, 200, 216, 0.1);
        --font-mono: 'IBM Plex Mono', 'JetBrains Mono', 'Space Mono', monospace;
        --transition-smooth: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        --shadow-card: 0 4px 20px rgba(0, 0, 0, 0.4), 0 0 40px rgba(10, 10, 18, 0.6);
        --shadow-hover: 0 8px 30px rgba(0, 0, 0, 0.5), 0 0 50px rgba(212, 168, 83, 0.08);
    }}
    
    /* ===== FULL SCREEN DARK BACKGROUND WITH SUBTLE HUE ===== */
    .stApp {{
        background: linear-gradient(165deg, 
            var(--bg-primary) 0%, 
            #0d0d18 30%, 
            #0f0f1a 60%, 
            #101020 100%);
        min-height: 100vh;
    }}
    
    /* Subtle animated gradient overlay */
    .stApp::before {{
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(ellipse at 20% 20%, rgba(90, 200, 216, 0.03) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 80%, rgba(212, 168, 83, 0.03) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 50%, rgba(100, 80, 180, 0.02) 0%, transparent 60%);
        pointer-events: none;
        z-index: 0;
        animation: ambientGlow 20s ease-in-out infinite alternate;
    }}
    
    @keyframes ambientGlow {{
        0% {{ opacity: 0.6; }}
        100% {{ opacity: 1; }}
    }}
    
    /* ===== CUSTOM CURSOR ===== */
    /* Hide default cursor and use custom */
    *, *::before, *::after {{
        cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Ccircle cx='12' cy='12' r='4' fill='%23d4a853'/%3E%3Ccircle cx='12' cy='12' r='8' fill='none' stroke='%23d4a853' stroke-width='1' opacity='0.5'/%3E%3C/svg%3E") 12 12, auto !important;
    }}
    
    /* Pointer cursor for interactive elements */
    a, button, [role="button"], 
    .stButton > button,
    .stTabs [data-baseweb="tab"],
    input[type="submit"],
    input[type="button"],
    .stSelectbox > div,
    [data-testid="stSidebar"] *,
    .stRadio label,
    .stCheckbox label {{
        cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='28' height='28' viewBox='0 0 28 28'%3E%3Ccircle cx='14' cy='14' r='5' fill='%23f5d383'/%3E%3Ccircle cx='14' cy='14' r='10' fill='none' stroke='%23d4a853' stroke-width='2' opacity='0.7'/%3E%3Ccircle cx='14' cy='14' r='13' fill='none' stroke='%23d4a853' stroke-width='1' opacity='0.3'/%3E%3C/svg%3E") 14 14, pointer !important;
    }}
    
    /* Text cursor for inputs */
    input[type="text"], input[type="email"], input[type="password"], 
    input[type="number"], textarea {{
        cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Crect x='10' y='4' width='4' height='16' rx='2' fill='%23d4a853'/%3E%3C/svg%3E") 12 12, text !important;
    }}
    
    #MainMenu, footer, header {{ display: none !important; }}
    
    /* ===== TYPOGRAPHY - RETRO MONOSPACE ===== */
    * {{
        font-family: var(--font-mono) !important;
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em;
    }}
    
    p, span, div, label {{
        color: var(--text-secondary) !important;
    }}
    
    /* ===== ORION ENTERPRISE LOGO - KLAXON STYLE ===== */
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Oswald:wght@700&display=swap');
    
    .logo-container {{
        background: #000000 !important;
        padding: 60px 20px 40px 20px;
        margin: -20px -20px 30px -20px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }}
    
    .logo-container::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: 
            linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.02) 50%, transparent 100%);
        animation: scanLine 3s linear infinite;
    }}
    
    @keyframes scanLine {{
        0% {{ transform: translateX(-100%); }}
        100% {{ transform: translateX(100%); }}
    }}
    
    .logo-text {{
        font-family: 'Bebas Neue', 'Oswald', 'Impact', sans-serif !important;
        font-size: 5.5rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        text-align: center;
        margin: 0 !important;
        padding: 0 !important;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        line-height: 1;
        position: relative;
        display: inline-block;
        animation: morphGlow 4s ease-in-out infinite;
        text-shadow: none;
        background: none !important;
    }}
    
    /* Morph/Glitch effect */
    .logo-text::before {{
        content: 'ORION';
        position: absolute;
        top: 0;
        left: 2px;
        color: rgba(255, 100, 100, 0.8);
        -webkit-text-fill-color: rgba(255, 100, 100, 0.8);
        clip-path: inset(0 0 50% 0);
        animation: glitchTop 2.5s infinite linear alternate-reverse;
    }}
    
    .logo-text::after {{
        content: 'ORION';
        position: absolute;
        top: 0;
        left: -2px;
        color: rgba(100, 200, 255, 0.8);
        -webkit-text-fill-color: rgba(100, 200, 255, 0.8);
        clip-path: inset(50% 0 0 0);
        animation: glitchBottom 2.5s infinite linear alternate-reverse;
    }}
    
    @keyframes glitchTop {{
        0%, 90%, 100% {{ transform: translate(0); opacity: 0; }}
        92%, 94%, 96%, 98% {{ transform: translate(-2px, -1px); opacity: 0.8; }}
        93%, 95%, 97%, 99% {{ transform: translate(2px, 1px); opacity: 0.6; }}
    }}
    
    @keyframes glitchBottom {{
        0%, 90%, 100% {{ transform: translate(0); opacity: 0; }}
        92%, 94%, 96%, 98% {{ transform: translate(2px, 1px); opacity: 0.8; }}
        93%, 95%, 97%, 99% {{ transform: translate(-2px, -1px); opacity: 0.6; }}
    }}
    
    @keyframes morphGlow {{
        0%, 100% {{ 
            filter: brightness(1);
            text-shadow: 0 0 0 transparent;
        }}
        50% {{ 
            filter: brightness(1.1);
            text-shadow: 0 0 30px rgba(255, 255, 255, 0.3);
        }}
    }}
    
    .subtitle {{
        font-family: 'IBM Plex Mono', monospace !important;
        text-align: center;
        color: #666666 !important;
        -webkit-text-fill-color: #666666 !important;
        font-size: 0.75rem !important;
        font-weight: 400 !important;
        margin: 15px 0 0 0 !important;
        letter-spacing: 0.4em;
        text-transform: uppercase;
    }}
    
    /* ===== AUTH CARD - CLEAN BOXED LAYOUT ===== */
    .auth-card {{
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 2.5rem 2rem;
        max-width: 480px;
        margin: 1.5rem auto;
        box-shadow: var(--shadow-card);
        animation: fadeSlideIn 0.5s ease-out;
        position: relative;
        overflow: hidden;
    }}
    
    .auth-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--accent-gold), transparent);
        opacity: 0.6;
    }}
    
    .auth-card .stForm,
    .auth-card form {{
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
    }}
    
    .auth-card .stForm > div,
    .auth-card form > div {{
        width: 100%;
        max-width: 100%;
    }}
    
    @keyframes fadeSlideIn {{
        from {{
            opacity: 0;
            transform: translateY(20px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    
    /* ===== DASHBOARD CARDS - BOXED LAYOUT ===== */
    .dashboard-card {{
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 6px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: var(--shadow-card);
        transition: var(--transition-smooth);
        position: relative;
    }}
    
    .dashboard-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 3px;
        height: 100%;
        background: var(--accent-gold);
        opacity: 0;
        transition: var(--transition-smooth);
        border-radius: 6px 0 0 6px;
    }}
    
    .dashboard-card:hover {{
        background: var(--bg-hover);
        border-color: var(--border-hover);
        box-shadow: var(--shadow-hover);
        transform: translateX(4px);
    }}
    
    .dashboard-card:hover::before {{
        opacity: 1;
    }}
    
    .dashboard-card h3 {{
        color: var(--text-primary) !important;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }}
    
    .dashboard-card p {{
        color: var(--text-muted) !important;
        font-size: 0.85rem;
    }}
    
    .dashboard-card hr {{
        border: none;
        border-top: 1px solid var(--border-color);
        margin: 1rem 0;
    }}
    
    /* ===== INPUT FIELDS - CLEAN RETRO STYLE ===== */
    .stTextInput > div > div > input {{
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 4px !important;
        color: var(--text-primary) !important;
        padding: 0.9rem 1rem !important;
        font-size: 0.95rem !important;
        font-weight: 400 !important;
        transition: var(--transition-smooth);
        box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.3);
    }}
    
    .stTextInput > div > div > input:focus {{
        background: var(--bg-hover) !important;
        border-color: var(--accent-gold) !important;
        box-shadow: 0 0 0 2px var(--glow-gold), inset 0 1px 3px rgba(0, 0, 0, 0.3) !important;
        outline: none !important;
    }}
    
    .stTextInput > div > div > input::placeholder {{
        color: var(--text-muted) !important;
        opacity: 0.6;
    }}
    
    /* ===== SELECTBOX - FIXED DARK DROPDOWN ===== */
    .stSelectbox > div > div,
    .stSelectbox [data-baseweb="select"],
    .stSelectbox [data-baseweb="select"] > div {{
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 4px !important;
        color: var(--text-primary) !important;
        transition: var(--transition-smooth);
    }}
    
    .stSelectbox svg {{
        fill: var(--accent-gold) !important;
    }}
    
    /* Dropdown menu container - FORCE DARK BACKGROUND */
    .stSelectbox [role="listbox"],
    .stSelectbox [data-baseweb="popover"],
    .stSelectbox [data-baseweb="popover"] > div,
    .stSelectbox ul,
    div[data-baseweb="popover"],
    div[data-baseweb="menu"],
    div[data-baseweb="select"] ul {{
        background: #16161f !important;
        background-color: #16161f !important;
        border: 1px solid #2a2a3a !important;
        border-radius: 4px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6) !important;
    }}
    /* ===== DROPDOWN FIX - FORCE BLACK TEXT ===== */
    /* Target ALL dropdown/menu text to be BLACK */
    div[data-baseweb="popover"] *,
    div[data-baseweb="menu"] *,
    div[data-baseweb="select"] ul *,
    ul[role="listbox"] *,
    [role="listbox"] *,
    .stSelectbox ul * {{
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }}
    
    /* Menu container - white background */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    div[data-baseweb="menu"],
    ul[role="listbox"],
    [role="listbox"] {{
        background: #ffffff !important;
        background-color: #ffffff !important;
        border: 1px solid #333 !important;
        border-radius: 4px !important;
    }}
    
    /* Each option item */
    div[data-baseweb="menu"] li,
    div[data-baseweb="popover"] li,
    ul[role="listbox"] li,
    [role="option"] {{
        background: #ffffff !important;
        background-color: #ffffff !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        padding: 10px 14px !important;
        font-size: 0.9rem !important;
    }}
    
    /* Hover state */
    div[data-baseweb="menu"] li:hover,
    div[data-baseweb="popover"] li:hover,
    ul[role="listbox"] li:hover,
    [role="option"]:hover {{
        background: #e0e0e0 !important;
        background-color: #e0e0e0 !important;
        color: #000000 !important;
    }}
    
    /* Selected/highlighted option */
    [role="option"][aria-selected="true"],
    li[aria-selected="true"] {{
        background: #d0d0d0 !important;
        color: #000000 !important;
        font-weight: 600 !important;
    }}
    
    /* Keep the selectbox trigger text light */
    .stSelectbox [data-baseweb="select"] span,
    .stSelectbox [data-baseweb="select"] div {{
        color: var(--text-primary) !important;
        -webkit-text-fill-color: var(--text-primary) !important;
    }}
    
    /* ===== INPUT LABELS ===== */
    .stTextInput > label, 
    .stSelectbox > label,
    .stNumberInput > label,
    .stFileUploader > label {{
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        margin-bottom: 0.5rem !important;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }}
    
    /* ===== BUTTONS - CLEAN RETRO ===== */
    .stButton > button,
    .stFormSubmitButton > button {{
        background: linear-gradient(180deg, var(--bg-hover) 0%, var(--bg-card) 100%) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 4px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
        transition: var(--transition-smooth) !important;
    }}
    
    .stButton > button:hover,
    .stFormSubmitButton > button:hover {{
        background: linear-gradient(180deg, var(--bg-card) 0%, var(--bg-secondary) 100%) !important;
        border-color: var(--accent-gold) !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4), 0 0 20px var(--glow-gold) !important;
        transform: translateY(-2px);
        color: var(--accent-gold) !important;
    }}
    
    .stButton > button:active,
    .stFormSubmitButton > button:active {{
        transform: translateY(0);
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.4) !important;
    }}
    
    /* ===== TABS - BOXED RETRO STYLE ===== */
    .stTabs [data-baseweb="tab-list"] {{
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 4px !important;
        padding: 4px !important;
        gap: 4px !important;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: transparent !important;
        color: var(--text-muted) !important;
        border-radius: 3px !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        padding: 0.7rem 1.25rem !important;
        transition: var(--transition-smooth);
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }}
    
    .stTabs [data-baseweb="tab"]:hover {{
        background: var(--bg-hover) !important;
        color: var(--text-secondary) !important;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
    }}
    
    /* Tab highlight bar */
    .stTabs [data-baseweb="tab-highlight"] {{
        background: var(--accent-gold) !important;
        height: 2px !important;
    }}
    
    /* ===== RADIO BUTTONS ===== */
    .stRadio > label {{
        color: var(--text-secondary) !important;
        font-weight: 500;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    
    .stRadio > div {{
        background: var(--bg-secondary);
        padding: 0.75rem 1rem;
        border-radius: 4px;
        border: 1px solid var(--border-color);
    }}
    
    .stRadio > div label {{
        color: var(--text-primary) !important;
    }}
    
    /* ===== ID BADGE ===== */
    .id-badge {{
        background: var(--bg-secondary);
        color: var(--accent-gold) !important;
        padding: 0.4rem 0.9rem;
        border-radius: 3px;
        font-weight: 600;
        font-size: 0.75rem;
        display: inline-block;
        border: 1px solid var(--border-color);
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }}
    
    /* ===== ALERTS ===== */
    .stSuccess {{
        background: rgba(125, 216, 125, 0.1) !important;
        border: 1px solid rgba(125, 216, 125, 0.3) !important;
        border-left: 3px solid var(--accent-green) !important;
        border-radius: 4px !important;
        color: var(--text-primary) !important;
    }}
    
    .stInfo {{
        background: rgba(90, 200, 216, 0.1) !important;
        border: 1px solid rgba(90, 200, 216, 0.3) !important;
        border-left: 3px solid var(--accent-cyan) !important;
        border-radius: 4px !important;
        color: var(--text-primary) !important;
    }}
    
    .stWarning {{
        background: rgba(212, 168, 83, 0.1) !important;
        border: 1px solid rgba(212, 168, 83, 0.3) !important;
        border-left: 3px solid var(--accent-gold) !important;
        border-radius: 4px !important;
        color: var(--text-primary) !important;
    }}
    
    .stError {{
        background: rgba(232, 93, 93, 0.1) !important;
        border: 1px solid rgba(232, 93, 93, 0.3) !important;
        border-left: 3px solid var(--accent-red) !important;
        border-radius: 4px !important;
        color: var(--text-primary) !important;
    }}
    
    /* ===== PROGRESS BAR ===== */
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, var(--accent-gold) 0%, var(--accent-amber) 100%) !important;
        border-radius: 2px !important;
    }}
    
    /* ===== SPINNER ===== */
    .stSpinner > div {{
        border-top-color: var(--accent-gold) !important;
    }}
    
    /* ===== FILE UPLOADER ===== */
    .stFileUploader {{
        background: var(--bg-secondary) !important;
        border: 1px dashed var(--border-color) !important;
        border-radius: 4px !important;
        padding: 1rem !important;
    }}
    
    .stFileUploader:hover {{
        border-color: var(--accent-gold) !important;
        background: var(--bg-hover) !important;
    }}
    
    /* ===== TEXT AREA ===== */
    .stTextArea textarea {{
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 4px !important;
        color: var(--text-primary) !important;
        font-family: var(--font-mono) !important;
        transition: var(--transition-smooth);
    }}
    
    .stTextArea textarea:focus {{
        border-color: var(--accent-gold) !important;
        box-shadow: 0 0 0 2px var(--glow-gold) !important;
    }}
    
    /* ===== NUMBER INPUT ===== */
    .stNumberInput input {{
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 4px !important;
        color: var(--text-primary) !important;
    }}
    
    /* ===== CHECKBOX ===== */
    .stCheckbox label {{
        color: var(--text-primary) !important;
    }}
    
    .stCheckbox label span {{
        color: var(--text-secondary) !important;
    }}
    
    /* ===== MARKDOWN HEADERS IN AUTH CARD ===== */
    .auth-card h1, .auth-card h2, .auth-card h3, .auth-card h4 {{
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        margin: 1.25rem 0 0.75rem 0 !important;
    }}
    
    .auth-card h3 {{
        font-size: 1rem !important;
        border-bottom: 1px solid var(--border-color);
        padding-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }}
    
    .auth-card p, .auth-card span, .auth-card div {{
        color: var(--text-secondary) !important;
    }}
    
    /* ===== AUTH TITLE STYLES ===== */
    .auth-title {{
        color: var(--text-primary) !important;
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        text-align: center;
        margin-bottom: 0.25rem !important;
        letter-spacing: 0.05em;
    }}
    
    .auth-subtitle {{
        color: var(--text-muted) !important;
        font-size: 0.8rem;
        text-align: center;
        margin-bottom: 1.5rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }}
    
    /* ===== TIMER DISPLAY ===== */
    .timer-display {{
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 4px;
        padding: 0.75rem 1.25rem;
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--accent-gold) !important;
        text-align: center;
        letter-spacing: 0.1em;
        font-variant-numeric: tabular-nums;
        box-shadow: var(--shadow-card);
    }}
    
    /* ===== DIVIDER ===== */
    hr {{
        border: none;
        border-top: 1px solid var(--border-color);
        margin: 1.5rem 0;
    }}
    
    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: var(--bg-primary);
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: var(--border-color);
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: var(--border-hover);
    }}
    
    /* ===== TABLES ===== */
    .stDataFrame {{
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 4px !important;
    }}
    
    .stDataFrame th {{
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-size: 0.8rem !important;
    }}
    
    .stDataFrame td {{
        color: var(--text-secondary) !important;
        border-color: var(--border-color) !important;
    }}
    
    /* ===== EXPANDER ===== */
    .streamlit-expanderHeader {{
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 4px !important;
        color: var(--text-primary) !important;
    }}
    
    .streamlit-expanderContent {{
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-color) !important;
        border-top: none !important;
    }}
    
    /* ===== SIDEBAR (if used) ===== */
    [data-testid="stSidebar"] {{
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border-color) !important;
    }}
    
    /* ===== COLUMN LAYOUT FIX ===== */
    [data-testid="column"] {{
        padding: 0 0.5rem !important;
    }}
</style>
""", unsafe_allow_html=True)


# ========== SESSION STATE ==========
def init_session():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'auth_mode' not in st.session_state:
        st.session_state.auth_mode = 'login'
    if 'page' not in st.session_state:
        st.session_state.page = 'dashboard'
    if 'selected_students' not in st.session_state:
        st.session_state.selected_students = []
    if 'exam_timer' not in st.session_state:
        st.session_state.exam_timer = None


# ========== VIDEO PROCTORING ==========
class ProctoringProcessor(VideoTransformerBase):
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.warning_count = 0
        self.lock = threading.Lock()
        self.last_face_center = None
        self.frame_count = 0

    def get_warning_count(self):
        with self.lock:
            return self.warning_count

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        self.frame_count += 1
        height, width = img.shape[:2]
        center_x, center_y = width // 2, height // 2
        
        status_color = (0, 255, 0) # Green
        status_text = "Proctoring Active"
        
        if len(faces) == 0:
            status_color = (0, 0, 255) # Red
            status_text = "WARNING: Face not detected!"
            if self.frame_count % 30 == 0: # Check every ~1 second
                with self.lock:
                    self.warning_count += 1
        elif len(faces) > 1:
            status_color = (0, 0, 255)
            status_text = "WARNING: Multiple faces detected!"
            if self.frame_count % 30 == 0:
                with self.lock:
                    self.warning_count += 1
        else:
            # Movement detection
            (x, y, w, h) = faces[0]
            face_center = (x + w//2, y + h//2)
            
            # Use specific color for face box
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # Check displacement
            if self.last_face_center:
                dist = np.sqrt((face_center[0] - self.last_face_center[0])**2 + 
                             (face_center[1] - self.last_face_center[1])**2)
                if dist > 50: # Significant movement threshold
                    status_color = (0, 165, 255) # Orange
                    status_text = "WARNING: Excessive Movement!"
                    if self.frame_count % 30 == 0:
                        with self.lock:
                            self.warning_count += 1
            
            self.last_face_center = face_center

        # Overlay HUD
        cv2.putText(img, status_text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
        
        with self.lock:
            warnings = self.warning_count
            
        remaining = max(0, 5 - warnings)
        cv2.putText(img, f"Warnings Left: {remaining}", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        if remaining == 0:
             cv2.putText(img, "EXAM TERMINATED", (center_x - 150, center_y), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 4)

        return img


# ========== AUTHENTICATION ==========
def render_auth():
    import streamlit.components.v1 as components
    
    # Check if we should show welcome screen
    if 'welcome_shown' not in st.session_state:
        st.session_state.welcome_shown = False
    
    if not st.session_state.welcome_shown:
        # Load ORION logo as base64
        orion_logo_b64 = get_base64_image(ORION_LOGO_PATH)
        
        # Show welcome animation
        welcome_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:wght@400;600;700&display=swap');
                
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                    font-family: 'IBM Plex Mono', monospace;
                    cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Ccircle cx='12' cy='12' r='4' fill='%23d4a853'/%3E%3Ccircle cx='12' cy='12' r='8' fill='none' stroke='%23d4a853' stroke-width='1' opacity='0.5'/%3E%3C/svg%3E") 12 12, auto;
                }}
                
                body {{
                    background: linear-gradient(165deg, #0a0a12 0%, #0d0d18 50%, #101020 100%);
                    min-height: 100vh;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    overflow: hidden;
                }}
                
                /* Ambient golden glow */
                body::before {{
                    content: '';
                    position: fixed;
                    top: 0; left: 0; right: 0; bottom: 0;
                    background: 
                        radial-gradient(ellipse at 50% 30%, rgba(212, 168, 83, 0.08) 0%, transparent 50%),
                        radial-gradient(ellipse at 30% 70%, rgba(201, 162, 39, 0.05) 0%, transparent 40%),
                        radial-gradient(ellipse at 70% 60%, rgba(212, 168, 83, 0.06) 0%, transparent 45%);
                    pointer-events: none;
                    animation: ambientPulse 4s ease-in-out infinite alternate;
                }}
                
                @keyframes ambientPulse {{
                    0% {{ opacity: 0.6; }}
                    100% {{ opacity: 1; }}
                }}
                
                .welcome-container {{
                    text-align: center;
                    z-index: 1;
                }}
                
                /* KLAXON-style enterprise title */
                .title-container {{
                    display: flex;
                    justify-content: center;
                    margin-bottom: 20px;
                }}
                
                .wave-letter {{
                    font-family: 'Bebas Neue', 'Impact', sans-serif;
                    font-size: 6rem;
                    font-weight: 700;
                    color: #ffffff;
                    text-shadow: none;
                    display: inline-block;
                    animation: glitchLetter 3s ease-in-out infinite;
                    animation-delay: calc(var(--i) * 0.15s);
                    letter-spacing: 0.1em;
                }}
                
                @keyframes glitchLetter {{
                    0%, 90%, 100% {{
                        transform: translateY(0) skewX(0deg);
                        color: #ffffff;
                        text-shadow: 0 0 0 transparent;
                    }}
                    92% {{
                        transform: translateY(-5px) skewX(-2deg);
                        color: #ff6b6b;
                        text-shadow: 2px 0 #00ffff, -2px 0 #ff0066;
                    }}
                    94% {{
                        transform: translateY(5px) skewX(2deg);
                        color: #6bffff;
                        text-shadow: -2px 0 #ff6b6b, 2px 0 #0066ff;
                    }}
                    96% {{
                        transform: translateY(-3px) skewX(-1deg);
                        color: #ffffff;
                        text-shadow: 1px 0 #ff0066, -1px 0 #00ffff;
                    }}
                }}
                
                .subtitle {{
                    color: #9a9585;
                    font-size: 0.9rem;
                    letter-spacing: 0.4em;
                    text-transform: uppercase;
                    margin-bottom: 30px;
                    animation: fadeIn 1s ease-out 1.5s both;
                }}
                
                /* Logo image styling */
                .logo-image {{
                    width: 120px;
                    height: auto;
                    margin-bottom: 30px;
                    animation: logoFloat 3s ease-in-out infinite, fadeIn 1s ease-out 0.5s both;
                    filter: drop-shadow(0 0 20px rgba(212, 168, 83, 0.4)) 
                            drop-shadow(0 0 40px rgba(212, 168, 83, 0.2));
                }}
                
                @keyframes logoFloat {{
                    0%, 100% {{ transform: translateY(0) scale(1); }}
                    50% {{ transform: translateY(-8px) scale(1.02); }}
                }}
                
                @keyframes fadeIn {{
                    from {{ opacity: 0; transform: translateY(10px); }}
                    to {{ opacity: 1; transform: translateY(0); }}
                }}
                
                /* Round loader */
                .loader-container {{
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    animation: fadeIn 1s ease-out 2s both;
                }}
                
                .round-loader {{
                    width: 50px;
                    height: 50px;
                    border: 3px solid #2a2a3a;
                    border-top: 3px solid #d4a853;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                    margin-bottom: 20px;
                    box-shadow: 0 0 20px rgba(212, 168, 83, 0.2);
                }}
                
                @keyframes spin {{
                    0% {{ transform: rotate(0deg); }}
                    100% {{ transform: rotate(360deg); }}
                }}
                
                .loading-text {{
                    color: #9a9585;
                    font-size: 0.8rem;
                    letter-spacing: 0.2em;
                    text-transform: uppercase;
                }}
                
                .loading-dots::after {{
                    content: '';
                    animation: dots 1.5s steps(4, end) infinite;
                }}
                
                @keyframes dots {{
                    0% {{ content: ''; }}
                    25% {{ content: '.'; }}
                    50% {{ content: '..'; }}
                    75% {{ content: '...'; }}
                    100% {{ content: ''; }}
                }}
                
                /* Golden particles */
                .particle {{
                    position: fixed;
                    width: 4px;
                    height: 4px;
                    background: #d4a853;
                    border-radius: 50%;
                    pointer-events: none;
                    opacity: 0;
                    animation: float 8s ease-in-out infinite;
                }}
                
                @keyframes float {{
                    0%, 100% {{
                        opacity: 0;
                        transform: translateY(100vh) scale(0);
                    }}
                    10% {{
                        opacity: 0.8;
                    }}
                    90% {{
                        opacity: 0.3;
                    }}
                    100% {{
                        opacity: 0;
                        transform: translateY(-100vh) scale(1);
                    }}
                }}
            </style>
        </head>
        <body>
            <!-- Golden particles -->
            <div class="particle" style="left: 10%; animation-delay: 0s;"></div>
            <div class="particle" style="left: 20%; animation-delay: 1s;"></div>
            <div class="particle" style="left: 35%; animation-delay: 2s;"></div>
            <div class="particle" style="left: 50%; animation-delay: 0.5s;"></div>
            <div class="particle" style="left: 65%; animation-delay: 1.5s;"></div>
            <div class="particle" style="left: 80%; animation-delay: 2.5s;"></div>
            <div class="particle" style="left: 90%; animation-delay: 0.8s;"></div>
            
            <div class="welcome-container">
                <!-- ORION Logo -->
                <img src="data:image/png;base64,{orion_logo_b64}" class="logo-image" alt="ORION Logo">
                
                <div class="title-container">
                    <span class="wave-letter" style="--i: 0">O</span>
                    <span class="wave-letter" style="--i: 1">R</span>
                    <span class="wave-letter" style="--i: 2">I</span>
                    <span class="wave-letter" style="--i: 3">O</span>
                    <span class="wave-letter" style="--i: 4">N</span>
                </div>
                <div class="subtitle">AI Viva Voce Examiner</div>
                
                <div class="loader-container">
                    <div class="round-loader"></div>
                    <div class="loading-text">Initializing<span class="loading-dots"></span></div>
                </div>
            </div>
            
            <script>
                // Auto-redirect after animation
                setTimeout(function() {{
                    localStorage.setItem('welcome_complete', 'true');
                    window.location.reload();
                }}, 4000);
            </script>
        </body>
        </html>
        """
        
        # Check if welcome was already completed
        components.html("""
        <script>
            if (localStorage.getItem('welcome_complete') === 'true') {
                localStorage.removeItem('welcome_complete');
                window.parent.postMessage({type: 'streamlit:setComponentValue', value: true}, '*');
            }
        </script>
        """, height=0)
        
        # Show welcome screen
        components.html(welcome_html, height=600, scrolling=False)
        
        # Auto-progress after delay
        time.sleep(4)
        st.session_state.welcome_shown = True
        st.rerun()
        return
    
    # Regular auth page
    st.markdown(f"""
    <div class="logo-container">
        <h1 class="logo-text">ORION</h1>
        <p class="subtitle">AI VIVA VOCE EXAMINER</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    
    tab_login, tab_reg = st.tabs(["🔐 Sign In", "📝 Create Account"])
    
    with tab_login:
        st.markdown('<h2 class="auth-title">Welcome Back</h2>', unsafe_allow_html=True)
        st.markdown('<p class="auth-subtitle">Login to access your examinations</p>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            email = st.text_input("📧 Email")
            password = st.text_input("🔒 Password", type="password")
            submit = st.form_submit_button("Log In", use_container_width=True)
            
            if submit:
                if email and password:
                    user = authenticate_user(email, password)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user = user
                        st.session_state.page = 'dashboard'
                        st.rerun()
                    else:
                        st.error("❌ Invalid email or password")
    
    with tab_reg:
        st.markdown('<h2 class="auth-title">Create Account</h2>', unsafe_allow_html=True)
        st.markdown('<p class="auth-subtitle">Join ORION today</p>', unsafe_allow_html=True)
        
        # Teacher vs Student Selection (OUTSIDE FORM to trigger rerun)
        user_type = st.radio("I am a:", ["Student", "Teacher"], horizontal=True, key="reg_role_radio")
        
        selected_class = None
        
        if user_type == "Student":
            st.markdown("### Academic Details")
            # Stream selection (OUTSIDE FORM to trigger rerun)
            stream = st.selectbox("Select Stream/Level", ["School", "B.Tech", "M.Tech", "PhD"], key="reg_stream_select")
            
            current_year_options = []
            if stream == "School":
                current_year_options = ["Class 9", "Class 10", "Class 11", "Class 12"]
            elif stream == "B.Tech":
                current_year_options = ["1st Year", "2nd Year", "3rd Year", "4th Year"]
            elif stream == "M.Tech":
                current_year_options = ["1st Year", "2nd Year"]
            elif stream == "PhD":
                current_year_options = ["Research Scholar"]
        
        # Password validation function
        def check_password_strength(password):
            """Check password strength and return details"""
            checks = {
                'length': len(password) >= 8,
                'uppercase': any(c.isupper() for c in password),
                'lowercase': any(c.islower() for c in password),
                'number': any(c.isdigit() for c in password),
                'special': any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
            }
            
            passed = sum(checks.values())
            
            if passed <= 2:
                strength = 'weak'
                color = '#e85d5d'
            elif passed <= 3:
                strength = 'fair'
                color = '#d4a853'
            elif passed <= 4:
                strength = 'good'
                color = '#5ac8d8'
            else:
                strength = 'strong'
                color = '#7dd87d'
            
            return checks, strength, color, passed
        
        with st.form("register_form"):
            name = st.text_input("Full Name")
            reg_email = st.text_input("Email Address")
            reg_pass = st.text_input("Create Password", type="password", key="reg_pass_input")
            reg_pass_confirm = st.text_input("Confirm Password", type="password")
            
            if user_type == "Student":
                # Year selection (Inside form is fine as options are already set)
                year_val = st.selectbox("Current Class/Year", current_year_options)
                selected_class = f"{stream} - {year_val}"
            
            role = "teacher" if user_type == "Teacher" else "student"
            
            reg_submit = st.form_submit_button("Create Account", use_container_width=True)
            
            if reg_submit:
                # Validate password
                if not name or not reg_email or not reg_pass:
                    st.warning("⚠️ Please fill all fields")
                elif reg_pass != reg_pass_confirm:
                    st.error("❌ Passwords do not match")
                else:
                    checks, strength, color, passed = check_password_strength(reg_pass)
                    
                    if passed < 4:
                        st.error("❌ Password is too weak. Please meet at least 4 requirements.")
                    else:
                        # If teacher, class is None or "Teacher"
                        final_class = "Faculty" if role == "teacher" else selected_class
                        
                        result = create_user(name, reg_email, reg_pass, role, final_class)
                        if 'error' not in result:
                            st.success("✅ Account created successfully! Please Login.")
                        else:
                            st.error(f"❌ {result['error']}")
        
        # Password strength indicator (outside form for real-time update)
        st.markdown("### Password Requirements")
        
        # Add password strength meter with JavaScript
        components.html("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&display=swap');
            
            .password-container {
                font-family: 'IBM Plex Mono', monospace;
                background: #12121a;
                border: 1px solid #2a2a3a;
                border-radius: 6px;
                padding: 16px;
            }
            
            .strength-bar-container {
                height: 6px;
                background: #2a2a3a;
                border-radius: 3px;
                margin-bottom: 16px;
                overflow: hidden;
            }
            
            .strength-bar {
                height: 100%;
                border-radius: 3px;
                transition: all 0.3s ease;
                width: 0%;
            }
            
            .strength-label {
                font-size: 0.75rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                margin-bottom: 12px;
                display: flex;
                justify-content: space-between;
            }
            
            .requirement {
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 6px 0;
                font-size: 0.75rem;
                color: #9a9585;
                transition: all 0.2s ease;
            }
            
            .requirement.met {
                color: #7dd87d;
            }
            
            .requirement .icon {
                width: 16px;
                height: 16px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 10px;
                border: 1px solid currentColor;
            }
            
            .requirement.met .icon {
                background: #7dd87d;
                border-color: #7dd87d;
                color: #0a0a12;
            }
        </style>
        
        <div class="password-container">
            <div class="strength-label">
                <span style="color: #f5f0dc;">Password Strength</span>
                <span id="strength-text" style="color: #9a9585;">Enter password</span>
            </div>
            <div class="strength-bar-container">
                <div class="strength-bar" id="strength-bar"></div>
            </div>
            
            <div class="requirement" id="req-length">
                <span class="icon">✓</span>
                <span>At least 8 characters</span>
            </div>
            <div class="requirement" id="req-upper">
                <span class="icon">✓</span>
                <span>One uppercase letter (A-Z)</span>
            </div>
            <div class="requirement" id="req-lower">
                <span class="icon">✓</span>
                <span>One lowercase letter (a-z)</span>
            </div>
            <div class="requirement" id="req-number">
                <span class="icon">✓</span>
                <span>One number (0-9)</span>
            </div>
            <div class="requirement" id="req-special">
                <span class="icon">✓</span>
                <span>One special character (!@#$%...)</span>
            </div>
        </div>
        
        <script>
            function checkPassword() {
                // Try to get password from Streamlit input
                const inputs = window.parent.document.querySelectorAll('input[type="password"]');
                let password = '';
                
                // Find the registration password field (usually the one with specific key)
                inputs.forEach(input => {
                    if (input.closest('[data-testid]')) {
                        const testId = input.closest('[data-testid]').getAttribute('data-testid');
                        if (testId && testId.includes('password')) {
                            // Get the first password in registration form
                        }
                    }
                    // Use the second password input (registration) if exists
                    if (inputs.length >= 2) {
                        password = inputs[1].value;
                    } else if (inputs.length === 1) {
                        password = inputs[0].value;
                    }
                });
                
                // Check requirements
                const checks = {
                    length: password.length >= 8,
                    upper: /[A-Z]/.test(password),
                    lower: /[a-z]/.test(password),
                    number: /[0-9]/.test(password),
                    special: /[!@#$%^&*()_+\\-=\\[\\]{}|;:,.<>?]/.test(password)
                };
                
                // Update UI
                const reqIds = ['length', 'upper', 'lower', 'number', 'special'];
                let passed = 0;
                
                reqIds.forEach(id => {
                    const el = document.getElementById('req-' + id);
                    if (checks[id]) {
                        el.classList.add('met');
                        passed++;
                    } else {
                        el.classList.remove('met');
                    }
                });
                
                // Update strength bar
                const bar = document.getElementById('strength-bar');
                const text = document.getElementById('strength-text');
                const percentage = (passed / 5) * 100;
                bar.style.width = percentage + '%';
                
                if (password.length === 0) {
                    bar.style.background = '#2a2a3a';
                    text.textContent = 'Enter password';
                    text.style.color = '#9a9585';
                } else if (passed <= 2) {
                    bar.style.background = '#e85d5d';
                    text.textContent = 'Weak';
                    text.style.color = '#e85d5d';
                } else if (passed <= 3) {
                    bar.style.background = '#d4a853';
                    text.textContent = 'Fair';
                    text.style.color = '#d4a853';
                } else if (passed <= 4) {
                    bar.style.background = '#5ac8d8';
                    text.textContent = 'Good';
                    text.style.color = '#5ac8d8';
                } else {
                    bar.style.background = 'linear-gradient(90deg, #7dd87d, #5ac8d8)';
                    text.textContent = 'Strong ✓';
                    text.style.color = '#7dd87d';
                }
            }
            
            // Check periodically
            setInterval(checkPassword, 300);
            checkPassword();
        </script>
        """, height=220)
    
    st.markdown('</div>', unsafe_allow_html=True)


# ========== TEACHER DASHBOARD ==========
def render_teacher_dashboard():
    user = st.session_state.user
    
    # Header with ID
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
        <h1 class="logo-text" style="font-size: 2rem;">ORION</h1>
        <div style="text-align: right;">
            <div style="font-weight: 600; font-size: 1.2rem;">{user['name']}</div>
            <div class="id-badge">Teacher ID: #{user['user_id']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()

    tab1, tab2, tab3 = st.tabs(["📋 My Exams", "➕ Create Exam", "👥 Manage Students"])
    
    with tab1:
        render_teacher_exams()
    
    with tab2:
        render_create_exam()
    
    with tab3:
        render_manage_students()


def render_teacher_exams():
    user = st.session_state.user
    exams = get_teacher_exams(user['user_id'])
    
    if exams:
        for exam in exams:
            st.markdown(f"""
            <div class="dashboard-card">
                <div style="float: right;" class="id-badge">CODE: {exam['join_code']}</div>
                <h3>{exam['title']}</h3>
                <p style="color: var(--text-muted);">Subject: {exam.get('subject_name', 'N/A')}</p>
                <hr>
                <div style="display: flex; gap: 1rem; align-items: center;">
                    <span style="background: {'#dcfce7' if exam['status'] == 'active' else '#fee2e2'}; 
                                 color: {'#166534' if exam['status'] == 'active' else '#991b1b'}; 
                                 padding: 4px 12px; border-radius: 8px; font-size: 0.8rem; font-weight: 600;">
                        {exam['status'].upper()}
                    </span>
                    <span style="font-size: 0.9rem; color: var(--text-muted);">👥 {exam.get('student_count', 0)} Students</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2, c3, c4 = st.columns(4)
            
            with c1:
                if st.button("✅ Activate & Start", key=f"activate_{exam['exam_id']}", use_container_width=True):
                    if exam['status'] == 'draft':
                        activate_exam(exam['exam_id'])
                        st.session_state.exam_timer = {
                            'exam_id': exam['exam_id'],
                            'start_time': datetime.now(),
                            'duration': 60  # 60 minutes default
                        }
                        st.rerun()
                    else:
                        st.session_state.current_exam = exam
                        st.session_state.page = 'live_exam'
                        st.rerun()
            
            with c2:
                if st.button("👥 Select Students", key=f"manage_{exam['exam_id']}", use_container_width=True):
                    st.session_state.current_exam = exam
                    st.session_state.page = 'select_students'
                    st.rerun()
            
            with c3:
                if st.button("📊 View Marks", key=f"marks_{exam['exam_id']}", use_container_width=True):
                    st.session_state.current_exam = exam
                    st.session_state.page = 'view_marks'
                    st.rerun()
            
            with c4:
                if exam['status'] == 'active':
                    if st.button("🔴 Close Exam", key=f"close_{exam['exam_id']}", use_container_width=True):
                        close_exam(exam['exam_id'])
                        st.rerun()
            
            st.markdown("---")
    else:
        st.info("📝 No exams created yet. Create your first exam!")


def render_create_exam():
    st.subheader("Create New Exam")
    user = st.session_state.user
    
    with st.form("create_exam_form"):
        title = st.text_input("Exam Title")
        
        subjects = get_all_subjects()
        if subjects:
            subject_names = [s['name'] for s in subjects]
            selected_subject = st.selectbox("Subject", subject_names)
            subject_id = subjects[subject_names.index(selected_subject)]['id']
        else:
            st.error("No subjects available")
            return
        
        num_questions = st.number_input("Number of Questions", 3, 10, 5)
        
        pdf = st.file_uploader("Upload Viva Material (PDF)", type=['pdf'])
        
        submit = st.form_submit_button("Create Exam", use_container_width=True)
        
        if submit and title:
            # Create exam
            exam = create_exam(user['user_id'], title, subject_id, num_questions=num_questions)
            
            # Process PDF if uploaded
            success = True
            if pdf:
                with st.spinner("📄 Processing Study Material..."):
                    try:
                        # Save file
                        pdf_path = settings.upload_dir / f"{exam['exam_id']}_{pdf.name}"
                        with open(pdf_path, "wb") as f:
                            f.write(pdf.read())
                            
                        # Process PDF
                        processor = get_pdf_processor()
                        chunks = processor.process_pdf(pdf_path)
                        
                        if not chunks:
                             st.error("❌ PDF extraction failed. No text found.")
                             success = False
                        else:
                             # Create Vector Store (Using Exam ID as Session ID)
                             vector_store = get_vector_store(exam['exam_id'])
                             vector_store.create_index(chunks)
                             
                             # Update DB
                             update_exam_pdf(exam['exam_id'], pdf.name)
                             st.success("✅ Study Material processed!")
                        
                    except Exception as e:
                        st.error(f"❌ Error processing PDF: {str(e)}")
                        success = False
            else:
                 st.warning("⚠️ No PDF uploaded. Exam will use generic questions.")
            
            if success:
                st.success(f"✅ Exam Created! Join Code: **{exam['join_code']}**")
                time.sleep(2)
                st.session_state.page = 'dashboard'
                st.rerun()


def render_manage_students():
    """Student selection with checkboxes"""
    if 'current_exam' not in st.session_state:
        st.info("Select an exam first to manage students")
        return
    
    exam = st.session_state.current_exam
    st.subheader(f"Select Students for: {exam['title']}")
    
    # Get all students organized by class
    all_students = get_all_students()
    
    # Group by class
    classes_dict = {}
    for student in all_students:
        class_name = student.get('class_name', 'Other')
        if class_name not in classes_dict:
            classes_dict[class_name] = []
        classes_dict[class_name].append(student)
    
    # Display by class with checkboxes
    selected_students = []
    
    for class_name, students in sorted(classes_dict.items()):
        st.markdown(f"### 🏫 {class_name}")
        
        select_all = st.checkbox(f"Select all from {class_name}", key=f"all_{class_name}")
        
        for student in students:
            default_checked = select_all
            if st.checkbox(
                f"{student['name']} ({student['email']})",
                key=f"student_{student['user_id']}",
                value=default_checked
            ):
                selected_students.append(student['user_id'])
        
        st.markdown("---")
    
    if st.button("📨 Grant Access & Send Notifications", use_container_width=True):
        if selected_students:
            grant_exam_access(exam['exam_id'], selected_students)
            st.success(f"✅ Access granted to {len(selected_students)} students!")
            time.sleep(1)
            st.session_state.page = 'dashboard'
            st.rerun()
        else:
            st.warning("Please select at least one student")


def render_live_exam():
    """Live exam monitoring with timer and real-time marks"""
    if 'current_exam' not in st.session_state:
        st.session_state.page = 'dashboard'
        st.rerun()
        return
    
    exam = st.session_state.current_exam
    
    # Timer display
    if 'exam_timer' in st.session_state and st.session_state.exam_timer:
        timer = st.session_state.exam_timer
        elapsed = (datetime.now() - timer['start_time']).total_seconds()
        remaining = timer['duration'] * 60 - elapsed
        
        if remaining > 0:
            mins = int(remaining // 60)
            secs = int(remaining % 60)
            st.markdown(f"""
            <div class="timer-display">
                ⏱️ {mins:02d}:{secs:02d}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="timer-display">⏰ TIME UP!</div>', unsafe_allow_html=True)
    
    st.subheader(f"📊 Live Exam: {exam['title']}")
    
    # Real-time marks table
    results = get_exam_results(exam['exam_id'])
    enrolled_students = get_exam_students(exam['exam_id'])
    
    if results or enrolled_students:
        st.markdown("### Student Progress")
        
        data = []
        for student in enrolled_students:
            student_result = next((r for r in results if r['student_id'] == student['user_id']), None)
            
            data.append({
                "Name": student['name'],
                "Class": student.get('class_name', 'N/A'),
                "Status": student.get('status', 'pending'),
                "Score": f"{student_result['total_score']:.1f}%" if student_result else "Not Started"
            })
        
        st.table(data)
    else:
        st.info("No students have started the exam yet")
    
    if st.button("← Back to Dashboard"):
        st.session_state.page = 'dashboard'
        st.rerun()


def render_view_marks():
    """View detailed marks for an exam"""
    if 'current_exam' not in st.session_state:
        st.session_state.page = 'dashboard'
        st.rerun()
        return
    
    exam = st.session_state.current_exam
    st.subheader(f"📊 Detailed Marks: {exam['title']}")
    
    results = get_exam_results(exam['exam_id'])
    
    if results:
        for result in results:
            st.markdown(f"""
            <div class="dashboard-card">
                <h4>{result['student_name']}</h4>
                <p>{result['student_email']}</p>
                <div style="font-size: 2rem; font-weight: 800; color: var(--primary);">
                    {result['total_score']:.1f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No submissions yet")
    
    if st.button("← Back to Dashboard"):
        st.session_state.page = 'dashboard'
        st.rerun()


# ========== STUDENT DASHBOARD ==========
def render_student_dashboard():
    user = st.session_state.user
    
    # Header with Student ID
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
        <h1 class="logo-text" style="font-size: 2rem;">ORION</h1>
        <div style="text-align: right;">
            <div style="font-weight: 600; font-size: 1.2rem;">{user['name']}</div>
            <div class="id-badge">Student ID: #{user['user_id']}</div>
            <div style="color: var(--text-muted); font-size: 0.9rem;">{user.get('class_name', 'N/A')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()

    tab1, tab2 = st.tabs(["📚 My Exams", "🔔 Notifications"])
    
    with tab1:
        exams = get_student_exams(user['user_id'])
        
        if exams:
            for exam in exams:
                st.markdown(f"""
                <div class="dashboard-card">
                    <h3>{exam['title']}</h3>
                    <p style="color: var(--text-muted);">Teacher: {exam.get('teacher_name')} | Subject: {exam.get('subject_name')}</p>
                    <span style="background: #f1f5f9; padding: 6px 14px; border-radius: 50px; 
                                 font-size: 0.8rem; font-weight: 600;">
                        {exam.get('access_status', 'pending').upper()}
                    </span>
                </div>
                """, unsafe_allow_html=True)
                
                if exam.get('access_status') != 'completed':
                    if st.button("▶️ Start AI Viva Exam", key=f"start_{exam['exam_id']}", use_container_width=True):
                        # Force Clear Previous State
                        for k in ['viva_questions', 'current_q_index', 'viva_history']:
                            if k in st.session_state:
                                del st.session_state[k]
                        
                        # Clear audio
                        for k in list(st.session_state.keys()):
                            if k.startswith("audio_"):
                                del st.session_state[k]

                        st.session_state.current_exam = exam
                        
                        # Use Exam ID for question generation so it uses the exam's PDF context
                        q_gen = get_question_generator(exam['exam_id'])
                        
                        with st.spinner("🤖 AI Examiner is analysing materials and generating 'tear-the-mind' questions..."):
                            questions = q_gen.generate_questions(exam.get('num_questions', 5))
                            
                            if not questions:
                                 # Fallback
                                from backend.question_generator import VivaQuestion
                                questions = [VivaQuestion(
                                    question_number=1,
                                    question_text="Could not generate questions. Please discuss your project overview.",
                                    expected_concepts=["Overview"],
                                    context_used="System Fallback",
                                    difficulty="General"
                                )]

                            st.session_state.viva_questions = questions
                            st.session_state.current_q_index = 0
                            st.session_state.viva_history = []
                            update_access_status(exam['exam_id'], user['user_id'], 'started')
                                
                        st.session_state.page = 'viva_exam'
                        st.rerun()
            
            st.markdown("---")
        else:
            st.info("No exams assigned yet")
            
    with tab2:
        notifs = get_user_notifications(user['user_id'])
        
        if notifs:
            for n in notifs:
                unread_border = "border-left: 4px solid var(--accent);" if not n['is_read'] else ""
                st.markdown(f"""
                <div class="dashboard-card" style="{unread_border}">
                    <b>{n['title']}</b><br>
                    <span style="color: var(--text-muted); font-size: 0.9rem;">{n['message']}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No notifications")

def render_viva_exam():
    """Real-time AI Viva Interface"""
    
    if 'current_exam' not in st.session_state:
        st.error("⚠️ No exam loaded. Redirecting to dashboard...")
        st.session_state.page = 'dashboard'
        st.rerun()
        return

    exam = st.session_state.current_exam
    user = st.session_state.user
    
    # Model Check (Strict Examiner Requirement)
    llm = get_llm_engine()
    if getattr(llm, 'model_name', '') == 'gemini-3-flash-preview':
        st.success("✅ Gemini 3 Flash Preview is active")
    else:
        st.error(f"❌ Model Issue: {llm.model_name}")
    
    questions = st.session_state.get('viva_questions', [])
    q_idx = st.session_state.get('current_q_index', 0)
    
    # SAFETY: Redirect if no questions
    if not questions:
        st.error("⚠️ Exam initialization failed. Please try starting again.")
        if st.button("Back to Dashboard"):
            st.session_state.page = 'dashboard'
            st.rerun()
        return

    # SAFETY: Ensure history exists
    if 'viva_history' not in st.session_state:
        st.session_state.viva_history = []
    # Check completion
    if q_idx >= len(questions):
        st.balloons()
        
        # Calculate final result
        total_score = sum([h['score'] for h in st.session_state.viva_history])
        final_score = (total_score / (len(questions) * 10)) * 100
        
        # Personalized Closing Speech with student name
        voice_engine = get_voice_engine()
        closing_key = "audio_closing"
        closing_message = f"Thank you, {user['name']}. Your viva examination is now complete. You may go."
        if closing_key not in st.session_state:
             _, audio_bytes = voice_engine.speak_question(closing_message)
             st.session_state[closing_key] = audio_bytes
        
        if st.session_state.get(closing_key):
             st.audio(st.session_state[closing_key], format="audio/mp3", autoplay=True)
        
        # Enhanced completion display
        from frontend.live_conversation import render_viva_completion_screen
        import streamlit.components.v1 as components
        
        completion_html = render_viva_completion_screen(
            student_name=user['name'],
            final_score=final_score,
            total_questions=len(questions),
            transcript_summary=st.session_state.viva_history
        )
        components.html(completion_html, height=500, scrolling=False)
        
        # Session completion feedback format
        st.markdown(f"""
        <div class="dashboard-card" style="margin-top: 1rem;">
            <h3 style="color: var(--accent-gold) !important; margin-bottom: 1rem;">📋 Session Summary</h3>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; text-align: center;">
                <div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary) !important;">{len(questions)}</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted) !important; text-transform: uppercase;">Questions</div>
                </div>
                <div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: var(--accent-gold) !important;">{final_score:.0f}%</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted) !important; text-transform: uppercase;">Score</div>
                </div>
                <div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: var(--accent-cyan) !important;">{len([h for h in st.session_state.viva_history if h['score'] >= 6])}</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted) !important; text-transform: uppercase;">Passed</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Return to Dashboard", use_container_width=True):
            update_access_status(exam['exam_id'], user['user_id'], 'completed')
            # Save results
            save_exam_result(
                exam['exam_id'], 
                user['user_id'], 
                st.session_state.viva_history, 
                [h['score'] for h in st.session_state.viva_history], 
                final_score
            )
            st.session_state.page = 'dashboard'
            del st.session_state.viva_questions
            del st.session_state.current_q_index
            st.rerun()
        return

    current_q = questions[q_idx]
    
    # Import modern live conversation interface
    from frontend.live_conversation import render_modern_viva_interface, render_viva_completion_screen
    import streamlit.components.v1 as components
    
    # Get model status for display
    model_status = getattr(llm, 'model_name', 'unknown')
    if hasattr(llm, '_demo_mode') and llm._demo_mode:
        model_status = "demo-mode"
    
    # Render the modern grid-view interface with full verification
    html_content = render_modern_viva_interface(
        question_text=current_q.question_text,
        question_number=q_idx + 1,
        total_questions=len(questions),
        timer_seconds=90,  # 90 seconds per question
        student_name=user['name'],
        model_status=model_status,
        difficulty=getattr(current_q, 'difficulty', 'Medium')
    )
    components.html(html_content, height=780, scrolling=False)
    
    # Play question audio
    voice_engine = get_voice_engine()
    q_audio_key = f"audio_q_{exam['exam_id']}_{q_idx}"
    if q_audio_key not in st.session_state:
        _, audio_bytes = voice_engine.speak_question(current_q.question_text)
        st.session_state[q_audio_key] = audio_bytes
    if st.session_state.get(q_audio_key):
        st.audio(st.session_state[q_audio_key], format="audio/mp3", autoplay=True)
    
    # JavaScript to check localStorage for voice answer
    components.html("""
    <script>
        const voiceAnswer = localStorage.getItem('viva_answer');
        const submitted = localStorage.getItem('viva_submitted');
        
        if (submitted === 'true' && voiceAnswer) {
            // Clear the flags
            localStorage.removeItem('viva_answer');
            localStorage.removeItem('viva_submitted');
            
            // Set the answer in Streamlit's text area
            const textareas = window.parent.document.querySelectorAll('textarea');
            textareas.forEach(ta => {
                if (ta.placeholder && ta.placeholder.includes('answer')) {
                    ta.value = voiceAnswer;
                    ta.dispatchEvent(new Event('input', { bubbles: true }));
                }
            });
            
            // Click submit button
            setTimeout(() => {
                const buttons = window.parent.document.querySelectorAll('button');
                buttons.forEach(btn => {
                    if (btn.textContent.includes('Submit')) {
                        btn.click();
                    }
                });
            }, 100);
        }
    </script>
    """, height=0)
    
    # Fallback text input with dark theme
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #000000 0%, #0a0a15 100%);
        padding: 15px 20px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.05);
        margin-top: 10px;
    ">
        <p style="color: #475569; font-size: 13px; margin: 0;">
            💡 Fallback: Type your answer if voice doesn't work
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    answer_text = None
    student_answer = st.text_area(
        "Type your answer:",
        height=80,
        key=f"answer_{q_idx}",
        placeholder="Type your answer here...",
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns([4, 1])
    with col1:
        submit = st.button("📤 Submit Answer", use_container_width=True, type="primary", key=f"submit_{q_idx}")
    with col2:
        skip = st.button("⏭️", use_container_width=True, key=f"skip_{q_idx}", help="Skip this question")
    
    if submit and student_answer.strip():
        answer_text = student_answer
    elif skip:
        answer_text = "I don't know the answer."
    
    # Evaluation
    if answer_text:
        with st.spinner("🧠 AI Examiner is evaluating..."):
            eval_result = backend_evaluate(
                current_q,
                answer_text,
                "",
                session_id=exam['exam_id']
            )
            
            # Store history
            st.session_state.viva_history.append({
                "question": current_q.question_text,
                "answer": answer_text,
                "evaluation": eval_result['evaluation'],
                "score": eval_result['score'],
                "feedback": eval_result['feedback']
            })
            
            # Show feedback
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%);
                padding: 1.5rem;
                border-radius: 15px;
                border-left: 5px solid #22c55e;
                margin-top: 15px;
            ">
                <div style="color: #22c55e; font-weight: bold; margin-bottom: 10px; font-size: 16px;">
                    🤖 AI Examiner Feedback
                </div>
                <div style="color: #ffffff; font-size: 15px; line-height: 1.6;">
                    {eval_result['feedback']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Speak feedback
            _, fb_audio = voice_engine.speak_feedback(eval_result['score'], eval_result['feedback'] + "... Moving to next question.")
            st.audio(fb_audio, format="audio/mp3", autoplay=True)
            
            time.sleep(3)
            
            # Next question
            st.session_state.current_q_index += 1
            st.rerun()




# ========== MAIN ==========
def main():
    init_session()
    
    if not st.session_state.authenticated:
        render_auth()
    else:
        user = st.session_state.user
        
        # Route to correct page
        if st.session_state.page == 'select_students':
            render_manage_students()
        elif st.session_state.page == 'live_exam':
            render_live_exam()
        elif st.session_state.page == 'view_marks':
            render_view_marks()
        elif st.session_state.page == 'viva_exam':
            render_viva_exam()
        elif user['role'] == 'teacher':
            render_teacher_dashboard()
        else:
            render_student_dashboard()


if __name__ == "__main__":
    main()
