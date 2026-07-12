import cv2
import threading
import sounddevice as sd  # Used to instantly kill audio card playback
from time import perf_counter, time, strftime

from ocr.paddle import OCR
from modes.reading import process
from tts.piper import PiperTTS
from camera.camera import Camera

# Global tracking variable for our speaker thread worker
speaker_thread = None


def async_speak(tts_engine, text):
    """Worker function to process and play audio on a separate thread."""
    try:
        tts_engine.speak(text)
    except Exception as e:
        print(f"\n[TTS Thread Error]: {e}")


def main():
    global speaker_thread
    print("Initializing components...")

    ocr = OCR()
    tts = PiperTTS()
    cam = Camera()

    capture_interval = 3.0  # seconds
    last_capture_time = time()

    print("\n=======================================================")
    print("VisionMate Live Preview Active!")
    print("  - Press 'q' to Quit application.")
    print("  - Press 's' to STOP/SILENCE active audio instantly.")
    print("=======================================================")

    try:
        while True:
            # 1. Capture live frame and show preview smoothly
            frame = cam.capture()
            cv2.imshow("VisionMate Live Feed", frame)

            # 2. Check time interval
            current_time = time()
            if current_time - last_capture_time >= capture_interval:
                
                # Check if previous speech thread is still running
                # If it's running, we skip triggering a new cycle to prevent overlapping audio
                if speaker_thread is None or not speaker_thread.is_alive():
                    print(f"\n[{strftime('%H:%M:%S')}] --- Triggering Pipeline ---")
                    
                    text = ocr.read(frame)
                    if text.strip():
                        result = process(text)
                        print(f"Reading: {result}")

                        # Fire up the background speaker thread (Non-blocking)
                        speaker_thread = threading.Thread(
                            target=async_speak, 
                            args=(tts, result), 
                            daemon=True
                        )
                        speaker_thread.start()
                    else:
                        print("No text detected.")
                else:
                    print(".", end="", flush=True) # Quietly indicate audio is still playing

                last_capture_time = time()

            # 3. Handle Keyboard Interrupts from cv2 window
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord("q"):
                break
            
            elif key == ord("s"):
                print("\n[AUDIO KILL SWITCH] Silencing speaker instantly...")
                sd.stop()  # Aborts all hardware sound reproduction streams immediately

    finally:
        sd.stop()
        cam.release()
        cv2.destroyAllWindows()
        print("\nApplication cleanly terminated.")


if __name__ == "__main__":
    main()