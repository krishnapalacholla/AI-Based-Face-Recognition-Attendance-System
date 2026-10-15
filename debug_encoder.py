import cv2
from pathlib import Path

from recognition.face_detector import FaceDetector

detector = FaceDetector()

image_path = Path("dataset/krishna/img_001.jpg")

image = cv2.imread(str(image_path))

print("Image Shape:", image.shape)

faces = detector.detect_faces(image)

print("Faces Found:", len(faces))

if len(faces) > 0:

    face = faces[0]

    print("Bounding Box:", face.bbox)

    print("Embedding Length:", len(face.embedding))