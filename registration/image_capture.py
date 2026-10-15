"""
image_capture.py

Handles face image capture during user registration.
Provides an ImageCapture class that wraps the camera
and face detector for clean, guided image collection.
"""

from pathlib import Path

import cv2

from camera.camera import Camera
from recognition.face_detector import FaceDetector


class ImageCapture:
    """
    Guided face image capture for user registration.

    Usage:
        capture = ImageCapture(user_name="Alice")
        count   = capture.run()          # opens webcam window
        # returns number of images saved (0 = cancelled)
    """

    # --------------------------------------------------
    # SETTINGS
    # --------------------------------------------------

    DATASET_FOLDER  = Path("dataset")
    MAXIMUM_IMAGES  = 5
    WINDOW_TITLE    = "Register Face — SPACE: Capture | Q: Quit"

    def __init__(self, user_name: str):

        self.user_name = user_name.strip()

        self.user_folder = (
            self.DATASET_FOLDER / self.user_name
        )

        self.camera   = Camera()
        self.detector = FaceDetector()
        try:
            from database.database import get_setting
            self.MAXIMUM_IMAGES = int(get_setting("registration_images", "5"))
        except Exception:
            self.MAXIMUM_IMAGES = 5

    # --------------------------------------------------
    # PREPARE FOLDER
    # --------------------------------------------------

    def prepare_folder(self):
        """
        Create the user's dataset folder and
        remove any pre-existing images.
        """
        self.DATASET_FOLDER.mkdir(exist_ok=True)

        if self.user_folder.exists():
            old_images = list(
                self.user_folder.glob("*.jpg")
            )
            for img in old_images:
                img.unlink()

        self.user_folder.mkdir(exist_ok=True)

    # --------------------------------------------------
    # SAVE FACE CROP
    # --------------------------------------------------

    def save_face_crop(
        self,
        frame,
        face,
        image_count: int
    ) -> bool:
        """
        Crop and save a single face image.
        Returns True on success, False on failure.
        """
        x1, y1, x2, y2 = map(int, face.bbox)

        h, w = frame.shape[:2]

        pad_x = int((x2 - x1) * 0.5)
        pad_y = int((y2 - y1) * 0.5)

        crop_x1 = max(0, x1 - pad_x)
        crop_y1 = max(0, y1 - pad_y)
        crop_x2 = min(w, x2 + pad_x)
        crop_y2 = min(h, y2 + pad_y)

        face_image = frame[crop_y1:crop_y2, crop_x1:crop_x2]

        if face_image.size == 0:
            return False

        image_path = (
            self.user_folder
            / f"img_{image_count:03}.jpg"
        )

        return cv2.imwrite(str(image_path), face_image)

    # --------------------------------------------------
    # DRAW OVERLAY
    # --------------------------------------------------

    def draw_overlay(
        self,
        frame,
        faces,
        image_count: int
    ):
        """
        Draw face bounding boxes and HUD text
        onto the frame in-place.
        """
        h, w = frame.shape[:2]

        # Face boxes
        for face in faces:
            x1, y1, x2, y2 = map(int, face.bbox)
            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

        # Progress bar background
        bar_w = int(w * 0.55)
        progress = image_count / self.MAXIMUM_IMAGES
        filled_w = int(bar_w * progress)
        bx, by = 20, 20

        cv2.rectangle(
            frame,
            (bx, by),
            (bx + bar_w, by + 22),
            (40, 40, 40),
            -1
        )
        if filled_w > 0:
            cv2.rectangle(
                frame,
                (bx, by),
                (bx + filled_w, by + 22),
                (0, 220, 100),
                -1
            )
        cv2.rectangle(
            frame,
            (bx, by),
            (bx + bar_w, by + 22),
            (100, 100, 100),
            1
        )

        # Text
        cv2.putText(
            frame,
            f"Captured: {image_count} / {self.MAXIMUM_IMAGES}",
            (bx, by + 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.70,
            (0, 255, 100),
            2
        )
        cv2.putText(
            frame,
            "SPACE: Capture  |  Q: Quit",
            (bx, by + 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (200, 200, 200),
            1
        )

        face_status = (
            f"Faces: {len(faces)}"
            if faces
            else "No face detected"
        )
        color = (0, 255, 0) if faces else (0, 100, 255)
        cv2.putText(
            frame,
            face_status,
            (bx, by + 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            color,
            2
        )

    # --------------------------------------------------
    # RUN
    # --------------------------------------------------

    def run(self) -> int:
        """
        Open the webcam and collect face images.
        Returns the number of images successfully saved.
        """
        self.prepare_folder()

        image_count = 0

        try:
            self.camera.start()

            while image_count < self.MAXIMUM_IMAGES:

                frame = self.camera.read_frame()
                if frame is None:
                    print("Failed to read frame.")
                    break

                faces = self.detector.detect_faces(frame)

                self.draw_overlay(frame, faces, image_count)

                cv2.imshow(self.WINDOW_TITLE, frame)

                key = cv2.waitKey(1) & 0xFF

                # SPACE — capture
                if key == ord(" "):
                    if len(faces) == 0:
                        print("No face detected. Try again.")
                        continue
                    if len(faces) > 1:
                        print(
                            "Multiple faces detected. "
                            "Only one person should be visible."
                        )
                        continue

                    image_count += 1
                    saved = self.save_face_crop(
                        frame,
                        faces[0],
                        image_count
                    )
                    if saved:
                        print(f"Captured image {image_count}")
                    else:
                        image_count -= 1
                        print("Failed to save image.")

                # Q — quit
                elif key == ord("q"):
                    break

        finally:
            self.camera.stop()
            cv2.destroyAllWindows()

        if image_count == 0:
            print("\nRegistration cancelled — no images captured.")
            return 0

        print(
            f"\n{image_count} face images captured "
            f"for '{self.user_name}'."
        )
        return image_count
