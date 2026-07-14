
from detector.yolo import YOLODetector

class WalkingMode:
    def __init__(self):
        self.detector = YOLODetector()
        
        # Explicitly define items that are safe to ignore while walking.
        # Everything NOT in this list will be treated as a moving or structural hazard.
        self.safe_scenery = {
            "cup", "glass", "fork", "knife", "spoon", "bowl", "banana", "apple", 
            "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", 
            "donut", "cake", "book", "clock", "vase", "scissors", "teddy bear", 
            "hair drier", "toothbrush", "tie", "mouse", "keyboard", "remote"
        }

    def process(self, frame):
        """
        Processes the frame, maps spatial zones, and estimates proximity.
        """
        raw_data = self.detector.detect(frame)
        width = raw_data["width"]
        height = raw_data["height"]
        total_frame_area = width * height
        processed_detections = []
        
        left_boundary = width / 3
        right_boundary = (2 * width) / 3
        
        for detection in raw_data["detections"]:
            obj_class = detection["class"]
            cx = detection["center"][0]
            bbox = detection["bbox"]
            
            # 1. Determine Horizontal Spatial Position
            if cx < left_boundary:
                position = "on your left"
            elif cx > right_boundary:
                position = "on your right"
            else:
                position = "ahead"
                
            # SAFE BY DEFAULT LOGIC:
            # If the object is NOT in the safe list, it's automatically a high-priority hazard.
            priority = "low" if obj_class in self.safe_scenery else "high"
            
            # 2. Estimate Proximity based on Bounding Box Area Ratio
            box_width = bbox[2] - bbox[0]
            box_height = bbox[3] - bbox[1]
            box_area = box_width * box_height
            area_ratio = box_area / total_frame_area
            
            if area_ratio > 0.30:
                proximity = "immediate"
            elif area_ratio > 0.10:
                proximity = "close"
            else:
                proximity = "far"
            
            processed_detections.append({
                **detection,
                "priority": priority,
                "position": position,
                "proximity": proximity,
                "area_ratio": area_ratio
            })
            
        return {
            "width": width,
            "height": height,
            "detections": processed_detections
        }

    # Inside your generate_alert_text method in visionmate/modes/walking.py

    def generate_alert_text(self, processed_data):
        """
        Constructs a complete panoramic phrase scanning from Left to Center to Right.
        Fails safe if the environment is completely unmapped or empty.
        """
        detections = processed_data["detections"]
        
        # 1. Edge-Case Safety Fallback: Complete lack of structural tracking data
        if not detections:
            return "NEEDS_SCENERY_DESCRIPTION"

        # 2. Filter out 'far' items to keep the spatial text dense and relevant
        actionable_items = [d for d in detections if d["proximity"] != "far"]
        
        if not actionable_items:
            return "NEEDS_SCENERY_DESCRIPTION"

        # Separate detections into their respective spatial columns
        left_zone = [d for d in actionable_items if "left" in d["position"]]
        center_zone = [d for d in actionable_items if "ahead" in d["position"]]
        right_zone = [d for d in actionable_items if "right" in d["position"]]

        # Helper function to find the single most urgent object in a specific zone
        def get_top_object_phrase(zone_items):
            if not zone_items:
                return "clear"
                
            # Sort by proximity/size severity
            zone_items.sort(key=lambda d: (d["priority"] == "high", d["area_ratio"]), reverse=True)
            top = zone_items[0]
            
            # Trigger an immediate stop prefix if a high hazard is right in front of them
            if top["proximity"] == "immediate" and top["priority"] == "high":
                return f"Danger! {top['class']} immediate"
                
            return f"{top['class']} {top['proximity']}"

        # 3. Build the individual structural components
        left_status = get_top_object_phrase(left_zone)
        center_status = get_top_object_phrase(center_zone)
        right_status = get_top_object_phrase(right_zone)

        # OPTIMIZATION: If all lanes are clear, keep it short!
        if left_status == "clear" and center_status == "clear" and right_status == "clear":
            return "All clear."

        # Re-attach spatial context labels for the spoken sentence
        left_phrase = f"{left_status} on your left" if left_status != "clear" else "clear left"
        center_phrase = f"{center_status} ahead" if center_status != "clear" else "clear ahead"
        right_phrase = f"{right_status} on your right" if right_status != "clear" else "clear right"

        # 4. Check if a high-priority hazard requires an emergency "Stop" call
        for item in actionable_items:
            if item["priority"] == "high" and item["proximity"] == "immediate":
                return f"Stop. {left_phrase}. {center_phrase}. {right_phrase}."

        # Standard navigational guidance sentence
        return f"{left_phrase}. {center_phrase}. {right_phrase}."