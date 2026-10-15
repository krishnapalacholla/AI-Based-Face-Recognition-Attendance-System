from pathlib import Path
import pickle

import cv2

from recognition.face_detector import FaceDetector


class FaceEncoder:
    """
    Generate face embeddings for all registered users.
    """

    def __init__(self):

        # -------------------------
        # Load Face Detector
        # -------------------------
        self.detector = FaceDetector()

    # --------------------------------------------------
    # GENERATE EMBEDDINGS
    # --------------------------------------------------

    def generate_embeddings(self):
        """
        Generate and save face embeddings
        for all valid registered users.
        """

        # -------------------------
        # Dataset Path
        # -------------------------
        dataset_path = Path("dataset")

        # -------------------------
        # Check Dataset
        # -------------------------
        if not dataset_path.exists():

            print(
                "Dataset folder not found."
            )

            return

        # -------------------------
        # Embeddings Dictionary
        # -------------------------
        embeddings = {}

        print(
            "\nGenerating Face Embeddings...\n"
        )

        # -------------------------
        # Loop Through Users
        # -------------------------
        for user_folder in dataset_path.iterdir():

            if not user_folder.is_dir():

                continue

            user_name = user_folder.name

            print(
                f"Processing {user_name}..."
            )

            # -------------------------
            # User Embeddings
            # -------------------------
            user_embeddings = []

            # -------------------------
            # Read User Images
            # -------------------------
            image_paths = list(
                user_folder.glob("*.jpg")
            )

            if len(image_paths) == 0:

                print(
                    f"No images found for "
                    f"{user_name}."
                )

                print(
                    f"Skipping {user_name}.\n"
                )

                continue

            # -------------------------
            # Process Images
            # -------------------------
            for image_path in image_paths:

                image = cv2.imread(
                    str(image_path)
                )

                # -------------------------
                # Invalid Image
                # -------------------------
                if image is None:

                    print(
                        f"{image_path.name} "
                        f"-> Invalid image"
                    )

                    continue

                # -------------------------
                # Detect Faces
                # -------------------------
                faces = (
                    self.detector.detect_faces(
                        image
                    )
                )

                print(
                    f"{image_path.name} "
                    f"-> Faces detected: "
                    f"{len(faces)}"
                )

                # -------------------------
                # No Face
                # -------------------------
                if len(faces) == 0:

                    continue

                # -------------------------
                # Get First Face
                # -------------------------
                face = faces[0]

                # -------------------------
                # Check Embedding
                # -------------------------
                if face.embedding is None:

                    continue

                # -------------------------
                # Store Embedding
                # -------------------------
                user_embeddings.append(
                    face.embedding
                )

            # -------------------------
            # Validate User Embeddings
            # -------------------------
            if len(user_embeddings) == 0:

                print(
                    f"No valid face embeddings "
                    f"generated for {user_name}."
                )

                print(
                    f"Skipping {user_name}.\n"
                )

                continue

            # -------------------------
            # Add Valid User
            # -------------------------
            embeddings[user_name] = (
                user_embeddings
            )

            print(
                f"{len(user_embeddings)} "
                f"embeddings generated "
                f"for {user_name}.\n"
            )

        # -------------------------
        # Output Folder
        # -------------------------
        output_folder = Path(
            "embeddings"
        )

        output_folder.mkdir(
            exist_ok=True
        )

        # -------------------------
        # Output Path
        # -------------------------
        output_path = (
            output_folder
            / "embeddings.pkl"
        )

        # -------------------------
        # Save Embeddings
        # -------------------------
        with open(
            output_path,
            "wb"
        ) as file:

            pickle.dump(
                embeddings,
                file
            )

        # -------------------------
        # Completion Output
        # -------------------------
        print(
            "=" * 50
        )

        print(
            "Embeddings saved successfully."
        )

        print(
            f"Valid registered users: "
            f"{len(embeddings)}"
        )

        print(
            "=" * 50
        )