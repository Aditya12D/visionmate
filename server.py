import os
import base64
import numpy as np
import cv2
from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS

from ocr.paddle import OCR
from modes.reading import process
from tts.piper import PiperTTS

app = Flask(__name__)
CORS(app)  # Allows cross-origin requests from mobile devices

# Initialize core intelligence engines on laptop memory
print("Warming up VisionMate AI Core on Laptop...")
ocr = OCR()
tts = PiperTTS()

# Temporary audio path to store the spoken phrase
AUDIO_OUTPUT_PATH = "static/output.wav"
os.makedirs("static", exist_ok=True)

HTML_INTERFACE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VisionMate Client</title>
    <style>
        body { font-family: sans-serif; text-align: center; background: #121212; color: white; margin: 0; padding: 20px; }
        #video { width: 100%; max-width: 400px; border-radius: 10px; background: #222; transform: scaleX(1); }
        button { width: 85%; padding: 18px; font-size: 1.2rem; background: #28a745; color: white; border: none; border-radius: 8px; margin: 15px 0; font-weight: bold; }
        button:active { background: #218838; }
        #stopBtn { background: #dc3545; }
        #stopBtn:active { background: #c82333; }
        #status { font-size: 1.1rem; color: #007bff; font-weight: bold; margin: 10px 0; }
        #output-text { padding: 10px; background: #222; margin-top: 10px; border-radius: 5px; font-size: 0.9rem; text-align: left; max-height: 100px; overflow-y: auto;}
    </style>
</head>
<body>
    <h1>VisionMate Mobile</h1>
    
    <video id="video" autoplay playsinline muted></video>
    
    <br>
    <button id="scanBtn" onclick="captureAndProcess()">⚡ SCAN & READ</button>
    <button id="stopBtn" onclick="stopAudio()">🛑 STOP AUDIO</button>
    
    <div id="status">Ready</div>
    <h3>Processed Text:</h3>
    <div id="output-text" id="textLog">No text scanned yet.</div>

    <audio id="audioPlayer" style="display:none;"></audio>

    <canvas id="canvas" style="display:none;"></canvas>

    <script>
        const video = document.getElementById('video');
        const canvas = document.getElementById('canvas');
        const statusDiv = document.getElementById('status');
        const textLog = document.getElementById('output-text');
        const audioPlayer = document.getElementById('audioPlayer');

        // Request Access to Back Facing Camera of Phone
        navigator.mediaDevices.getUserMedia({ 
            video: { facingMode: "environment" }, 
            audio: false 
        })
        .then(stream => { video.srcObject = stream; })
        .catch(err => { 
            statusDiv.innerText = "Camera Access Denied";
            console.error(err);
        });

        function captureAndProcess() {
            statusDiv.innerText = "Capturing frame...";
            
            // Draw current video frame to hidden canvas to extract image
            const context = canvas.getContext('2d');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            
            // Convert frame to Base64 JPEG string
            const dataUrl = canvas.toDataURL('image/jpeg');
            
            statusDiv.innerText = "Laptop processing AI pipeline...";
            
            fetch('/process_mobile', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image: dataUrl })
            })
            .then(res => res.json())
            .then(data => {
                if(data.error) {
                    statusDiv.innerText = "Error: " + data.error;
                    return;
                }
                
                textLog.innerText = data.text;
                statusDiv.innerText = "Streaming Audio Output...";
                
                // Force mobile browser to fetch and play synthesized file with timestamp cache-buster
                audioPlayer.src = "/get_audio?v=" + new Date().getTime();
                audioPlayer.play();
                audioPlayer.onended = () => { statusDiv.innerText = "Ready"; };
            })
            .catch(err => {
                statusDiv.innerText = "Server Error.";
                console.error(err);
            });
        }

        function stopAudio() {
            audioPlayer.pause();
            audioPlayer.currentTime = 0;
            statusDiv.innerText = "Audio Stopped.";
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_INTERFACE)

@app.route('/process_mobile', methods=['POST'])
def process_mobile():
    try:
        data = request.json['image']
        # Strip metadata header from base64 string
        header, encoded = data.split(",", 1)
        img_data = base64.b64decode(encoded)
        
        # Reconstruct base64 back into an OpenCV image frame array natively
        nparr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # 1. Run Laptop OCR
        text = ocr.read(frame)
        if not text.strip():
            return jsonify({"text": "No text detected in camera frame.", "audio_available": False})

        # 2. Run Laptop LLM Post-Correction
        cleaned_text = process(text)
        print(f"\n[AI Pipeline Output]: {cleaned_text}")

        # 3. Generate Audio File on Laptop
        # NOTE: Modify your Piper wrapper if necessary so it writes to disk instead of using hardware audio lines.
        # Example target behavior: tts.synthesize_to_file(cleaned_text, AUDIO_OUTPUT_PATH)
        if hasattr(tts, 'save_to_file'):
            tts.save_to_file(cleaned_text, AUDIO_OUTPUT_PATH)
        else:
            # Fallback if your class only has .speak(): change piper internally to write output.wav
            tts.speak(cleaned_text) 

        return jsonify({"text": cleaned_text, "audio_available": True})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_audio')
def get_audio():
    # Serves the generated wav file directly down to the mobile phone speaker system
    return send_file(AUDIO_OUTPUT_PATH, mimetype="audio/wav")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)