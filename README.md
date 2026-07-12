# VisionMate 👁️🔊

**VisionMate** is an offline, network-capable AI-powered accessibility assistant that helps users read printed text using local, on-device AI models.

By turning a laptop into an edge computing cluster and utilizing a mobile phone as a wireless sensor, VisionMate extracts text via OCR, cleans scanning errors with a local LLM, and streams natural speech directly back to the user's hand without relying on external cloud APIs.

Built for **OSDHack 2026** with a focus on **efficient, edge-deployed on-device AI**.

---

## Features

- 📱 **Distributed Architecture:** Use any mobile phone browser on the same Wi-Fi network as your scanner and audio output device.
- 📝 **Offline OCR:** Text extraction powered by PaddleOCR running locally on the laptop host.
- 🤖 **Contextual Correction Shield:** Rigid formatting correction rules using a local Qwen 2.5 instance to seamlessly stitch broken lines and fix misread characters without hallucinations.
- 🔊 **Targeted Offline Speech:** Natural, low-latency text-to-speech generation using Piper (Lessac Medium) compiled directly to disk.
- 🌐 **True Local Privacy:** Zero internet connection required after initial setup. 100% processing happens on your local area network (LAN).
- 🍓 **Hardware Native Portability:** Decoupled layout designed for smooth upcoming integration with standalone Raspberry Pi or dedicated accessibility hardware.

---

## Architecture

```
[Mobile Client Browser] ---> (Base64 JPEG Frame via Wi-Fi LAN) ---> [Laptop Server Backend]
        ▲                                                                   │
        │                                                            (PaddleOCR Execution)
        │                                                                   ▼
        │                                                            (Qwen 2.5 Correction)
        │                                                                   ▼
        │                                                            (Piper Audio Synthesis)
        │                                                                   │
[Audio Stream Output] <------- (Binary WAV Delivery File) <------------------┘
```

---

## Tech Stack

| Component | Technology | Role |
|------------|------------|------|
| **Server Framework** | Flask 3.0.3 & Flask-CORS | Local network distribution & streaming endpoints |
| **OCR** | PaddleOCR 2.9.1 | Local image character recognition |
| **LLM Engine** | Qwen2.5:1.5B (Ollama Client) | Contextual reading correction shield |
| **TTS Engine** | Piper (Lessac Medium) | Native Wave compilation synthesis |
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
│   ├── prompts.py        # Strict structured instructions protecting text evaluation
│   └── qwen.py           # Explicit Ollama Local Client orchestration layer
├── modes/
│   └── reading.py        # Clean text formatting pipelines
├── ocr/
│   └── paddle.py         # PaddleOCR framework engine wrappers
├── static/
│   └── output.wav        # Generated real-time synthesized network audio file
├── tts/
│   └── piper.py          # Class wrapper handling synthesis to physical disk storage
│
├── .gitignore             # Prevents environment files and binary weights tracking
├── requirements.txt       # Fixed library versions ensuring dependency safety
├── config.py               # Shared global pipeline configurations
└── server.py               # Active network Flask application server loop
```

---

## Installation & Network Setup

### 1. Clone Repository & Environment Configuration

```bash
git clone https://github.com/yourusername/visionmate.git
cd visionmate

# Create Python 3.10 virtual environment
python -m venv venv310

# Windows activation
venv310\Scripts\activate
# Linux/Ubuntu activation
source venv310/bin/activate

# Install dependency tree
pip install -r requirements.txt
```

### 2. Model Dependencies Setup

#### A. Ollama (LLM) Configuration

1. Download the tool engine directly from [Ollama's official page](https://ollama.com).
2. Pull the specified lightweight model:

   ```bash
   ollama pull qwen2.5:1.5b
   ```

3. **CRITICAL:** Launch the Ollama service to listen across your network rather than only looking internally at localhost:
   - **Windows (CMD):** `set OLLAMA_HOST=0.0.0.0` then `ollama serve`
   - **Linux/Ubuntu:** `OLLAMA_HOST=0.0.0.0 ollama serve`

#### B. Piper (TTS) Downloads

Install the HuggingFace CLI utility to download the voice model and corresponding token properties structure directly into your local storage paths:

```bash
pip install -U "huggingface_hub[cli]"
hf download rhasspy/piper-voices --include "en/en_US/lessac/medium/*" --local-dir models
```

---

## Execution

1. Boot up the server application on your processing laptop:

   ```bash
   python server.py
   ```

2. Take note of your laptop's Local IP Address displayed in the terminal startup configurations, or check your network interface card settings (`ipconfig` on Windows / `hostname -I` on Linux).
3. Open your mobile phone browser on the **same Wi-Fi network** and navigate to:

   ```text
   http://<YOUR_LAPTOP_IP>:5000
   ```

   *(e.g., `http://10.253.122.40:5000`)*

> 💡 **Mobile Camera Authorization Note:** Because local network connections run over unencrypted `http://`, mobile browsers block hardware security layers by default. To unlock the camera on an Android Chrome client, navigate to `chrome://flags`, search for `#unsafely-treat-insecure-origin-as-secure`, set it to **Enabled**, paste your target URL entry (`http://<YOUR_LAPTOP_IP>:5000`), and tap **Relaunch**.

---

## Pipeline Progression Matrix

### Executed Local Network Loop (Current Hackathon State)

```
Mobile Capture (Base64 Web Image)
       ↓
Network Ingestion (Flask Server Decoding)
       ↓
Local OCR (PaddleOCR Engine Analysis)
       ↓
Strict Correction (Qwen 2.5 Text Assembly)
       ↓
Direct Synthesis (Piper wav_file Compilation)
       ↓
Audio Delivery (HTML5 browser streaming playback output)
```

---

## Progress Tracking

- [x] WebRTC Front-facing / Rear-facing Mobile Camera Capture Stream
- [x] Base64 Image Matrix Recovery Pipeline via OpenCV
- [x] PaddleOCR Segment Processing
- [x] Explicitly Anchored Local Ollama Qwen Core Orchestration
- [x] Isolated Piper Disk Synthesis Architecture (`synthesize_wav`)
- [x] Multi-Device Web-Streaming Sound Playback Interface
- [ ] Frame Duplicate Change Detection (Filtering duplicate text frames)
- [ ] Explain Mode Extension
- [ ] Summary Mode Extension
- [ ] Standalone Device Shell Enclosure Deployment (Raspberry Pi Setup)

---

## Performance Benchmark (Current Setup)

| Pipeline Phase | Execution Profile | Metrics / Latency |
| --- | --- | --- |
| Network Image Capture | Device to Server Transfer | ~0.2 s |
| Word/Character Recognition | PaddleOCR Engine Analysis | ~0.7 s |
| Reading Post-Correction | Qwen 2.5 Optimization | ~1.1 s |
| Text-to-Speech Compilation | Piper Wave Matrix Building | ~1.4 s |
| Client Audio Delivery | HTML5 Stream Buffering | ~0.1 s |

---

## License

Distributed under the MIT License. See `LICENSE` for more information.

---

## Acknowledgements

- **PaddleOCR** — High performance local text identification engines.
- **Ollama & Qwen Team** — Fast, highly efficient open model parameters for offline systems.
- **Rhasspy Piper Project** — Incredibly fast, natural localized text-to-speech engine architectures.
