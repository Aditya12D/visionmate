import cv2
import os
import base64
import numpy as np

from modes.walking import WalkingMode
from flask import Flask,request, jsonify,send_file,render_template_string
from flask_cors import CORS
from ocr.paddle import OCR
from tts.piper import PiperTTS
from modes.reading import process
app=Flask(__name__)
CORS(app)

print("Warming up Visionmate ai core modules")
ocr=OCR()
walking_engine=WalkingMode()
tts=PiperTTS()

AUDIO_OUTPUT_PATH="static/output.wav"
os.makedirs("static",exist_ok=True)


@app.route('/')
def index():
    return render_template_string(HTML_INTERFACE)


@app.route('/api/reading-mode',methods=['POST'])
def handle_reading_mode():
    try:
        data=request.json['image']
        _, encoded=data.split(",",1)
        img_bytes=base64.b64decode(encoded)
        nparr=np.frombuffer(img_bytes,np.uint8)
        frame=cv2.imdecode(nparr,cv2.IMREAD_COLOR)

        raw_text=ocr.read(frame)
        if not raw_text.strip():
            return jsonify({
                "text":"No text detected.",
                "audio_available":False
            })
        
        cleaned_text=process(raw_text)

        tts.save_to_file(cleaned_text,AUDIO_OUTPUT_PATH)
        return jsonify({
            "text":cleaned_text,
            "audio_available":True
        })

    except Exception as e:
        return jsonify ({
            "error":str(e)
        }),500


@app.route('/api/walking-mode',methods=["POST"])
def handle_walking_mode():
    try:
        data = request.json['image']
        _, encoded = data.split(",", 1)
        img_bytes = base64.b64decode(encoded)
        
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        spatial_matrix=walking_engine.process(frame)
        alert_phrase=walking_engine.generate_alert_text(spatial_matrix)

        if alert_phrase=="NEEDS_SCENERY_DESCRIPTION":
            alert_phrase="Caution. Open space ahead"
        
        tts.save_to_file(alert_phrase,AUDIO_OUTPUT_PATH)
        return jsonify({
            "text":alert_phrase,
            "audio_available":True
        })

    except Exception as e:
        return jsonify({
            "error":str(e)
        }),500
    

@app.route("/get_audio")
def get_audio():
    try:
        if os.path.exists(AUDIO_OUTPUT_PATH):
            with open(AUDIO_OUTPUT_PATH, 'rb') as f:
                data = f.read()
            try:
                os.remove(AUDIO_OUTPUT_PATH)
            except Exception as e:
                print(f"Error removing temporary audio file: {e}")
            from io import BytesIO
            return send_file(
                BytesIO(data),
                mimetype="audio/wav"
            )
        return jsonify({"error": "Audio file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


HTML_INTERFACE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VisionMate AI Dashboard</title>
    <style>
        body { font-family: system-ui, sans-serif; text-align: center; background: #0f0f12; color: #e4e4e7; margin: 0; padding: 20px; }
        .container { max-width: 450px; margin: 0 auto; }
        #video { width: 100%; border-radius: 12px; background: #18181b; border: 2px solid #27272a; }
        .mode-container { display: flex; gap: 10px; margin: 15px 0; }
        .mode-btn { flex: 1; padding: 12px; font-weight: bold; background: #27272a; color: #a1a1aa; border: 2px solid transparent; border-radius: 8px; cursor: pointer; }
        .mode-btn.active { background: #1e1b4b; color: #818cf8; border-color: #4f46e5; }
        
        .btn-base { width: 100%; padding: 18px; font-size: 1.2rem; color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; transition: background 0.2s; }
        #actionBtn { background: #2563eb; }
        #actionBtn.streaming { background: #ea580c; }
        #stopBtn { padding: 12px; margin-top: 10px; background: #dc2626; }
        
        #status { font-size: 1rem; color: #3b82f6; font-weight: bold; margin: 15px 0; min-height: 24px; }
        .log-box { padding: 15px; background: #18181b; border-radius: 8px; text-align: left; border: 1px solid #27272a; min-height: 50px; font-family: monospace; }
    </style>
</head>
<body>
    <div class="container">
        <h2>VisionMate Framework</h2>
        <video id="video" autoplay playsinline muted></video>
        
        <div class="mode-container">
            <button id="btn-reading" class="mode-btn active" onclick="setMode('reading')">📖 READING MODE</button>
            <button id="btn-walking" class="mode-btn" onclick="setMode('walking')">🚶 WALKING MODE</button>
        </div>

        <button id="actionBtn" class="btn-base" onclick="toggleStreamState()">⚡ START LIVE PIPELINE</button>
        <button id="stopBtn" class="btn-base" onclick="emergencyStopAll()">🛑 EMERGENCY STOP</button>
        
        <div id="status">Ready</div>
        <div class="log-box" id="logBox">System initialized. Awaiting trigger.</div>
    </div>

    <audio id="audioPlayer" style="display:none;"></audio>
    <canvas id="canvas" style="display:none;"></canvas>

    <script>
        const video = document.getElementById('video');
        const canvas = document.getElementById('canvas');
        const statusDiv = document.getElementById('status');
        const logBox = document.getElementById('logBox');
        const audioPlayer = document.getElementById('audioPlayer');
        const actionBtn = document.getElementById('actionBtn');
        
        let currentMode = 'reading';
        let isLiveActive = false; // Main switch state
        let nextFrameTimeoutId = null; 

        navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" }, audio: false })
            .then(stream => { video.srcObject = stream; })
            .catch(err => { statusDiv.innerText = "Camera Missing/Denied"; });

        function setMode(mode) {
            currentMode = mode;
            document.getElementById('btn-reading').classList.toggle('active', mode === 'reading');
            document.getElementById('btn-walking').classList.toggle('active', mode === 'walking');
            logBox.innerText = `Switched to ${mode.toUpperCase()} mode.`;
            if (isLiveActive) stopReactivePipeline();
        }

        function toggleStreamState() {
            if (isLiveActive) {
                stopReactivePipeline();
            } else {
                isLiveActive = true;
                actionBtn.innerText = "⏸️ PAUSE LIVE STREAM";
                actionBtn.classList.add('streaming');
                // Kick off the very first reactive execution chain link
                executeReactiveCycle();
            }
        }

        function stopReactivePipeline() {
            isLiveActive = false;
            if (nextFrameTimeoutId) clearTimeout(nextFrameTimeoutId);
            actionBtn.innerText = "⚡ START LIVE PIPELINE";
            actionBtn.classList.remove('streaming');
            statusDiv.innerText = "Stream paused.";
        }

        function executeReactiveCycle() {
            // Check if the user paused the system mid-execution
            if (!isLiveActive) return; 

            statusDiv.innerText = "Capturing framework matrix...";
            
            const context = canvas.getContext('2d');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            
            const dataUrl = canvas.toDataURL('image/jpeg', 0.6); 
            const targetEndpoint = currentMode === 'reading' ? '/api/reading-mode' : '/api/walking-mode';

            fetch(targetEndpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image: dataUrl })
            })
            .then(res => res.json())
            .then(data => {
                if (!isLiveActive) return; // Guard clause if turned off mid-request
                
                if(data.error) {
                    logBox.innerText = "Pipeline exception: " + data.error;
                    // Try recovering by attempting a retry after 3 seconds
                    nextFrameTimeoutId = setTimeout(executeReactiveCycle, 3000);
                    return;
                }
                
                logBox.innerText = data.text;
                statusDiv.innerText = "Speaking alert...";
                
                // Point to the newly rendered Piper file
                audioPlayer.src = "/get_audio?v=" + new Date().getTime();
                audioPlayer.play().catch(e => {
                    console.log("Audio play blocked by browser window security policies.");
                    // Safe fallback: If audio player fails, force the loop forward anyway
                    scheduleNextFrame(1500);
                });
            })
            .catch(err => {
                if (!isLiveActive) return;
                statusDiv.innerText = "Connection dropped. Retrying...";
                nextFrameTimeoutId = setTimeout(executeReactiveCycle, 3000);
            });
        }

        // --- THE DYNAMIC EVENT EVENT TRIGGER ---
        // Tells the hardware: The absolute second you finish speaking, wait a beat, then run again!
        audioPlayer.onended = () => {
            if (!isLiveActive) return;
            // Introduce a short, natural breathing window of silence before taking the next photo
            // 1500ms (1.5 seconds) gives the user a beat to register the audio environment
            scheduleNextFrame(1500);
        };

        function scheduleNextFrame(delayMs) {
            statusDiv.innerText = "Awaiting natural pause window...";
            nextFrameTimeoutId = setTimeout(executeReactiveCycle, delayMs);
        }

        function emergencyStopAll() {
            stopReactivePipeline();
            audioPlayer.pause();
            audioPlayer.currentTime = 0;
            statusDiv.innerText = "System halted.";
            logBox.innerText = "All loops cleanly detached.";
        }
    </script>
</body>
</html>
"""

if __name__=='__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)