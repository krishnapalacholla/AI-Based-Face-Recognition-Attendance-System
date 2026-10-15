import cv2

from camera.camera import Camera
from recognition.face_detector import FaceDetector


camera = Camera()
detector = FaceDetector()

camera.start()

while True:

    frame = camera.read_frame()

    if frame is None:
        break

    faces = detector.detect_faces(frame)

    for face in faces:

        x1, y1, x2, y2 = map(int, face.bbox)

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )

    camera.show_frame(frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.stop()