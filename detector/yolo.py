# detector/yolo.py

from ultralytics import YOLO


class YOLODetector:
    def __init__(self, model_path: str = "yolo11n.pt", conf: float = 0.35):
        """
        Initialize the YOLO detector.

        Args:
            model_path: Path to the YOLO model.
            conf: Confidence threshold.
        """
        self.model = YOLO(model_path)
        self.conf = conf

    def detect(self, frame):
        """
        Detect objects in an OpenCV frame.

        Args:
            frame: OpenCV image (numpy array, BGR)

        Returns:
            List of detected objects.
        """
        results = self.model.predict(
            source=frame,
            conf=self.conf,
            verbose=False
        )

        detections = []

        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                confidence = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2

                detections.append({
                    "class": result.names[cls_id],
                    "confidence": round(confidence, 2),
                    "bbox": [x1, y1, x2, y2],
                    "center": [cx, cy]
                })

        return {
            "width": frame.shape[1],
            "height": frame.shape[0],
            "detections": detections
        }