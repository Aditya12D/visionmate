import cv2


class Camera:

    def __init__(self, camera_index=0):
        self.cap = cv2.VideoCapture(camera_index)

        if not self.cap.isOpened():
            raise RuntimeError("Could not open camera.")

    def capture(self):
        ret, frame = self.cap.read()

        if not ret:
            raise RuntimeError("Failed to capture frame.")

        return frame

    def save_frame(self, frame, path):
        cv2.imwrite(path, frame)

    def start_preview(self):
        """Starts a live camera preview window. Press 'q' to exit."""
        print("Starting live preview. Press 'q' in the window to stop...")
        try:
            while True:
                frame = self.capture()

                # Display the frame in a window named 'VisionMate Preview'
                cv2.imshow("VisionMate Preview", frame)

                # Break the loop if 'q' key is pressed
                # 1ms delay allows the window to refresh fluidly
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
        finally:
            cv2.destroyAllWindows()

    def release(self):
        self.cap.release()


# Quick test execution
if __name__ == "__main__":
    cam = Camera()
    try:
        cam.start_preview()
    finally:
        cam.release()