import cv2
import time
from modes.walking import WalkingMode

# Initialize walking mode
walker = WalkingMode()

# Load real image
test_frame = cv2.imread("test.jpg")

if test_frame is None:
    print("Error: Could not find 'test.jpg'.")
else:
    # 1. Process the frame through YOLO
    output = walker.process(test_frame)
    
    # 2. Benchmark Native Rule Engine Speed
    print("\n--- Running Pure Python Phrase Logic ---")
    start_time = time.time()
    
    alert_phrase = walker.generate_alert_text(output)
    
    end_time = time.time()
    latency = end_time - start_time
    
    # 3. Print Results
    print(f"Phrase Result    : '{alert_phrase}'")
    print(f"Inference Latency: {latency:.6f} seconds")
    print("-----------------------------------------")