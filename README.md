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
├── models/               # Model weights (YOLO .pt & Piper voice) — downloaded at setup, not committed
├── certs/                # Self-signed TLS certificate for HTTPS — generated at setup, not committed
│
├── ARCHITECTURE.md       # System diagram, pipeline, data flow, and design decisions
├── TECHNICAL_REPORT.md   # Measured specs, local-AI verification, and evaluation
├── .gitignore            # Ignores byte caches, IDE configs, virtual environments and WAV files
├── requirements.txt      # Cleaned and grouped dependency tree requirements
├── config.py             # Shared global pipeline configurations (model paths, thresholds)
└── server.py             # Flask app: endpoints, embedded web UI, and HTTPS serving
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

### C. HTTPS certificate (required for the phone camera)

Mobile browsers only allow camera access (`getUserMedia`) on **secure origins**, so the server runs over HTTPS with a self-signed certificate. Generate one into the `certs/` folder (replace `192.168.1.15` with your laptop's local IP):

```bash
mkdir -p certs
openssl req -x509 -newkey rsa:2048 -keyout certs/key.pem -out certs/cert.pem \
  -days 365 -nodes -subj "/CN=192.168.1.15" \
  -addext "subjectAltName=IP:192.168.1.15,IP:127.0.0.1,DNS:localhost"
```

`server.py` picks up `certs/cert.pem` and `certs/key.pem` automatically.

---

## Running the Complete Project

1. With your virtual environment activated, run the web application server:
   ```bash
   python server.py
   ```
2. Locate your server laptop's Local IP Address (displayed on server boot, or find via `ipconfig` on Windows, `hostname -I` on Linux, or `ipconfig getifaddr en0` on macOS).
3. Connect your mobile phone browser to the **same Wi-Fi network** and navigate to:
   ```text
   https://<YOUR_LAPTOP_IP>:5001
   ```
   *(For example: `https://192.168.1.15:5001` — note **https** and port **5001**)*
4. Your browser will warn that the connection is not private — that's expected with a self-signed certificate. Tap **Advanced / Show Details → Proceed / Visit Website** (needed once per device), then **Allow** camera access when prompted.

> 💡 **Why port 5001?** On modern macOS, the AirPlay Receiver service occupies port 5000, so VisionMate serves on 5001. If you change it, update the port in `server.py`.
>
> 💡 **No sound on iPhone?** Check the ring/silent switch and volume. The app already unlocks audio playback on the **Start** tap to satisfy iOS autoplay rules.

## Privacy and Safety

### Data handling
- **Camera frames are processed entirely in RAM** — decoded, analyzed, and discarded. No image, extracted text, or generated audio is ever written to disk or any log.
- **Nothing leaves your local network.** Frames travel phone → laptop over your own Wi-Fi (HTTPS); all AI inference happens on the laptop; the LLM runs against `127.0.0.1` only. There is no cloud API, no telemetry, and no analytics in the application. Internet is required only once, to download the models at install time.
- **No accounts, no identifiers** — the app stores no user data at all.

### Permissions
- **Phone:** camera access only (requested by the browser). No microphone, no location, no storage.
- **Laptop:** the server binds to the local network so your phone can reach it — use it on a trusted home/private Wi-Fi network.

### Storage
- The only files on disk are the AI model weights themselves. Zero user-generated content is persisted (the `.gitignore` also excludes WAV artifacts from older versions).

### Limitations and risks — please read
- VisionMate is a **prototype assistive aid, not a certified medical or mobility device.** It must **complement — never replace — a white cane, guide dog, or human assistance.**
- Obstacle detection covers the 80 COCO object classes: **stairs, curbs, potholes, and glass doors are NOT detected.**
- Distance is estimated from object size in frame, not true depth sensing, and the scene is sampled once per spoken cycle (every few seconds) — fast-moving hazards can be missed.
- OCR and speech are English-only in this build; accuracy degrades in low light and with handwriting.
- The text-correction LLM is constrained by prompt to never answer or execute instructions found in scanned documents (prompt-injection mitigation), but as with any LLM this cannot be absolutely guaranteed.

---

## Attribution

VisionMate builds on outstanding open-source work:

| Component | Project / Authors | License |
|---|---|---|
| OCR | [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) (PP-OCRv3/v4 English mobile models) — PaddlePaddle team | Apache-2.0 |
| LLM | [Qwen 2.5 1.5B Instruct](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct) — Alibaba Qwen team | Apache-2.0 |
| LLM runtime | [Ollama](https://ollama.com) (llama.cpp backend, Q4_K_M quantization) | MIT |
| Object detection | [YOLOv11n](https://github.com/ultralytics/ultralytics) — Ultralytics (pretrained on the [COCO dataset](https://cocodataset.org)) | AGPL-3.0 |
| Text-to-speech | [Piper](https://github.com/rhasspy/piper) with the `en_US-lessac-medium` voice — Rhasspy project | MIT |
| Web framework | [Flask](https://flask.palletsprojects.com) + Flask-CORS | BSD-3-Clause / MIT |
| Vision utilities | [OpenCV](https://opencv.org), [NumPy](https://numpy.org) | Apache-2.0 / BSD |

All models are used as published pretrained weights; no additional training data was collected. Note that Ultralytics YOLO is AGPL-3.0-licensed — retain source availability of this project when distributing.

---

## License

Distributed under the MIT License. See `LICENSE` for more information.
