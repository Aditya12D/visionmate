from paddleocr import PaddleOCR


class OCR:
    def __init__(self):
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang="en"
        )

    def read(self, image_path, min_confidence=0.75):
        """
        Returns only the extracted text.
        """

        data = self.read_with_metadata(image_path, min_confidence)

        return "\n".join(item["text"] for item in data)

    def read_with_metadata(self, image_path, min_confidence=0.75):
        """
        Returns OCR results with metadata.

        Returns:
        [
            {
                "text": "...",
                "confidence": 0.98,
                "bbox": [...]
            },
            ...
        ]
        """

        result = self.ocr.ocr(image_path, cls=True)

        output = []

        if result and result[0]:

            for line in result[0]:

                bbox = line[0]
                text = line[1][0]
                confidence = line[1][1]

                if confidence >= min_confidence:

                    output.append({
                        "text": text,
                        "confidence": confidence,
                        "bbox": bbox
                    })

        return output