"""
Video Call Interface - Google Meet Style
Real-time AI Viva Examination
"""
import streamlit as st
import streamlit.components.v1 as components
import time


def render_video_call_interface(ai_avatar_base64: str, question_text: str, question_audio_b64: str = None):
    """
    Render a Google Meet-style video call interface
    
    Args:
        ai_avatar_base64: Base64 encoded AI avatar image
        question_text: Current question to display
        question_audio_b64: Base64 encoded question audio (optional)
    """
    
    video_call_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            
            .video-call-container {{
                display: flex;
                gap: 20px;
                height: 500px;
                background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 100%);
                border-radius: 20px;
                padding: 20px;
                position: relative;
            }}
            
            .video-panel {{
                flex: 1;
                background: #1e1e3f;
                border-radius: 15px;
                overflow: hidden;
                position: relative;
                box-shadow: 0 10px 40px rgba(0,0,0,0.5);
            }}
            
            .ai-panel {{
                background: linear-gradient(180deg, #1e3a5f 0%, #0f2027 100%);
            }}
            
            .student-panel {{
                background: #000;
            }}
            
            .panel-label {{
                position: absolute;
                bottom: 15px;
                left: 15px;
                background: rgba(0,0,0,0.7);
                color: white;
                padding: 8px 16px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                z-index: 10;
            }}
            
            .ai-avatar {{
                width: 100%;
                height: 100%;
                object-fit: cover;
            }}
            
            .ai-speaking-indicator {{
                position: absolute;
                bottom: 80px;
                left: 50%;
                transform: translateX(-50%);
                display: flex;
                gap: 5px;
            }}
            
            .speaking-bar {{
                width: 6px;
                height: 30px;
                background: #22c55e;
                border-radius: 3px;
                animation: speaking 0.5s ease-in-out infinite;
            }}
            
            .speaking-bar:nth-child(2) {{ animation-delay: 0.1s; }}
            .speaking-bar:nth-child(3) {{ animation-delay: 0.2s; }}
            .speaking-bar:nth-child(4) {{ animation-delay: 0.3s; }}
            .speaking-bar:nth-child(5) {{ animation-delay: 0.4s; }}
            
            @keyframes speaking {{
                0%, 100% {{ height: 10px; }}
                50% {{ height: 30px; }}
            }}
            
            #student-video {{
                width: 100%;
                height: 100%;
                object-fit: cover;
                transform: scaleX(-1);
            }}
            
            .question-overlay {{
                position: absolute;
                top: 15px;
                left: 15px;
                right: 15px;
                background: rgba(30, 41, 59, 0.95);
                padding: 15px 20px;
                border-radius: 12px;
                border-left: 4px solid #3b82f6;
            }}
            
            .question-text {{
                color: #ffffff;
                font-size: 14px;
                line-height: 1.5;
            }}
            
            .controls-bar {{
                display: flex;
                justify-content: center;
                gap: 15px;
                margin-top: 20px;
            }}
            
            .control-btn {{
                width: 60px;
                height: 60px;
                border-radius: 50%;
                border: none;
                cursor: pointer;
                font-size: 24px;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            
            .mic-btn {{
                background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
                color: white;
            }}
            
            .mic-btn.recording {{
                background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
                animation: pulse-red 1s infinite;
            }}
            
            @keyframes pulse-red {{
                0%, 100% {{ box-shadow: 0 0 0 0 rgba(239,68,68,0.7); }}
                50% {{ box-shadow: 0 0 0 15px rgba(239,68,68,0); }}
            }}
            
            .end-btn {{
                background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
                color: white;
            }}
            
            .control-btn:hover {{
                transform: scale(1.1);
            }}
            
            .transcript-box {{
                background: rgba(30, 41, 59, 0.95);
                padding: 15px;
                border-radius: 12px;
                margin-top: 15px;
                min-height: 80px;
            }}
            
            .transcript-label {{
                color: #60a5fa;
                font-size: 12px;
                margin-bottom: 8px;
            }}
            
            .transcript-text {{
                color: #ffffff;
                font-size: 16px;
                min-height: 40px;
            }}
            
            .status-indicator {{
                position: absolute;
                top: 15px;
                right: 15px;
                display: flex;
                align-items: center;
                gap: 8px;
                background: rgba(0,0,0,0.7);
                padding: 8px 15px;
                border-radius: 20px;
            }}
            
            .status-dot {{
                width: 10px;
                height: 10px;
                border-radius: 50%;
                background: #22c55e;
                animation: blink 2s infinite;
            }}
            
            @keyframes blink {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.5; }}
            }}
            
            .status-text {{
                color: white;
                font-size: 12px;
            }}
            
            .movement-warning {{
                display: none;
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: rgba(239, 68, 68, 0.9);
                color: white;
                padding: 20px 30px;
                border-radius: 12px;
                font-weight: bold;
                z-index: 100;
            }}
        </style>
    </head>
    <body>
        <div class="video-call-container">
            <!-- AI Panel -->
            <div class="video-panel ai-panel">
                <img src="data:image/png;base64,{ai_avatar_base64}" class="ai-avatar" alt="AI Examiner">
                
                <div class="question-overlay">
                    <div class="question-text">{question_text}</div>
                </div>
                
                <div class="ai-speaking-indicator" id="ai-speaking">
                    <div class="speaking-bar"></div>
                    <div class="speaking-bar"></div>
                    <div class="speaking-bar"></div>
                    <div class="speaking-bar"></div>
                    <div class="speaking-bar"></div>
                </div>
                
                <div class="panel-label">🤖 AI Examiner</div>
            </div>
            
            <!-- Student Panel -->
            <div class="video-panel student-panel">
                <video id="student-video" autoplay playsinline muted></video>
                
                <div class="status-indicator">
                    <div class="status-dot" id="status-dot"></div>
                    <span class="status-text" id="status-text">Connecting...</span>
                </div>
                
                <div class="movement-warning" id="movement-warning">
                    ⚠️ Please stay still!
                </div>
                
                <div class="panel-label">📹 You</div>
            </div>
        </div>
        
        <!-- Controls -->
        <div class="controls-bar">
            <button class="control-btn mic-btn" id="mic-btn" onclick="toggleMic()">🎤</button>
            <button class="control-btn end-btn" onclick="endCall()">📞</button>
        </div>
        
        <!-- Transcript -->
        <div class="transcript-box">
            <div class="transcript-label">📝 Your Answer (Live Transcription)</div>
            <div class="transcript-text" id="transcript">Click the microphone button and speak your answer...</div>
        </div>
        
        <input type="hidden" id="final-transcript" value="">
        
        <script>
            let isRecording = false;
            let recognition = null;
            let previousFrame = null;
            let movementCount = 0;
            
            // Initialize camera
            async function initCamera() {{
                try {{
                    const stream = await navigator.mediaDevices.getUserMedia({{
                        video: {{ facingMode: 'user', width: 640, height: 480 }},
                        audio: false
                    }});
                    document.getElementById('student-video').srcObject = stream;
                    document.getElementById('status-dot').style.background = '#22c55e';
                    document.getElementById('status-text').textContent = 'Camera Active';
                    
                    // Start movement detection
                    startMovementDetection(stream);
                }} catch (err) {{
                    console.error('Camera error:', err);
                    document.getElementById('status-dot').style.background = '#ef4444';
                    document.getElementById('status-text').textContent = 'Camera Error';
                }}
            }}
            
            // Movement detection using canvas
            function startMovementDetection(stream) {{
                const video = document.getElementById('student-video');
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                canvas.width = 160;
                canvas.height = 120;
                
                setInterval(() => {{
                    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                    const currentFrame = ctx.getImageData(0, 0, canvas.width, canvas.height);
                    
                    if (previousFrame) {{
                        let diff = 0;
                        for (let i = 0; i < currentFrame.data.length; i += 4) {{
                            diff += Math.abs(currentFrame.data[i] - previousFrame.data[i]);
                        }}
                        diff /= (canvas.width * canvas.height);
                        
                        if (diff > 15) {{
                            movementCount++;
                            if (movementCount > 3) {{
                                showMovementWarning();
                            }}
                        }} else {{
                            movementCount = Math.max(0, movementCount - 1);
                        }}
                    }}
                    previousFrame = currentFrame;
                }}, 500);
            }}
            
            function showMovementWarning() {{
                const warning = document.getElementById('movement-warning');
                warning.style.display = 'block';
                setTimeout(() => {{
                    warning.style.display = 'none';
                }}, 2000);
            }}
            
            // Speech recognition
            function initSpeechRecognition() {{
                if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
                    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                    recognition = new SpeechRecognition();
                    recognition.continuous = true;
                    recognition.interimResults = true;
                    recognition.lang = 'en-US';
                    
                    recognition.onresult = (event) => {{
                        let finalTranscript = '';
                        let interimTranscript = '';
                        
                        for (let i = event.resultIndex; i < event.results.length; i++) {{
                            if (event.results[i].isFinal) {{
                                finalTranscript += event.results[i][0].transcript;
                            }} else {{
                                interimTranscript += event.results[i][0].transcript;
                            }}
                        }}
                        
                        const transcript = finalTranscript || interimTranscript;
                        document.getElementById('transcript').textContent = transcript || 'Listening...';
                        document.getElementById('final-transcript').value = transcript;
                        
                        // Send to Streamlit
                        if (finalTranscript) {{
                            window.parent.postMessage({{
                                type: 'transcript',
                                text: finalTranscript
                            }}, '*');
                        }}
                    }};
                    
                    recognition.onerror = (event) => {{
                        console.error('Speech error:', event.error);
                        document.getElementById('transcript').textContent = 'Speech error: ' + event.error;
                    }};
                }}
            }}
            
            function toggleMic() {{
                const btn = document.getElementById('mic-btn');
                
                if (!isRecording) {{
                    if (recognition) {{
                        recognition.start();
                        isRecording = true;
                        btn.classList.add('recording');
                        btn.textContent = '🔴';
                        document.getElementById('transcript').textContent = 'Listening...';
                    }}
                }} else {{
                    if (recognition) {{
                        recognition.stop();
                        isRecording = false;
                        btn.classList.remove('recording');
                        btn.textContent = '🎤';
                        
                        // Submit the transcript
                        const text = document.getElementById('final-transcript').value;
                        if (text) {{
                            window.parent.postMessage({{
                                type: 'submit_answer',
                                text: text
                            }}, '*');
                        }}
                    }}
                }}
            }}
            
            function endCall() {{
                window.parent.postMessage({{ type: 'end_call' }}, '*');
            }}
            
            // Auto-play AI speaking animation
            function playAISpeaking() {{
                const indicator = document.getElementById('ai-speaking');
                indicator.style.display = 'flex';
                setTimeout(() => {{
                    indicator.style.display = 'none';
                }}, 5000);
            }}
            
            // Initialize
            initCamera();
            initSpeechRecognition();
            playAISpeaking();
        </script>
    </body>
    </html>
    """
    
    return video_call_html


def render_meet_interface(ai_base64: str, question: str, q_idx: int, total_q: int):
    """Render the complete Meet-style interface in Streamlit"""
    
    # Header
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 15px 25px;
        border-radius: 15px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    ">
        <div style="color: #ffffff; font-size: 20px; font-weight: bold;">
            🎓 AI Viva Examination
        </div>
        <div style="color: #60a5fa; font-size: 16px;">
            Question {q_idx + 1} of {total_q}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Video call interface
    html_content = render_video_call_interface(ai_base64, question)
    components.html(html_content, height=750, scrolling=False)
    
    return html_content
