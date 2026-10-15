from insightface.app import FaceAnalysis


class FaceDetector:
    """
    Detects faces using InsightFace.
    """

    def __init__(self):
        self.app = FaceAnalysis()

        # Prepare the model
        self.app.prepare(
            ctx_id=0,
            det_size=(640, 640)
        )

    def detect_faces(self, frame):
        """
        Detect all faces in a frame.
        """
        return self.app.get(frame)