"""
Browser-based Camera and Microphone Component
Uses JavaScript getUserMedia API - no Python dependencies required
"""
import streamlit as st
import streamlit.components.v1 as components


def render_camera_feed():
    """Render a live camera feed using JavaScript getUserMedia"""
    camera_html = """
    <div id="camera-container" style="
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    ">
        <video id="camera-feed" autoplay playsinline muted style="
            width: 100%;
            max-width: 400px;
            border-radius: 10px;
            border: 3px solid #4ade80;
            background: #000;
        "></video>
        <div id="camera-status" style="
            color: #4ade80;
            margin-top: 10px;
            font-family: 'Segoe UI', sans-serif;
            font-weight: bold;
        ">Initializing Camera...</div>
    </div>
    
    <script>
        async function initCamera() {
            const video = document.getElementById('camera-feed');
            const status = document.getElementById('camera-status');
            
            try {
                const stream = await navigator.mediaDevices.getUserMedia({
                    video: { facingMode: 'user', width: 640, height: 480 },
                    audio: false
                });
                video.srcObject = stream;
                status.textContent = '🟢 Camera Active';
                status.style.color = '#4ade80';
            } catch (err) {
                console.error('Camera error:', err);
                status.textContent = '🔴 Camera Access Denied: ' + err.message;
                status.style.color = '#ef4444';
            }
        }
        
        // Initialize on load
        initCamera();
    </script>
    """
    components.html(camera_html, height=400)


def render_microphone_recorder():
    """Render a microphone recorder using JavaScript Web Audio API"""
    mic_html = """
    <div id="mic-container" style="
        background: linear-gradient(135deg, #1e3a5f 0%, #0f2027 100%);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin-top: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    ">
        <div id="mic-status" style="
            color: #60a5fa;
            font-family: 'Segoe UI', sans-serif;
            font-weight: bold;
            margin-bottom: 15px;
        ">🎤 Microphone Ready</div>
        
        <button id="speak-btn" onclick="startRecording()" style="
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 18px;
            font-weight: bold;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 5px 20px rgba(59,130,246,0.4);
        ">🎙️ Speak Now</button>
        
        <button id="stop-btn" onclick="stopRecording()" style="
            background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 18px;
            font-weight: bold;
            border-radius: 50px;
            cursor: pointer;
            margin-left: 10px;
            display: none;
            transition: all 0.3s ease;
            box-shadow: 0 5px 20px rgba(239,68,68,0.4);
        ">⏹️ Stop</button>
        
        <div id="recording-indicator" style="
            margin-top: 15px;
            display: none;
        ">
            <div style="
                width: 20px;
                height: 20px;
                background: #ef4444;
                border-radius: 50%;
                display: inline-block;
                animation: pulse 1s infinite;
            "></div>
            <span style="color: #ef4444; margin-left: 10px;">Recording...</span>
        </div>
        
        <audio id="audio-playback" controls style="
            margin-top: 15px;
            display: none;
            width: 100%;
        "></audio>
    </div>
    
    <style>
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(1.2); }
        }
        #speak-btn:hover { transform: scale(1.05); }
        #stop-btn:hover { transform: scale(1.05); }
    </style>
    
    <script>
        let mediaRecorder;
        let audioChunks = [];
        
        async function initMicrophone() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                
                mediaRecorder.ondataavailable = (event) => {
                    audioChunks.push(event.data);
                };
                
                mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                    const audioUrl = URL.createObjectURL(audioBlob);
                    const audioPlayer = document.getElementById('audio-playback');
                    audioPlayer.src = audioUrl;
                    audioPlayer.style.display = 'block';
                    
                    // Store for potential upload
                    window.lastRecordedAudio = audioBlob;
                };
                
                document.getElementById('mic-status').textContent = '🟢 Microphone Ready';
                document.getElementById('mic-status').style.color = '#4ade80';
                document.getElementById('speak-btn').disabled = false;
                
            } catch (err) {
                console.error('Microphone error:', err);
                document.getElementById('mic-status').textContent = '🔴 Microphone Denied: ' + err.message;
                document.getElementById('mic-status').style.color = '#ef4444';
                document.getElementById('speak-btn').disabled = true;
            }
        }
        
        function startRecording() {
            audioChunks = [];
            mediaRecorder.start();
            document.getElementById('speak-btn').style.display = 'none';
            document.getElementById('stop-btn').style.display = 'inline-block';
            document.getElementById('recording-indicator').style.display = 'block';
            document.getElementById('audio-playback').style.display = 'none';
        }
        
        function stopRecording() {
            mediaRecorder.stop();
            document.getElementById('speak-btn').style.display = 'inline-block';
            document.getElementById('stop-btn').style.display = 'none';
            document.getElementById('recording-indicator').style.display = 'none';
        }
        
        // Initialize on load
        initMicrophone();
    </script>
    """
    components.html(mic_html, height=300)


def render_live_proctoring():
    """Render combined camera and microphone interface"""
    st.markdown("### 📹 Live Proctoring")
    render_camera_feed()
    render_microphone_recorder()
