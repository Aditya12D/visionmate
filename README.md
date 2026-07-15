# VisionMate AI Assistant

VisionMate is an offline AI accessibility assistant designed to help visually impaired individuals interact with their environment using real-time OCR and scene descriptions.

## Project Structure

The project follows a clean, professional Python package layout:

```
visionmate-root/
├── app.py                  # Main CLI/GUI application with live OpenCV preview
├── server.py               # Flask web api server serving the web-based app interface
├── requirements.txt        # Project dependencies
├── README.md               # Project documentation
├── models/                 # Model files (YOLO weights and Piper TTS folders)
│   ├── yolo11n.pt          # YOLOv11 model weights
│   └── en/                 # Piper en_US models
│       └── en_US-lessac-medium.onnx
├── static/                 # Static web files (compiled audio outputs)
│   └── output.wav
├── tests/                  # Test suites and testing scripts
│   ├── test.py             # Offline test script
│   └── assets/             # Mock test images
└── visionmate/             # Core application package
    ├── __init__.py         # Package marker
    ├── config.py           # General constants and model thresholds
    ├── camera.py           # Camera device capture wrapper
    ├── detector.py         # Object detector using YOLOv11
    ├── ocr.py              # OCR reader using PaddleOCR
    ├── tts.py              # Text to Speech using Piper Voice
    ├── llm/                # LLM module
    │   ├── __init__.py     # Module initialization
    │   ├── prompts.py      # LLM prompts for different modes
    │   └── qwen.py         # Ollama Qwen wrapper for LLM queries
    └── modes/              # Operational modes of VisionMate
        ├── __init__.py     # Module initialization
        ├── reading.py      # Text processing / Reading mode
        └── walking.py      # Hazard analysis / Walking mode
```

## Running the Project

### Prerequisites
Make sure your environment is activated.
For example:
```powershell
.\venv310\Scripts\Activate.ps1
```

### Running the Live App
To start the OpenCV preview locally:
```powershell
python app.py
```

### Running the Web Server Dashboard
To launch the Flask server:
```powershell
python server.py
```
Open a browser and navigate to `http://localhost:5000` to interact with the dashboard.

### Running the Verification Script
To run the safety/walking checks offline:
```powershell
$env:PYTHONPATH="."
python tests/test.py
```
