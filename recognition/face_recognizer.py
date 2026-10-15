from pathlib import Path
import pickle

import cv2
import numpy as np

from camera.camera import Camera
from recognition.face_detector import FaceDetector
from attendance.attendance_manager import AttendanceManager


class FaceRecognizer:
    """
    Recognize multiple registered users using face embeddings
    and automatically mark attendance.
    """

    def __init__(
        self,
        threshold=0.45,
        confirmation_frames=5
    ):

        # --------------------------------------------------
        # RECOGNITION SETTINGS
        # --------------------------------------------------

        self.threshold = threshold

        self.confirmation_frames = (
            confirmation_frames
        )

        # --------------------------------------------------
        # FACE DETECTOR
        # --------------------------------------------------

        self.detector = FaceDetector()

        # --------------------------------------------------
        # LOAD EMBEDDINGS
        # --------------------------------------------------

        self.embeddings = (
            self.load_embeddings()
        )

        # --------------------------------------------------
        # ATTENDANCE MANAGER
        # --------------------------------------------------

        self.attendance_manager = (
            AttendanceManager()
        )

        # --------------------------------------------------
        # SESSION ATTENDANCE CACHE
        # --------------------------------------------------

        self.session_attendance = set()

        # --------------------------------------------------
        # PER-PERSON CONFIRMATION COUNTERS
        # --------------------------------------------------

        self.recognition_counts = {}

        # --------------------------------------------------
        # DISPLAY LOADED EMBEDDINGS
        # --------------------------------------------------

        print("\nLoaded Embeddings:")

        if len(self.embeddings) == 0:

            print(
                "No registered face embeddings found."
            )

        for (
            user_name,
            user_embeddings
        ) in self.embeddings.items():

            print(
                f"{user_name}: "
                f"{len(user_embeddings)} embeddings"
            )

    # --------------------------------------------------
    # LOAD EMBEDDINGS
    # --------------------------------------------------

    def load_embeddings(self):
        """
        Load stored face embeddings.
        """

        embedding_path = (
            Path("embeddings")
            / "embeddings.pkl"
        )

        if not embedding_path.exists():

            print(
                "Embeddings file not found."
            )

            return {}

        try:

            with open(
                embedding_path,
                "rb"
            ) as file:

                embeddings = pickle.load(
                    file
                )

            return embeddings

        except (
            pickle.UnpicklingError,
            EOFError,
            OSError
        ) as error:

            print(
                f"Failed to load embeddings: "
                f"{error}"
            )

            return {}

    # --------------------------------------------------
    # NORMALIZE EMBEDDING
    # --------------------------------------------------

    def normalize_embedding(
        self,
        embedding
    ):
        """
        L2 normalize a face embedding.
        """

        if embedding is None:

            return None

        embedding = np.asarray(
            embedding,
            dtype=np.float32
        )

        norm = np.linalg.norm(
            embedding
        )

        if norm == 0:

            return None

        return embedding / norm

    # --------------------------------------------------
    # COMPARE EMBEDDING
    # --------------------------------------------------

    def compare_embedding(
        self,
        embedding
    ):
        """
        Compare a live embedding with registered users
        using cosine similarity and top-k averaging.
        """

        live_embedding = self.normalize_embedding(
            embedding
        )

        if live_embedding is None:
            return "Unknown"

        best_name = "Unknown"
        best_score = -1.0
        second_best_score = -1.0

        for user_name, stored_embeddings in self.embeddings.items():

            if len(stored_embeddings) == 0:
                continue

            user_scores = []

            for stored_embedding in stored_embeddings:

                normalized_stored = self.normalize_embedding(
                    stored_embedding
                )

                if normalized_stored is None:
                    continue

                cosine_similarity = float(
                    np.dot(
                        live_embedding,
                        normalized_stored
                    )
                )

                user_scores.append(
                    cosine_similarity
                )

            if len(user_scores) == 0:
                continue

            user_scores.sort(
                reverse=True
            )

            top_k = min(
                5,
                len(user_scores)
            )

            user_score = float(
                np.mean(
                    user_scores[:top_k]
                )
            )

            if user_score > best_score:

                second_best_score = best_score
                best_score = user_score
                best_name = user_name

            elif user_score > second_best_score:

                second_best_score = user_score

        if best_score < 0:

            print(
                "Best Match: Unknown, "
                "Similarity: unavailable"
            )

            return "Unknown"

        margin = (
            best_score - second_best_score
            if second_best_score >= 0
            else best_score
        )

        print(
            f"Best Match: {best_name}, "
            f"Similarity: {best_score:.4f}, "
            f"Margin: {margin:.4f}"
        )

        minimum_similarity = self.threshold
        minimum_margin = 0.03

        if (
            best_score >= minimum_similarity
            and
            (
                second_best_score < 0
                or margin >= minimum_margin
            )
        ):
            return best_name

        return "Unknown"

    # --------------------------------------------------
    # UPDATE RECOGNITION COUNTER
    # --------------------------------------------------

    def update_recognition_count(
        self,
        name
    ):
        """
        Update confirmation count for an
        individual recognized user.
        """

        # --------------------------------------------------
        # IGNORE UNKNOWN
        # --------------------------------------------------

        if name == "Unknown":

            return False

        # --------------------------------------------------
        # ALREADY PROCESSED
        # --------------------------------------------------

        if name in self.session_attendance:

            return False

        # --------------------------------------------------
        # CREATE COUNTER
        # --------------------------------------------------

        if name not in self.recognition_counts:

            self.recognition_counts[name] = 0

        # --------------------------------------------------
        # INCREMENT COUNTER
        # --------------------------------------------------

        self.recognition_counts[name] = min(
            self.recognition_counts[name] + 1,
            self.confirmation_frames
        )

        # --------------------------------------------------
        # DISPLAY CONFIRMATION
        # --------------------------------------------------

        print(
            f"Confirming {name}: "
            f"{self.recognition_counts[name]}/"
            f"{self.confirmation_frames}"
        )

        # --------------------------------------------------
        # CONFIRMATION CHECK
        # --------------------------------------------------

        return (
            self.recognition_counts[name]
            >= self.confirmation_frames
        )

    # --------------------------------------------------
    # RESET MISSING USER COUNTERS
    # --------------------------------------------------

    def reset_missing_users(
        self,
        visible_names
    ):
        """
        Reset confirmation counters for users
        not recognized in the current frame.
        """

        names_to_reset = []

        for name in self.recognition_counts:

            if (
                name not in visible_names
                and
                name not in self.session_attendance
            ):

                names_to_reset.append(
                    name
                )

        for name in names_to_reset:

            self.recognition_counts[name] = 0

    # --------------------------------------------------
    # PROCESS ATTENDANCE
    # --------------------------------------------------

    def process_attendance(
        self,
        name
    ):
        """
        Process attendance once per recognition
        session for each confirmed user.
        """

        if name == "Unknown":

            return

        # --------------------------------------------------
        # SESSION CACHE CHECK
        # --------------------------------------------------

        if name in self.session_attendance:

            return

        # --------------------------------------------------
        # MARK ATTENDANCE
        # --------------------------------------------------

        self.attendance_manager.mark_attendance(
            name
        )

        # --------------------------------------------------
        # ADD TO SESSION CACHE
        # --------------------------------------------------

        self.session_attendance.add(
            name
        )

        # --------------------------------------------------
        # REMOVE CONFIRMATION COUNTER
        # --------------------------------------------------

        self.recognition_counts.pop(
            name,
            None
        )

        print(
            f"Identity confirmed: {name}"
        )

    # --------------------------------------------------
    # GET DISPLAY LABEL
    # --------------------------------------------------

    def get_display_label(
        self,
        name
    ):
        """
        Return webcam label for a recognized face.
        """

        if name == "Unknown":

            return "Unknown"

        if name in self.session_attendance:

            return (
                f"{name} - Attendance Recorded"
            )

        count = self.recognition_counts.get(
            name,
            0
        )

        return (
            f"Confirming {name} "
            f"{count}/"
            f"{self.confirmation_frames}"
        )

    # --------------------------------------------------
    # START RECOGNITION
    # --------------------------------------------------

    def start(self):
        """
        Start real-time multi-face recognition
        and automatic attendance marking.
        """

        # --------------------------------------------------
        # CHECK EMBEDDINGS
        # --------------------------------------------------

        if len(self.embeddings) == 0:

            print(
                "\nNo registered embeddings "
                "available."
            )

            print(
                "Register a user or generate "
                "embeddings first."
            )

            return

        # --------------------------------------------------
        # CREATE CAMERA
        # --------------------------------------------------

        camera = Camera()

        # --------------------------------------------------
        # START CAMERA
        # --------------------------------------------------

        camera.start()

        print(
            "\nRecognition Started"
        )

        print(
            "Multiple registered faces are supported."
        )

        print(
            "Press Q to Quit\n"
        )

        # --------------------------------------------------
        # RECOGNITION LOOP
        # --------------------------------------------------

        while True:

            # --------------------------------------------------
            # READ CAMERA FRAME
            # --------------------------------------------------

            frame = camera.read_frame()

            if frame is None:

                print(
                    "Failed to read camera frame."
                )

                break

            # --------------------------------------------------
            # DETECT FACES
            # --------------------------------------------------

            faces = self.detector.detect_faces(
                frame
            )

            # --------------------------------------------------
            # NAMES VISIBLE IN CURRENT FRAME
            # --------------------------------------------------

            visible_names = set()

            # --------------------------------------------------
            # PROCESS EACH FACE
            # --------------------------------------------------

            for face in faces:

                # --------------------------------------------------
                # BOUNDING BOX
                # --------------------------------------------------

                x1, y1, x2, y2 = map(
                    int,
                    face.bbox
                )

                # --------------------------------------------------
                # DEFAULT NAME
                # --------------------------------------------------

                name = "Unknown"

                # --------------------------------------------------
                # FACE RECOGNITION
                # --------------------------------------------------

                if face.embedding is not None:

                    name = self.compare_embedding(
                        face.embedding
                    )

                # --------------------------------------------------
                # RECOGNIZED USER
                # --------------------------------------------------

                if name != "Unknown":

                    visible_names.add(
                        name
                    )

                    confirmed = (
                        self.update_recognition_count(
                            name
                        )
                    )

                    if confirmed:

                        self.process_attendance(
                            name
                        )

                # --------------------------------------------------
                # RECTANGLE COLOR
                # --------------------------------------------------

                if name == "Unknown":

                    rectangle_color = (
                        0,
                        0,
                        255
                    )

                else:

                    rectangle_color = (
                        0,
                        255,
                        0
                    )

                # --------------------------------------------------
                # DRAW RECTANGLE
                # --------------------------------------------------

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    rectangle_color,
                    2
                )

                # --------------------------------------------------
                # DISPLAY LABEL
                # --------------------------------------------------

                display_name = (
                    self.get_display_label(
                        name
                    )
                )

                cv2.putText(
                    frame,
                    display_name,
                    (
                        x1,
                        max(
                            30,
                            y1 - 10
                        )
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    rectangle_color,
                    2
                )

            # --------------------------------------------------
            # RESET USERS NOT VISIBLE
            # --------------------------------------------------

            self.reset_missing_users(
                visible_names
            )

            # --------------------------------------------------
            # DISPLAY CAMERA
            # --------------------------------------------------

            camera.show_frame(
                frame
            )

            # --------------------------------------------------
            # KEYBOARD INPUT
            # --------------------------------------------------

            key = cv2.waitKey(1) & 0xFF

            # --------------------------------------------------
            # Q -> QUIT
            # --------------------------------------------------

            if key == ord("q"):

                break

        # --------------------------------------------------
        # STOP CAMERA
        # --------------------------------------------------

        camera.stop()

        print(
            "\nRecognition Stopped"
        )

