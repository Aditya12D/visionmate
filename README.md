# VisionMate 👁️🔊

**VisionMate** is an offline, network-capable AI-powered accessibility assistant that helps visually impaired users read printed text and navigate safely using local, on-device AI models.

By utilizing a local Flask server on a laptop and a mobile phone browser as a wireless camera/output sensor, VisionMate extracts text via OCR, parses obstacles in walking mode, cleans scan errors using a local LLM, and streams natural speech directly back to the browser. 

Following our latest updates, **all speech synthesis is handled entirely in-memory (base64 data streams)**, meaning zero temporary files are written to the disk.

---

## Architecture Flow

All processing is handled over your Local Area Network (LAN) for complete privacy and efficiency:

```
[Mobile Client Browser] ---> (Base64 JPEG Frame via Wi-Fi LAN) ---> [Laptop Server Backend]
         ▲                                                                  │
         │                                                         (PaddleOCR / YOLO Execution)
         │                                                                  ▼
         │                                                         (Qwen 2.5 Correction/LLM)
         │                                                                  ▼
         │                                                         (In-Memory Piper Synthesis)
         │                                                                  │
         └───────── (Audio streams & plays directly from memory) ◄──────────┘
```

---

## Tech Stack

| Component | Technology | Role |
|------------|------------|------|
| **Server Framework** | Flask 3.0.3 & Flask-CORS | Local network distribution & in-memory streaming endpoints |
| **Obstacle/Hazard Detection** | YOLOv11 (`ultralytics`) | Detect obstacles in walking mode |
| **Local OCR** | PaddleOCR 2.9.1 | Local image character recognition |
| **LLM Engine** | Qwen2.5:1.5B (Ollama Client) | Contextual reading correction & formatting shield |
| **TTS Engine** | Piper (Lessac Medium) | In-memory wave generation (`BytesIO`) |
| **Vision Utilities** | OpenCV (`opencv-python`) | Dynamic image matrix decoding |
| **Language Baseline** | Python 3.10 | Core framework coordination |

---

## Project Structure

```
visionmate/
│
├── camera/
│   └── camera.py         # Maintained for upcoming native hardware/Raspberry Pi integration
├── llm/
│   ├── prompts.py        # Strict structured prompt constraints for LLM text formatting
│   └── qwen.py           # Local Ollama client orchestration layer
├── modes/
│   ├── reading.py        # Reading mode text cleanup flow
│   └── walking.py        # Object & collision warning processing
├── ocr/
│   └── paddle.py         # PaddleOCR framework wrapper
├── detector/
│   └── yolo.py           # YOLO detector implementation for walking mode
├── tts/
│   └── piper.py          # Piper TTS engine wrapper supporting in-memory BytesIO generation
├── static/               # Contains static output assets (no persistent WAV logs)
├── models/               # Model weights storage directory (YOLO & Piper folders)
│
├── .gitignore            # Ignores byte caches, IDE configs, virtual environments and WAV files
├── requirements.txt      # Cleaned and grouped dependency tree requirements
├── config.py             # Shared global pipeline configurations (model paths, thresholds)
└── server.py             # Flask application server and real-time processing endpoints
```

---

## Onboarding Guide: Setup & Running From Scratch

Follow these steps to run the complete project on your local machine:

### 1. Prerequisites
- **Python 3.10** is required to guarantee PaddlePaddle and NumPy stability.
- **Ollama** installed on your system (get it from [ollama.com](https://ollama.com)).
- Both the server laptop and mobile test device must be on the **same Wi-Fi network**.

### 2. Clone the Repository & Setup Environment
Open your terminal (PowerShell on Windows, bash on Linux/Mac):

```bash
# Clone the repository
git clone https://github.com/Aditya12D/visionmate.git
cd visionmate

# Create a Python 3.10 virtual environment
python -m venv venv310

# Activate the virtual environment
# Windows Powershell:
.\venv310\Scripts\Activate.ps1
# Windows CMD:
.\venv310\Scripts\activate.bat
# Linux/Mac:
source venv310/bin/activate

# Install all required package dependencies
pip install -r requirements.txt
```

### 3. Download AI Model Dependencies

#### A. Ollama (LLM) Server
Start the Ollama server to accept external requests on your local network (e.g. from the Flask server run loop) and pull the required model:

1. Launch Ollama listening on all interfaces (`0.0.0.0`):
   - **Windows PowerShell**:
     ```powershell
     $env:OLLAMA_HOST="0.0.0.0"
     ollama serve
     ```
   - **Linux/Mac**:
     ```bash
     OLLAMA_HOST=0.0.0.0 ollama serve
     ```
2. In *another* terminal tab, download the Qwen model:
   ```bash
   ollama pull qwen2.5:1.5b
   ```

#### B. Piper (TTS) voice models
Download the voice models directly into the `models` directory:

```bash
# Ensure huggingface-cli is ready
pip install -U "huggingface_hub[cli]"

# Download rhasspy medium voices
huggingface-cli download rhasspy/piper-voices --include "en/en_US/lessac/medium/*" --local-dir models
```

---

## Running the Complete Project

1. With your virtual environment activated, run the web application server:
   ```bash
   python server.py
   ```
2. Locate your server laptop's Local IP Address (displayed on server boot, or find via `ipconfig` on Windows or `hostname -I` on Linux).
3. Connect your mobile phone browser to the **same Wi-Fi network** and navigate to:
   ```text
   http://<YOUR_LAPTOP_IP>:5000
   ```
   *(For example: `http://192.168.1.15:5000`)*

> 💡 **Camera Access on Insecure HTTP (Mobile Browsers):**
> Because local connections run over unencrypted `http://`, mobile browsers restrict camera access.
> - **Android Chrome:** Navigate to `chrome://flags`, search for `#unsafely-treat-insecure-origin-as-secure`, set it to **Enabled**, add your server URL (e.g., `http://192.168.1.15:5000`), and tap **Relaunch**.
> - **iOS Safari:** iOS devices normally require HTTPS. You may configure a self-signed local SSL certificate or forward the port using a tunnel service like Ngrok for secure development testing.

## License

Distributed under the MIT License. See `LICENSE` for more information.

---

## Acknowledgements

- **PaddleOCR** — High performance local text identification engines.
- **Ollama & Qwen Team** — Fast, highly efficient open model parameters for offline systems.
- **Rhasspy Piper Project** — Incredibly fast, natural localized text-to-speech engine architectures.
