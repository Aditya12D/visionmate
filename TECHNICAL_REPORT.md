# VisionMate — Technical Report

*Covers: technical specifications, local-AI verification, and evaluation. All figures below were **measured on the test device described in §1.6**, not estimated.*

---

## 1. Technical Specifications

### 1.1 Models and runtimes

| Task | Model | Runtime | Precision / format | On-disk size |
|---|---|---|---|---|
| Text detection | PP-OCRv3 (en, mobile) | PaddlePaddle (CPU) | FP32 inference graph | 3.8 MB |
| Text recognition | PP-OCRv4 (en, mobile) | PaddlePaddle (CPU) | FP32 inference graph | 9.8 MB |
| Text-angle classification | PP-OCR mobile cls | PaddlePaddle (CPU) | FP32 inference graph | 2.1 MB |
| OCR text correction | Qwen 2.5 — 1.5B Instruct | Ollama / llama.cpp (GPU-accelerated) | **GGUF Q4_K_M (4-bit quantized)** | 986 MB |
| Obstacle detection | YOLOv11-nano (2.6 M params) | Ultralytics / PyTorch (CPU) | FP32 | 5.6 MB |
| Speech synthesis | Piper en_US-lessac-medium | ONNX Runtime (CPU) | ONNX FP32 | 63 MB |
| **Total model footprint** | | | | **≈ 1.07 GB** |

### 1.2 Quantization and optimization techniques

- **4-bit quantization (Q4_K_M)** of the LLM via Ollama/llama.cpp — the single largest optimization: a 1.5B-parameter model runs in 1.2 GB of memory, fully GPU-resident.
- **Nano/mobile model variants** chosen at every stage (YOLO-*nano*, PaddleOCR *mobile* checkpoints, Piper *medium* voice) to fit the whole pipeline into a consumer laptop.
- **Warm model residency**: all models are loaded once at server boot ("warm-up"), never per-request. Ollama keeps the LLM resident in GPU memory between requests.
- **In-memory audio synthesis** (`BytesIO` → Base64) eliminates disk I/O from the hot path.
- **Client-side JPEG compression** (quality 0.6) keeps a frame at roughly 60–140 KB, minimizing LAN transfer time.
- **OCR confidence gating** (threshold 0.75) discards unreliable lines *before* they consume LLM tokens.

### 1.3 Inference latency (measured)

Method: 5 sequential requests per endpoint against the running server on localhost, warm models, using the actual demo images (900×400 text image; 810×1080 street scene). Timed end-to-end: Base64 decode → inference → TTS → Base64 encode.

| Endpoint | Pipeline | Min | Median | Max |
|---|---|---|---|---|
| `/api/reading-mode` | OCR + LLM + TTS | 0.73 s | **0.74 s** | 1.76 s |
| `/api/walking-mode` | YOLO + spatial + TTS | 0.18 s | **0.19 s** | 0.19 s |
| Cold start (first request after boot) | reading / walking | — | 2.0 s / 3.8 s | — |

Over Wi-Fi from the phone, add ≈ 0.1–0.3 s transfer overhead per round-trip. Perceived cycle time additionally includes audio playback (several seconds of speech) plus a deliberate 1.5 s pause.

### 1.4 CPU / GPU / NPU usage

| Component | Compute unit |
|---|---|
| Qwen 2.5 1.5B (Ollama) | **100 % GPU** — Ollama auto-selects the available accelerator (CUDA / ROCm / Metal); confirmed via `ollama ps` |
| PaddleOCR | CPU (`use_gpu=False`) |
| YOLOv11n | CPU |
| Piper TTS | CPU |
| NPU | Not used |

Compute placement is deliberate: the heaviest model (the LLM) is offloaded to the GPU, while the lighter vision and speech models run on CPU — so the two never contend for the same processor and the pipeline stays responsive. On a machine without a usable GPU, Ollama transparently falls back to CPU inference; every component of the stack is CPU-capable.

**No high-end hardware is required.** The LLM needs only ~1.2 GB of GPU memory, so an ordinary entry-level or integrated GPU is sufficient — and a plain CPU works too, just with higher latency. Total system footprint (~4 GB RAM, ~1 GB of weights) is deliberately sized for everyday consumer machines and edge devices, not workstation GPUs.

### 1.5 Peak memory usage (measured, RSS)

| Process | RSS |
|---|---|
| Flask worker (PaddleOCR + YOLO + Piper loaded) | ≈ 2.97 GB |
| Flask debug reloader parent (dev mode only) | ≈ 0.52 GB |
| Ollama daemon | ≈ 0.05 GB |
| Qwen 2.5 model (GPU, unified memory) | ≈ 1.2 GB |
| **Peak total** | **≈ 4.2 GB** (≈ 3.7 GB with debug reloader disabled) |

Comfortably within the 16 GB test machine; 8 GB machines should also work with reduced headroom.

### 1.6 Tested device specifications

The system was tested on **two different server machines across two operating systems**:

| | |
|---|---|
| Server — test rig 1 *(source of the measured figures above)* | MacBook, **Apple M5**, 16 GB unified memory, macOS 26.6 — Python 3.10 (conda env) |
| Server — test rig 2 | Windows laptop, **13th Gen Intel Core i7-13620H**, 16 GB RAM — Python 3.10 (`venv310` virtual environment) |
| Client | Smartphone browser (iPhone/Safari in testing; any Android or iOS phone works), over 2.4/5 GHz Wi-Fi LAN |
| Software stack | Flask 3, PaddleOCR 2.9.1, ultralytics (YOLO11), Piper TTS, Ollama |

Running verified on both an ARM machine (Apple Silicon/macOS) and an x86 machine (Intel/Windows) — **nothing in VisionMate is platform-specific.** Linux is equally supported (all dependencies are cross-platform; Ollama ships for all three OSes), and the client is any modern browser: Android Chrome, iOS Safari, or a desktop browser all work, since the "app" is a plain web page served over the LAN.

### 1.7 Hardware portability — beyond the laptop

The compute node is **hardware-agnostic**: the only physical requirements on the user's side are **a camera and a speaker**. In the current prototype a smartphone browser provides both — connected purely over the local Wi-Fi network, with **no internet involved** — which proves the server needs no attached peripherals at all. The same design ports directly to embedded targets:

- **Raspberry Pi / single-board computers:** the entire stack is plain Python with CPU-capable models. Piper TTS was *originally built for the Raspberry Pi 4*, PaddleOCR ships mobile-class checkpoints, YOLOv11-nano (2.6 M params) runs on ARM CPUs, and Ollama officially supports ARM64 Linux — the 4-bit-quantized 1.5B LLM fits in a Pi 5's 8 GB RAM. Latency would be higher than the figures in §1.3 (measured on the laptop test rig), and the LLM could be swapped for an even smaller variant (e.g. a 0.5B model) on constrained boards.
- **Dedicated wearable form factor:** with a USB/CSI camera module and a small speaker or bone-conduction headset attached directly to the board, the phone disappears entirely and VisionMate becomes a self-contained assistive device — same code, same models, zero cloud.
- **Edge AI boards (NVIDIA Jetson and similar):** Jetson-class devices run the same stack with GPU acceleration via Ollama's ARM64+CUDA builds; boards with NPUs can additionally take over the vision models (YOLO and PaddleOCR both export to ONNX/TensorRT for NPU/accelerator runtimes) — a natural next optimization step.
- **Any laptop/desktop:** Windows, Linux, or macOS; a simple integrated or entry-level GPU is plenty (the LLM needs only ~1.2 GB of GPU memory), and pure CPU works as well — Ollama auto-detects whatever is available.

This flexibility is a direct consequence of the local-first architecture: because nothing depends on an internet service, the whole system relocates to any device that can run Python and hold ~1 GB of model weights.

---

## 2. Local AI Verification

| Question | Answer |
|---|---|
| What runs fully on-device? | **Everything**: OCR (PaddleOCR), text correction (Qwen 2.5 via Ollama bound to `127.0.0.1`), obstacle detection (YOLOv11n), spatial reasoning, and speech synthesis (Piper) all execute on the laptop. |
| What requires internet? | **Nothing at runtime.** Internet is needed exactly once, at install time, to download model weights (Ollama pull, Piper voice, YOLO weights) and pip dependencies. |
| Does any user data leave the device? | **No.** Camera frames travel only from the phone to the laptop over the local network (HTTPS, self-signed certificate) and are processed in RAM. No frame, text, or audio is written to disk, logged, or transmitted to any external service. There is no analytics or telemetry code in the application. |
| How to verify | Disable the internet uplink (keep the Wi-Fi LAN or use a phone hotspot without data): the full pipeline continues to work — this is demonstrated in the demo video. |

---

## 3. Evaluation

### 3.1 Method

Manual functional evaluation on the test device: synthetic and real printed-text images for reading mode, and real photographs (street scene containing a bus and pedestrians) for walking mode, verified against ground truth by inspection. No formal benchmark dataset was run; figures below are qualitative spot checks plus the measured latency in §1.3.

### 3.2 Quality results (spot checks)

- **Reading mode — OCR + LLM stitching:** a test image containing three separately rendered lines ("VisionMate helps people / read printed text aloud / using local AI models.") was returned as one grammatically joined sentence with correct punctuation — demonstrating line-stitching, not just transcription. Hyphenated line-breaks (e.g. "every-\nday") are rejoined into single words.
- **Walking mode — detection and spatialization:** on a street-scene photo, the system produced *"Stop. person close on your left. Danger! bus immediate ahead. clear right."* — correct object classes, correct zone assignment, correct proximity ranking, and correct escalation to the emergency "Stop." prefix.
- **Confidence gating:** OCR lines under 0.75 confidence are dropped, trading recall for precision — for an assistive reader, speaking wrong text is worse than skipping doubtful text.

### 3.3 Baseline comparison

| | VisionMate (local) | Typical cloud pipeline (Vision API + LLM + TTS) |
|---|---|---|
| Reading latency | ~0.7–2 s | ~1–3 s (network dependent) |
| Works offline | ✅ | ❌ |
| Per-use cost | 0 | metered API cost |
| Data leaves device | Never | Every frame |
| Text-correction quality | Good (1.5B model) | Better (frontier models) |

The deliberate trade-off: a frontier cloud model corrects text better than a 4-bit 1.5B model, but VisionMate's privacy, cost, and offline properties are architectural guarantees the cloud cannot match.

### 3.4 Known failure cases and limitations

1. **Handwriting and stylized fonts** — PaddleOCR is trained for printed text; cursive or decorative fonts fail or fall below the confidence gate.
2. **Low light, glare, and motion blur** degrade both OCR and YOLO accuracy.
3. **English-only** — OCR models, the correction prompt, and the TTS voice are all English; other scripts are unsupported in this build.
4. **LLM over-correction** — a 1.5B model can occasionally paraphrase instead of strictly correcting, despite prompt constraints; rare and mitigated by low temperature (0.2).
5. **YOLO class ceiling** — detection is limited to the 80 COCO classes. Critically for navigation: **stairs, curbs, potholes, and glass doors are not detected.**
6. **Proximity is a heuristic**, not depth sensing — bounding-box area ratio confuses "small object very near" with "large object far away".
7. **Sampling rate** — one frame per spoken cycle (several seconds); a fast-moving hazard can appear between frames.
8. **Not a certified assistive device** — VisionMate is a prototype that complements, and must never replace, a white cane or guide dog (see Privacy & Safety in the README).
