from pathlib import Path

import cv2

from camera.camera import Camera
from recognition.face_detector import FaceDetector
from recognition.face_encoder import FaceEncoder
from database.database import get_setting


def register_user(user_name=None):
    """
    Register a user by capturing face images
    and automatically generating embeddings.

    The user name can come from:
    1. Terminal input
    2. GUI input
    """

    # --------------------------------------------------
    # GET USER NAME
    # --------------------------------------------------

    if user_name is None:

        user_name = input(
            "Enter user name: "
        ).strip()

    else:

        user_name = user_name.strip()

    # --------------------------------------------------
    # VALIDATE USER NAME
    # --------------------------------------------------

    if not user_name:

        print(
            "User name cannot be empty."
        )

        return False

    # --------------------------------------------------
    # DATASET FOLDER
    # --------------------------------------------------

    dataset_path = Path(
        "dataset"
    )

    dataset_path.mkdir(
        exist_ok=True
    )

    # --------------------------------------------------
    # USER FOLDER
    # --------------------------------------------------

    user_folder = (
        dataset_path
        / user_name
    )

    # --------------------------------------------------
    # CLEAN OLD USER IMAGES
    # --------------------------------------------------

    if user_folder.exists():

        old_images = list(
            user_folder.glob("*.jpg")
        )

        if len(old_images) > 0:

            print(
                f"\nExisting images found "
                f"for {user_name}."
            )

            print(
                "Removing old face images..."
            )

            for image_path in old_images:

                image_path.unlink()

            print(
                f"{len(old_images)} old images "
                f"removed."
            )

    # --------------------------------------------------
    # CREATE USER FOLDER
    # --------------------------------------------------

    user_folder.mkdir(
        exist_ok=True
    )

    print(
        f"\nUser folder ready: "
        f"{user_folder}"
    )

    # --------------------------------------------------
    # START CAMERA
    # --------------------------------------------------

    camera = Camera()

    try:

        camera.start()

        # --------------------------------------------------
        # LOAD FACE DETECTOR
        # --------------------------------------------------

        detector = FaceDetector()

        # --------------------------------------------------
        # INSTRUCTIONS
        # --------------------------------------------------

        print("\nInstructions:")

        print(
            "SPACE -> Capture Face"
        )

        print(
            "Q     -> Quit"
        )

        print(
            "\nCapture images with slightly "
            "different face angles."
        )

        print(
            "Look straight, left, right, "
            "slightly up and slightly down.\n"
        )

        # --------------------------------------------------
        # IMAGE SETTINGS
        # --------------------------------------------------

        image_count = 0

        maximum_images = int(get_setting("registration_images", "5"))

        # --------------------------------------------------
        # CAMERA LOOP
        # --------------------------------------------------

        while image_count < maximum_images:

            # ----------------------------------------------
            # READ CAMERA FRAME
            # ----------------------------------------------

            frame = camera.read_frame()

            if frame is None:

                print(
                    "Failed to read camera frame."
                )

                break

            # ----------------------------------------------
            # DETECT FACES
            # ----------------------------------------------

            faces = detector.detect_faces(
                frame
            )

            # ----------------------------------------------
            # DRAW FACE BOXES
            # ----------------------------------------------

            for face in faces:

                x1, y1, x2, y2 = map(
                    int,
                    face.bbox
                )

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (
                        0,
                        255,
                        0
                    ),
                    2
                )

            # ----------------------------------------------
            # DISPLAY CAPTURE COUNT
            # ----------------------------------------------

            cv2.putText(
                frame,
                (
                    f"Captured: "
                    f"{image_count}/"
                    f"{maximum_images}"
                ),
                (
                    20,
                    40
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (
                    0,
                    255,
                    0
                ),
                2
            )

            # ----------------------------------------------
            # DISPLAY INSTRUCTIONS
            # ----------------------------------------------

            cv2.putText(
                frame,
                "SPACE: Capture | Q: Quit",
                (
                    20,
                    75
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (
                    255,
                    255,
                    255
                ),
                2
            )

            # ----------------------------------------------
            # SHOW CAMERA
            # ----------------------------------------------

            camera.show_frame(
                frame
            )

            # ----------------------------------------------
            # KEYBOARD INPUT
            # ----------------------------------------------

            key = cv2.waitKey(1) & 0xFF

            # ==============================================
            # SPACE -> CAPTURE FACE
            # ==============================================

            if key == ord(" "):

                # ------------------------------------------
                # NO FACE
                # ------------------------------------------

                if len(faces) == 0:

                    print(
                        "No face detected. "
                        "Try again."
                    )

                    continue

                # ------------------------------------------
                # MULTIPLE FACES
                # ------------------------------------------

                if len(faces) > 1:

                    print(
                        "Multiple faces detected. "
                        "Only one person should "
                        "be visible."
                    )

                    continue

                # ------------------------------------------
                # GET DETECTED FACE
                # ------------------------------------------

                face = faces[0]

                x1, y1, x2, y2 = map(
                    int,
                    face.bbox
                )

                # ------------------------------------------
                # FRAME SIZE
                # ------------------------------------------

                frame_height = frame.shape[0]

                frame_width = frame.shape[1]

                # ------------------------------------------
                # FACE SIZE
                # ------------------------------------------

                face_width = x2 - x1

                face_height = y2 - y1

                # ------------------------------------------
                # ADD PADDING
                # ------------------------------------------

                padding_x = int(
                    face_width * 0.5
                )

                padding_y = int(
                    face_height * 0.5
                )

                # ------------------------------------------
                # PADDED COORDINATES
                # ------------------------------------------

                crop_x1 = max(
                    0,
                    x1 - padding_x
                )

                crop_y1 = max(
                    0,
                    y1 - padding_y
                )

                crop_x2 = min(
                    frame_width,
                    x2 + padding_x
                )

                crop_y2 = min(
                    frame_height,
                    y2 + padding_y
                )

                # ------------------------------------------
                # CROP FACE REGION
                # ------------------------------------------

                face_image = frame[
                    crop_y1:crop_y2,
                    crop_x1:crop_x2
                ]

                # ------------------------------------------
                # VALIDATE FACE IMAGE
                # ------------------------------------------

                if face_image.size == 0:

                    print(
                        "Invalid face image. "
                        "Try again."
                    )

                    continue

                # ------------------------------------------
                # IMAGE NUMBER
                # ------------------------------------------

                image_count += 1

                # ------------------------------------------
                # IMAGE PATH
                # ------------------------------------------

                image_path = (
                    user_folder
                    / (
                        f"img_"
                        f"{image_count:03}.jpg"
                    )
                )

                # ------------------------------------------
                # SAVE IMAGE
                # ------------------------------------------

                saved = cv2.imwrite(
                    str(image_path),
                    face_image
                )

                if saved:

                    print(
                        f"Captured Image "
                        f"{image_count}"
                    )

                else:

                    image_count -= 1

                    print(
                        "Failed to save image."
                    )

            # ==============================================
            # Q -> QUIT
            # ==============================================

            elif key == ord("q"):

                break

    finally:

        # --------------------------------------------------
        # ALWAYS RELEASE CAMERA
        # --------------------------------------------------

        camera.stop()

    # --------------------------------------------------
    # CHECK REGISTRATION
    # --------------------------------------------------

    if image_count == 0:

        print(
            "\nRegistration cancelled."
        )

        return False

    # --------------------------------------------------
    # REGISTRATION COMPLETED
    # --------------------------------------------------

    print(
        "\nRegistration Completed."
    )

    print(
        f"{image_count} face images "
        f"captured for {user_name}."
    )

    # --------------------------------------------------
    # AUTOMATIC EMBEDDING GENERATION
    # --------------------------------------------------

    print(
        "\nAutomatically generating "
        "face embeddings..."
    )

    encoder = FaceEncoder()

    encoder.generate_embeddings()

    # --------------------------------------------------
    # READY MESSAGE
    # --------------------------------------------------

    print(
        f"\nUser '{user_name}' is ready "
        f"for face recognition."
    )

    return True


if __name__ == "__main__":

    register_user()