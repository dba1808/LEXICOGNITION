"""
Modern Live Viva Interface v3 - COMPLETE SYSTEM
- Verified Camera & Microphone with retry
- Real-time voice transcription with auto-submit
- Strict model verification display
- Adaptive difficulty indicators
- Professional retro dark theme
- Complete error handling
"""
import streamlit as st
import streamlit.components.v1 as components
import base64
from pathlib import Path


def get_robot_avatar_base64():
    """Get the robot avatar as base64"""
    avatar_path = Path(__file__).parent.parent / "assets" / "ai_robot.png"
    if avatar_path.exists():
        with open(avatar_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


def render_modern_viva_interface(
    question_text: str, 
    question_number: int, 
    total_questions: int, 
    timer_seconds: int = 60,
    student_name: str = "Student",
    model_status: str = "gemini-3-flash-preview",
    difficulty: str = "Medium"
):
    """
    Render the complete modern grid-view viva interface with full verification
    """
    
    avatar_b64 = get_robot_avatar_base64()
    
    # Difficulty color coding
    difficulty_colors = {
        "easy": "#7dd87d",
        "medium": "#d4a853", 
        "hard": "#e85d5d"
    }
    diff_color = difficulty_colors.get(difficulty.lower(), "#d4a853")
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            /* ===== RETRO PROFESSIONAL DARK THEME - VIVA INTERFACE ===== */
            @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
            
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
                --transition-smooth: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
            }}
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'IBM Plex Mono', 'JetBrains Mono', monospace;
                /* Custom cursor */
                cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Ccircle cx='12' cy='12' r='4' fill='%23d4a853'/%3E%3Ccircle cx='12' cy='12' r='8' fill='none' stroke='%23d4a853' stroke-width='1' opacity='0.5'/%3E%3C/svg%3E") 12 12, auto;
            }}
            
            /* Pointer cursor for buttons */
            button, [role="button"] {{
                cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='28' height='28' viewBox='0 0 28 28'%3E%3Ccircle cx='14' cy='14' r='5' fill='%23f5d383'/%3E%3Ccircle cx='14' cy='14' r='10' fill='none' stroke='%23d4a853' stroke-width='2' opacity='0.7'/%3E%3Ccircle cx='14' cy='14' r='13' fill='none' stroke='%23d4a853' stroke-width='1' opacity='0.3'/%3E%3C/svg%3E") 14 14, pointer !important;
            }}
            
            body {{
                background: var(--bg-primary);
            }}
            
            .container {{
                background: linear-gradient(165deg, var(--bg-primary) 0%, #0d0d18 50%, #0f0f1a 100%);
                min-height: 720px;
                padding: 16px;
                border-radius: 8px;
                border: 1px solid var(--border-color);
                position: relative;
            }}
            
            /* Ambient glow */
            .container::before {{
                content: '';
                position: absolute;
                top: 0; left: 0; right: 0; bottom: 0;
                background: 
                    radial-gradient(ellipse at 20% 20%, rgba(90, 200, 216, 0.02) 0%, transparent 50%),
                    radial-gradient(ellipse at 80% 80%, rgba(212, 168, 83, 0.02) 0%, transparent 50%);
                pointer-events: none;
                border-radius: 8px;
            }}
            
            /* ===== STATUS BAR ===== */
            .status-bar {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 8px 14px;
                background: var(--bg-secondary);
                border: 1px solid var(--border-color);
                border-radius: 4px;
                margin-bottom: 12px;
                font-size: 0.7rem;
                position: relative;
                z-index: 1;
            }}
            
            .status-item {{
                display: flex;
                align-items: center;
                gap: 6px;
                color: var(--text-muted);
                text-transform: uppercase;
                letter-spacing: 0.08em;
            }}
            
            .status-dot {{
                width: 8px;
                height: 8px;
                border-radius: 2px;
                background: var(--text-muted);
            }}
            
            .status-dot.active {{
                background: var(--accent-green);
                animation: pulse 2s infinite;
            }}
            
            .status-dot.error {{
                background: var(--accent-red);
            }}
            
            .status-dot.checking {{
                background: var(--accent-gold);
                animation: blink 0.5s infinite;
            }}
            
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; box-shadow: 0 0 0 0 rgba(125, 216, 125, 0.4); }}
                50% {{ opacity: 0.8; box-shadow: 0 0 0 4px rgba(125, 216, 125, 0); }}
            }}
            
            @keyframes blink {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.3; }}
            }}
            
            .model-badge {{
                background: var(--bg-card);
                border: 1px solid var(--accent-cyan);
                color: var(--accent-cyan);
                padding: 4px 10px;
                border-radius: 3px;
                font-size: 0.65rem;
                font-weight: 600;
            }}
            
            /* ===== HEADER ===== */
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px 16px;
                background: var(--bg-card);
                border: 1px solid var(--border-color);
                border-radius: 6px;
                margin-bottom: 14px;
                position: relative;
                z-index: 1;
            }}
            
            .header::before {{
                content: '';
                position: absolute;
                top: 0; left: 0; right: 0;
                height: 2px;
                background: linear-gradient(90deg, transparent, var(--accent-gold), transparent);
                opacity: 0.5;
                border-radius: 6px 6px 0 0;
            }}
            
            .header-left {{
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .header-icon {{
                width: 34px;
                height: 34px;
                background: var(--bg-secondary);
                border: 1px solid var(--border-color);
                border-radius: 4px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 16px;
            }}
            
            .header-title {{
                color: var(--text-primary);
                font-size: 0.9rem;
                font-weight: 600;
                letter-spacing: 0.06em;
                text-transform: uppercase;
            }}
            
            .header-right {{
                display: flex;
                align-items: center;
                gap: 12px;
            }}
            
            .question-badge {{
                background: var(--bg-secondary);
                border: 1px solid var(--border-color);
                padding: 6px 12px;
                border-radius: 4px;
                color: var(--text-muted);
                font-size: 0.75rem;
                font-weight: 500;
            }}
            
            .question-badge span {{
                color: var(--accent-gold);
                font-weight: 700;
            }}
            
            .difficulty-badge {{
                background: var(--bg-secondary);
                border: 1px solid {diff_color};
                color: {diff_color};
                padding: 4px 10px;
                border-radius: 3px;
                font-size: 0.65rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.1em;
            }}
            
            /* ===== TIMER ===== */
            .timer {{
                display: flex;
                align-items: center;
                gap: 6px;
                background: var(--bg-secondary);
                border: 1px solid var(--border-color);
                padding: 6px 12px;
                border-radius: 4px;
                transition: var(--transition-smooth);
            }}
            
            .timer.warning {{
                border-color: var(--accent-gold);
                box-shadow: 0 0 12px rgba(212, 168, 83, 0.1);
            }}
            
            .timer.danger {{
                border-color: var(--accent-red);
                box-shadow: 0 0 12px rgba(232, 93, 93, 0.15);
                animation: timer-pulse 1s infinite;
            }}
            
            @keyframes timer-pulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.7; }}
            }}
            
            .timer-icon {{ font-size: 14px; }}
            
            .timer-value {{
                font-size: 0.9rem;
                font-weight: 700;
                color: var(--accent-green);
                font-variant-numeric: tabular-nums;
                letter-spacing: 0.05em;
            }}
            
            .timer.warning .timer-value {{ color: var(--accent-gold); }}
            .timer.danger .timer-value {{ color: var(--accent-red); }}
            
            /* ===== GRID ===== */
            .grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 14px;
                position: relative;
                z-index: 1;
            }}
            
            /* ===== PANELS ===== */
            .panel {{
                background: var(--bg-card);
                border: 1px solid var(--border-color);
                border-radius: 6px;
                padding: 16px;
                position: relative;
                transition: var(--transition-smooth);
            }}
            
            .panel::before {{
                content: '';
                position: absolute;
                top: 0; left: 0;
                width: 3px;
                height: 100%;
                opacity: 0;
                transition: var(--transition-smooth);
                border-radius: 6px 0 0 6px;
            }}
            
            .panel:hover {{ border-color: var(--border-hover); }}
            .panel:hover::before {{ opacity: 1; }}
            
            .ai-panel::before {{ background: var(--accent-cyan); }}
            .user-panel::before {{ background: var(--accent-gold); }}
            
            .panel-header {{
                display: flex;
                align-items: center;
                gap: 10px;
                margin-bottom: 12px;
                padding-bottom: 10px;
                border-bottom: 1px solid var(--border-color);
            }}
            
            .panel-avatar {{
                width: 36px;
                height: 36px;
                border-radius: 4px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                background: var(--bg-secondary);
                border: 1px solid var(--border-color);
            }}
            
            .ai-avatar {{ 
                border-color: var(--accent-cyan);
                box-shadow: 0 0 8px rgba(90, 200, 216, 0.1);
            }}
            .user-avatar {{ 
                border-color: var(--accent-gold);
                box-shadow: 0 0 8px var(--glow-gold);
            }}
            
            .panel-info h3 {{
                color: var(--text-primary);
                font-size: 0.8rem;
                font-weight: 600;
                margin-bottom: 2px;
                letter-spacing: 0.05em;
                text-transform: uppercase;
            }}
            
            .panel-info p {{
                color: var(--text-muted);
                font-size: 0.7rem;
            }}
            
            /* ===== AI PANEL ===== */
            .ai-panel {{ border-color: rgba(90, 200, 216, 0.15); }}
            
            .robot-container {{
                display: flex;
                justify-content: center;
                margin-bottom: 12px;
            }}
            
            .robot-wrapper {{
                position: relative;
                width: 80px;
                height: 80px;
            }}
            
            .robot-img {{
                width: 100%;
                height: 100%;
                border-radius: 4px;
                object-fit: cover;
                border: 2px solid var(--accent-cyan);
                box-shadow: 0 0 15px rgba(90, 200, 216, 0.2);
            }}
            
            .speak-ring {{
                position: absolute;
                inset: -6px;
                border-radius: 6px;
                border: 1px solid var(--accent-green);
                animation: ring-pulse 1.5s ease-out infinite;
            }}
            
            @keyframes ring-pulse {{
                0% {{ transform: scale(1); opacity: 0.6; }}
                100% {{ transform: scale(1.25); opacity: 0; }}
            }}
            
            .question-box {{
                background: var(--bg-secondary);
                border: 1px solid var(--border-color);
                border-radius: 4px;
                padding: 14px;
                position: relative;
            }}
            
            .question-box::before {{
                content: '"';
                position: absolute;
                top: 6px;
                left: 10px;
                font-size: 1.8rem;
                color: var(--accent-cyan);
                opacity: 0.3;
                font-family: Georgia, serif;
            }}
            
            .question-text {{
                color: var(--text-secondary);
                font-size: 0.8rem;
                line-height: 1.7;
                padding-left: 18px;
            }}
            
            /* ===== USER PANEL ===== */
            .user-panel {{ border-color: rgba(212, 168, 83, 0.15); }}
            
            #camera {{
                width: 100%;
                height: 120px;
                border-radius: 4px;
                background: var(--bg-secondary);
                object-fit: cover;
                transform: scaleX(-1);
                margin-bottom: 10px;
                border: 1px solid var(--border-color);
            }}
            
            /* Error overlay for camera */
            .camera-error {{
                position: absolute;
                top: 0; left: 0; right: 0; bottom: 0;
                background: rgba(10, 10, 18, 0.95);
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                color: var(--accent-red);
                font-size: 0.75rem;
                text-align: center;
                padding: 10px;
                border-radius: 4px;
            }}
            
            .camera-error button {{
                margin-top: 8px;
                background: var(--bg-card);
                border: 1px solid var(--accent-gold);
                color: var(--accent-gold);
                padding: 6px 12px;
                border-radius: 3px;
                cursor: pointer;
                font-size: 0.7rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }}
            
            .camera-container {{
                position: relative;
            }}
            
            .speak-section {{
                text-align: center;
                margin-top: 8px;
            }}
            
            .speak-btn {{
                width: 54px;
                height: 54px;
                border-radius: 4px;
                border: 1px solid var(--border-color);
                background: var(--bg-secondary);
                color: var(--text-primary);
                font-size: 22px;
                cursor: pointer;
                transition: var(--transition-smooth);
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
            }}
            
            .speak-btn:hover:not(:disabled) {{
                border-color: var(--accent-gold);
                box-shadow: 0 0 15px var(--glow-gold);
                transform: translateY(-2px);
            }}
            
            .speak-btn:disabled {{
                opacity: 0.4;
                cursor: not-allowed;
            }}
            
            .speak-btn.active {{
                background: var(--accent-red);
                border-color: var(--accent-red);
                box-shadow: 0 0 15px rgba(232, 93, 93, 0.3);
                animation: rec-pulse 1s infinite;
            }}
            
            @keyframes rec-pulse {{
                0%, 100% {{ box-shadow: 0 0 0 0 rgba(232, 93, 93, 0.4); }}
                50% {{ box-shadow: 0 0 0 8px rgba(232, 93, 93, 0); }}
            }}
            
            .speak-hint {{
                color: var(--text-muted);
                font-size: 0.65rem;
                margin-top: 6px;
                letter-spacing: 0.05em;
                text-transform: uppercase;
            }}
            
            /* ===== TRANSCRIPT ===== */
            .transcript {{
                background: var(--bg-secondary);
                border: 1px solid var(--border-color);
                border-radius: 4px;
                padding: 12px;
                margin-top: 10px;
            }}
            
            .transcript-header {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 8px;
            }}
            
            .transcript-label {{
                color: var(--accent-gold);
                font-size: 0.6rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.1em;
            }}
            
            .transcript-status {{
                display: flex;
                align-items: center;
                gap: 5px;
                font-size: 0.6rem;
                color: var(--text-muted);
                text-transform: uppercase;
            }}
            
            .transcript-content {{
                background: var(--bg-primary);
                border: 1px solid var(--border-color);
                border-radius: 3px;
                padding: 10px;
                min-height: 45px;
                color: var(--text-primary);
                font-size: 0.8rem;
                line-height: 1.5;
            }}
            
            .transcript-tip {{
                text-align: center;
                margin-top: 8px;
                font-size: 0.65rem;
                color: var(--text-muted);
            }}
            
            .transcript-tip strong {{
                color: var(--accent-gold);
            }}
            
            /* ===== INITIALIZATION OVERLAY ===== */
            .init-overlay {{
                position: absolute;
                top: 0; left: 0; right: 0; bottom: 0;
                background: rgba(10, 10, 18, 0.98);
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                z-index: 100;
                border-radius: 8px;
            }}
            
            .init-overlay.hidden {{
                display: none;
            }}
            
            .init-title {{
                color: var(--text-primary);
                font-size: 1.2rem;
                font-weight: 600;
                margin-bottom: 20px;
                text-transform: uppercase;
                letter-spacing: 0.1em;
            }}
            
            .init-checklist {{
                list-style: none;
                width: 280px;
            }}
            
            .init-item {{
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 10px 0;
                border-bottom: 1px solid var(--border-color);
                color: var(--text-muted);
                font-size: 0.8rem;
            }}
            
            .init-item.success {{ color: var(--accent-green); }}
            .init-item.error {{ color: var(--accent-red); }}
            .init-item.checking {{ color: var(--accent-gold); }}
            
            .init-icon {{
                width: 20px;
                text-align: center;
            }}
            
            .init-spinner {{
                width: 14px;
                height: 14px;
                border: 2px solid var(--border-color);
                border-top-color: var(--accent-gold);
                border-radius: 50%;
                animation: spin 0.8s linear infinite;
            }}
            
            @keyframes spin {{
                to {{ transform: rotate(360deg); }}
            }}
            
            .init-start-btn {{
                margin-top: 20px;
                background: var(--bg-card);
                border: 1px solid var(--accent-gold);
                color: var(--accent-gold);
                padding: 12px 24px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 0.85rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                transition: var(--transition-smooth);
            }}
            
            .init-start-btn:hover:not(:disabled) {{
                background: var(--accent-gold);
                color: var(--bg-primary);
            }}
            
            .init-start-btn:disabled {{
                opacity: 0.4;
                cursor: not-allowed;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <!-- INITIALIZATION OVERLAY -->
            <div class="init-overlay" id="init-overlay">
                <div class="init-title">🎓 Viva System Check</div>
                <ul class="init-checklist">
                    <li class="init-item" id="check-model">
                        <span class="init-icon"><div class="init-spinner"></div></span>
                        <span>Model: {model_status}</span>
                    </li>
                    <li class="init-item" id="check-camera">
                        <span class="init-icon"><div class="init-spinner"></div></span>
                        <span>Camera Permission</span>
                    </li>
                    <li class="init-item" id="check-mic">
                        <span class="init-icon"><div class="init-spinner"></div></span>
                        <span>Microphone Permission</span>
                    </li>
                    <li class="init-item" id="check-speech">
                        <span class="init-icon"><div class="init-spinner"></div></span>
                        <span>Speech Recognition</span>
                    </li>
                </ul>
                <button class="init-start-btn" id="start-btn" disabled onclick="startViva()">
                    Start Viva Examination
                </button>
                <div id="init-error" style="color: var(--accent-red); margin-top: 15px; font-size: 0.75rem; text-align: center; max-width: 280px;"></div>
            </div>
            
            <!-- STATUS BAR -->
            <div class="status-bar">
                <div class="status-item">
                    <div class="status-dot" id="cam-status"></div>
                    <span>Camera</span>
                </div>
                <div class="status-item">
                    <div class="status-dot" id="mic-status"></div>
                    <span>Microphone</span>
                </div>
                <div class="model-badge" id="model-badge">{model_status}</div>
                <div class="status-item">
                    <span>Student: {student_name}</span>
                </div>
            </div>
            
            <!-- HEADER -->
            <div class="header">
                <div class="header-left">
                    <div class="header-icon">🎓</div>
                    <div class="header-title">AI Viva Examination</div>
                </div>
                <div class="header-right">
                    <div class="difficulty-badge">{difficulty}</div>
                    <div class="question-badge">
                        Q <span>{question_number}</span> / <span>{total_questions}</span>
                    </div>
                    <div class="timer" id="timer">
                        <span class="timer-icon">⏱️</span>
                        <span class="timer-value" id="timer-value">{timer_seconds}s</span>
                    </div>
                </div>
            </div>
            
            <!-- GRID -->
            <div class="grid">
                <!-- AI PANEL -->
                <div class="panel ai-panel">
                    <div class="panel-header">
                        <div class="panel-avatar ai-avatar">🤖</div>
                        <div class="panel-info">
                            <h3>AI Examiner</h3>
                            <p id="ai-status">Speaking...</p>
                        </div>
                    </div>
                    
                    <div class="robot-container">
                        <div class="robot-wrapper">
                            <img src="data:image/png;base64,{avatar_b64}" class="robot-img" onerror="this.style.display='none'">
                            <div class="speak-ring" id="speak-ring"></div>
                        </div>
                    </div>
                    
                    <div class="question-box">
                        <div class="question-text">{question_text}</div>
                    </div>
                </div>
                
                <!-- USER PANEL -->
                <div class="panel user-panel">
                    <div class="panel-header">
                        <div class="panel-avatar user-avatar">👤</div>
                        <div class="panel-info">
                            <h3>{student_name}</h3>
                            <p id="user-status">Initializing...</p>
                        </div>
                    </div>
                    
                    <div class="camera-container">
                        <video id="camera" autoplay playsinline muted></video>
                        <div class="camera-error" id="camera-error" style="display: none;">
                            <div>📷 Camera Access Required</div>
                            <div style="font-size: 0.65rem; margin-top: 4px; color: var(--text-muted);">Please allow camera access to continue</div>
                            <button onclick="retryCamera()">Retry</button>
                        </div>
                    </div>
                    
                    <div class="speak-section">
                        <button class="speak-btn" id="speak-btn" disabled onclick="toggleSpeak()">🎤</button>
                        <div class="speak-hint" id="speak-hint">Initializing...</div>
                    </div>
                    
                    <div class="transcript">
                        <div class="transcript-header">
                            <span class="transcript-label">Your Answer</span>
                            <div class="transcript-status">
                                <div class="status-dot" id="rec-dot"></div>
                                <span id="rec-label">Ready</span>
                            </div>
                        </div>
                        <div class="transcript-content" id="transcript">
                            Waiting for initialization...
                        </div>
                        <div class="transcript-tip">
                            Say "<strong>Done</strong>" or "<strong>Submit</strong>" when finished
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <input type="hidden" id="answer-data" value="">
        
        <script>
            // ===== STATE MANAGEMENT =====
            let state = {{
                recording: false,
                recognition: null,
                transcript: '',
                timerValue: {timer_seconds},
                timerInterval: null,
                cameraReady: false,
                micReady: false,
                speechReady: false,
                modelReady: false,
                vivaStarted: false,
                retryCount: 0,
                maxRetries: 3
            }};
            
            // ===== INITIALIZATION =====
            async function initialize() {{
                console.log('🔄 Starting system verification...');
                
                // Check 1: Model verification
                await checkModel();
                
                // Check 2: Camera
                await checkCamera();
                
                // Check 3: Microphone (implicitly checked with camera for some browsers)
                await checkMicrophone();
                
                // Check 4: Speech Recognition
                checkSpeechRecognition();
                
                // Enable start button if all checks pass
                updateStartButton();
            }}
            
            async function checkModel() {{
                const item = document.getElementById('check-model');
                item.className = 'init-item checking';
                item.querySelector('.init-icon').innerHTML = '<div class="init-spinner"></div>';
                
                // Model is verified server-side, we just confirm it here
                const modelName = '{model_status}';
                
                await sleep(500);
                
                if (modelName.includes('gemini-3-flash-preview')) {{
                    state.modelReady = true;
                    item.className = 'init-item success';
                    item.querySelector('.init-icon').textContent = '✓';
                    document.getElementById('model-badge').style.borderColor = 'var(--accent-green)';
                    document.getElementById('model-badge').style.color = 'var(--accent-green)';
                }} else if (modelName.includes('demo')) {{
                    state.modelReady = true; // Allow demo mode
                    item.className = 'init-item checking';
                    item.querySelector('.init-icon').textContent = '⚠';
                    item.querySelector('span:last-child').textContent = 'Demo Mode (No API)';
                }} else {{
                    state.modelReady = false;
                    item.className = 'init-item error';
                    item.querySelector('.init-icon').textContent = '✗';
                    showInitError('Model verification failed. Required: gemini-3-flash-preview');
                }}
            }}
            
            async function checkCamera() {{
                const item = document.getElementById('check-camera');
                item.className = 'init-item checking';
                
                try {{
                    const stream = await navigator.mediaDevices.getUserMedia({{ 
                        video: {{ facingMode: 'user' }}, 
                        audio: false 
                    }});
                    
                    document.getElementById('camera').srcObject = stream;
                    state.cameraReady = true;
                    
                    item.className = 'init-item success';
                    item.querySelector('.init-icon').textContent = '✓';
                    
                    document.getElementById('cam-status').classList.add('active');
                    document.getElementById('camera-error').style.display = 'none';
                    document.getElementById('user-status').textContent = 'Camera Active';
                    
                }} catch(e) {{
                    console.error('Camera error:', e);
                    state.cameraReady = false;
                    
                    item.className = 'init-item error';
                    item.querySelector('.init-icon').textContent = '✗';
                    
                    document.getElementById('cam-status').classList.add('error');
                    document.getElementById('camera-error').style.display = 'flex';
                    
                    showInitError('Camera access denied. Click Retry on the camera panel.');
                }}
            }}
            
            async function checkMicrophone() {{
                const item = document.getElementById('check-mic');
                item.className = 'init-item checking';
                
                try {{
                    const stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
                    stream.getTracks().forEach(track => track.stop()); // Stop after permission check
                    
                    state.micReady = true;
                    
                    item.className = 'init-item success';
                    item.querySelector('.init-icon').textContent = '✓';
                    
                    document.getElementById('mic-status').classList.add('active');
                    
                }} catch(e) {{
                    console.error('Microphone error:', e);
                    state.micReady = false;
                    
                    item.className = 'init-item error';
                    item.querySelector('.init-icon').textContent = '✗';
                    
                    document.getElementById('mic-status').classList.add('error');
                    
                    showInitError('Microphone access denied. Please allow microphone access and refresh.');
                }}
            }}
            
            function checkSpeechRecognition() {{
                const item = document.getElementById('check-speech');
                
                if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
                    initSpeechRecognition();
                    state.speechReady = true;
                    
                    item.className = 'init-item success';
                    item.querySelector('.init-icon').textContent = '✓';
                }} else {{
                    state.speechReady = false;
                    
                    item.className = 'init-item error';
                    item.querySelector('.init-icon').textContent = '✗';
                    item.querySelector('span:last-child').textContent = 'Speech Recognition (Not Supported)';
                    
                    showInitError('Speech Recognition not supported. Use Chrome for best experience.');
                }}
            }}
            
            function initSpeechRecognition() {{
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                state.recognition = new SpeechRecognition();
                state.recognition.continuous = true;
                state.recognition.interimResults = true;
                state.recognition.lang = 'en-US';
                
                state.recognition.onresult = (e) => {{
                    state.transcript = '';
                    for (let i = 0; i < e.results.length; i++) {{
                        state.transcript += e.results[i][0].transcript;
                    }}
                    document.getElementById('transcript').textContent = state.transcript || 'Listening...';
                    document.getElementById('answer-data').value = state.transcript;
                    
                    // Auto-submit on keywords
                    const lower = state.transcript.toLowerCase();
                    if (lower.includes('done') || lower.includes("that's all") || lower.includes('submit') || lower.includes('i am done')) {{
                        autoSubmit();
                    }}
                }};
                
                state.recognition.onerror = (e) => {{
                    console.error('Speech recognition error:', e.error);
                    if (e.error === 'not-allowed') {{
                        showInitError('Microphone permission was denied for speech recognition.');
                    }}
                }};
                
                state.recognition.onend = () => {{
                    if (state.recording && state.vivaStarted) {{
                        state.recognition.start(); // Restart if still recording
                    }}
                }};
            }}
            
            function updateStartButton() {{
                const btn = document.getElementById('start-btn');
                const allReady = state.modelReady && state.cameraReady && state.micReady && state.speechReady;
                
                btn.disabled = !allReady;
                
                if (allReady) {{
                    btn.textContent = 'Start Viva Examination';
                }} else {{
                    btn.textContent = 'Fix Issues Above';
                }}
            }}
            
            function showInitError(msg) {{
                document.getElementById('init-error').textContent = msg;
            }}
            
            async function retryCamera() {{
                state.retryCount++;
                if (state.retryCount <= state.maxRetries) {{
                    await checkCamera();
                    updateStartButton();
                }} else {{
                    showInitError('Maximum retries reached. Please refresh the page and allow camera access.');
                }}
            }}
            
            // ===== VIVA START =====
            function startViva() {{
                state.vivaStarted = true;
                
                // Hide overlay
                document.getElementById('init-overlay').classList.add('hidden');
                
                // Enable speak button
                document.getElementById('speak-btn').disabled = false;
                document.getElementById('speak-hint').textContent = 'Click to Speak';
                document.getElementById('transcript').textContent = 'Click the microphone and speak your answer...';
                
                // Start timer
                startTimer();
                
                // AI speaking animation (play for 5s)
                setTimeout(() => {{
                    document.getElementById('speak-ring').style.animation = 'none';
                    document.getElementById('speak-ring').style.opacity = '0';
                    document.getElementById('ai-status').textContent = 'Waiting for your answer';
                }}, 5000);
            }}
            
            // ===== TIMER =====
            function startTimer() {{
                state.timerInterval = setInterval(() => {{
                    state.timerValue--;
                    const el = document.getElementById('timer-value');
                    const timer = document.getElementById('timer');
                    el.textContent = state.timerValue + 's';
                    
                    if (state.timerValue <= 10) {{
                        timer.className = 'timer danger';
                    }} else if (state.timerValue <= 30) {{
                        timer.className = 'timer warning';
                    }}
                    
                    if (state.timerValue <= 0) {{
                        clearInterval(state.timerInterval);
                        autoSubmit();
                    }}
                }}, 1000);
            }}
            
            // ===== SPEAK TOGGLE =====
            function toggleSpeak() {{
                if (!state.vivaStarted) return;
                
                const btn = document.getElementById('speak-btn');
                const hint = document.getElementById('speak-hint');
                const dot = document.getElementById('rec-dot');
                const label = document.getElementById('rec-label');
                
                if (!state.recording) {{
                    try {{
                        state.recognition?.start();
                        state.recording = true;
                        btn.className = 'speak-btn active';
                        btn.textContent = '🔴';
                        hint.textContent = 'Speaking...';
                        dot.classList.add('active');
                        label.textContent = 'Recording';
                        document.getElementById('transcript').textContent = 'Listening...';
                    }} catch(e) {{
                        console.error('Failed to start recognition:', e);
                    }}
                }} else {{
                    state.recognition?.stop();
                    state.recording = false;
                    btn.className = 'speak-btn';
                    btn.textContent = '🎤';
                    hint.textContent = 'Click to Speak';
                    dot.classList.remove('active');
                    label.textContent = 'Stopped';
                }}
            }}
            
            // ===== AUTO SUBMIT =====
            function autoSubmit() {{
                if (state.recording) {{
                    state.recognition?.stop();
                    state.recording = false;
                }}
                
                clearInterval(state.timerInterval);
                
                const btn = document.getElementById('speak-btn');
                btn.className = 'speak-btn';
                btn.textContent = '✅';
                btn.disabled = true;
                document.getElementById('speak-hint').textContent = 'Submitted!';
                document.getElementById('rec-label').textContent = 'Done';
                
                // Clean answer (remove trigger words)
                let answer = document.getElementById('answer-data').value;
                answer = answer.replace(/\\b(done|that's all|submit|i am done)\\b/gi, '').trim();
                
                if (!answer) {{
                    answer = "No answer provided";
                }}
                
                // Store in localStorage for Streamlit
                localStorage.setItem('viva_answer', answer);
                localStorage.setItem('viva_submitted', 'true');
                
                // Trigger reload for Streamlit to pick up
                setTimeout(() => {{
                    window.location.reload();
                }}, 500);
            }}
            
            // ===== UTILITIES =====
            function sleep(ms) {{
                return new Promise(resolve => setTimeout(resolve, ms));
            }}
            
            // ===== START INITIALIZATION =====
            initialize();
        </script>
    </body>
    </html>
    """
    
    return html_content


def render_viva_completion_screen(
    student_name: str,
    final_score: float,
    total_questions: int,
    transcript_summary: list
):
    """
    Render the viva completion screen with results
    """
    
    # Determine grade and message
    if final_score >= 80:
        grade = "Excellent"
        grade_color = "#7dd87d"
        message = "Outstanding performance! You demonstrated exceptional understanding."
    elif final_score >= 60:
        grade = "Good"
        grade_color = "#5ac8d8"
        message = "Good job! You showed solid understanding of the concepts."
    elif final_score >= 40:
        grade = "Satisfactory"
        grade_color = "#d4a853"
        message = "Fair attempt. There's room for improvement in some areas."
    else:
        grade = "Needs Improvement"
        grade_color = "#e85d5d"
        message = "More study is recommended. Review the material thoroughly."
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&display=swap');
            
            * {{
                margin: 0; padding: 0; box-sizing: border-box;
                font-family: 'IBM Plex Mono', monospace;
                cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Ccircle cx='12' cy='12' r='4' fill='%23d4a853'/%3E%3Ccircle cx='12' cy='12' r='8' fill='none' stroke='%23d4a853' stroke-width='1' opacity='0.5'/%3E%3C/svg%3E") 12 12, auto;
            }}
            
            body {{ background: #0a0a12; }}
            
            .completion-container {{
                background: linear-gradient(165deg, #0a0a12 0%, #12121a 100%);
                padding: 30px;
                border-radius: 8px;
                border: 1px solid #2a2a3a;
                text-align: center;
                max-width: 500px;
                margin: 0 auto;
            }}
            
            .completion-icon {{
                font-size: 4rem;
                margin-bottom: 20px;
            }}
            
            .completion-title {{
                color: #f5f0dc;
                font-size: 1.5rem;
                font-weight: 700;
                margin-bottom: 10px;
                text-transform: uppercase;
                letter-spacing: 0.1em;
            }}
            
            .student-name {{
                color: #9a9585;
                font-size: 0.9rem;
                margin-bottom: 30px;
            }}
            
            .score-circle {{
                width: 140px;
                height: 140px;
                border-radius: 50%;
                border: 4px solid {grade_color};
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                margin: 0 auto 20px;
                box-shadow: 0 0 30px {grade_color}33;
            }}
            
            .score-value {{
                font-size: 2.5rem;
                font-weight: 700;
                color: {grade_color};
            }}
            
            .score-label {{
                font-size: 0.7rem;
                color: #9a9585;
                text-transform: uppercase;
                letter-spacing: 0.1em;
            }}
            
            .grade-badge {{
                display: inline-block;
                background: #16161f;
                border: 1px solid {grade_color};
                color: {grade_color};
                padding: 8px 20px;
                border-radius: 4px;
                font-size: 0.85rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                margin-bottom: 20px;
            }}
            
            .message {{
                color: #e8e3c8;
                font-size: 0.85rem;
                line-height: 1.6;
                margin-bottom: 30px;
            }}
            
            .closing-message {{
                color: #d4a853;
                font-size: 0.8rem;
                font-style: italic;
                padding: 15px;
                background: #12121a;
                border-radius: 4px;
                border-left: 3px solid #d4a853;
            }}
        </style>
    </head>
    <body>
        <div class="completion-container">
            <div class="completion-icon">🎓</div>
            <div class="completion-title">Viva Complete</div>
            <div class="student-name">{student_name}</div>
            
            <div class="score-circle">
                <div class="score-value">{final_score:.0f}%</div>
                <div class="score-label">Final Score</div>
            </div>
            
            <div class="grade-badge">{grade}</div>
            
            <div class="message">{message}</div>
            
            <div class="closing-message">
                "Thank you, {student_name}. Your viva examination is now complete. You may go."
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content
