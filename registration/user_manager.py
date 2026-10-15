"""
user_manager.py

Manages registered users in the Face Recognition
Attendance System.

Responsibilities:
  - List all registered users (by scanning /dataset)
  - Delete a user (removes dataset folder + rebuilds embeddings)
  - Check if a user exists
"""

import shutil
from pathlib import Path
from typing import List


DATASET_FOLDER   = Path("dataset")
EMBEDDINGS_FILE  = Path("embeddings") / "embeddings.pkl"


class UserManager:
    """
    Provides CRUD-like operations over registered users.
    Users are identified by their name (= folder name
    inside /dataset).
    """

    # --------------------------------------------------
    # LIST USERS
    # --------------------------------------------------

    def list_users(self) -> List[str]:
        """
        Return a sorted list of registered user names.
        Only users who have at least one .jpg image in
        their dataset folder are included.
        """
        if not DATASET_FOLDER.exists():
            return []

        users = []
        for folder in DATASET_FOLDER.iterdir():
            if not folder.is_dir():
                continue
            if list(folder.glob("*.jpg")):
                users.append(folder.name)

        return sorted(users)

    # --------------------------------------------------
    # USER EXISTS
    # --------------------------------------------------

    def user_exists(self, user_name: str) -> bool:
        """Return True if the user has registered images."""
        user_folder = DATASET_FOLDER / user_name
        if not user_folder.exists():
            return False
        return bool(list(user_folder.glob("*.jpg")))

    # --------------------------------------------------
    # GET IMAGE COUNT
    # --------------------------------------------------

    def get_image_count(self, user_name: str) -> int:
        """Return the number of captured face images."""
        user_folder = DATASET_FOLDER / user_name
        if not user_folder.exists():
            return 0
        return len(list(user_folder.glob("*.jpg")))

    # --------------------------------------------------
    # DELETE USER
    # --------------------------------------------------

    def delete_user(self, user_name: str) -> bool:
        """
        Remove the user's dataset folder and
        regenerate embeddings without this user.

        Returns True on success, False if the user
        was not found.
        """
        user_folder = DATASET_FOLDER / user_name

        if not user_folder.exists():
            print(f"User '{user_name}' not found.")
            return False

        # Remove dataset folder
        shutil.rmtree(str(user_folder), ignore_errors=True)

        print(f"User '{user_name}' deleted from dataset.")

        # Regenerate embeddings
        self._rebuild_embeddings()

        return True

    # --------------------------------------------------
    # REBUILD EMBEDDINGS
    # --------------------------------------------------

    def _rebuild_embeddings(self):
        """
        Regenerate the embeddings.pkl after a user
        has been deleted or added.
        """
        try:
            from recognition.face_encoder import FaceEncoder
            encoder = FaceEncoder()
            encoder.generate_embeddings()
            print("Embeddings rebuilt successfully.")
        except Exception as error:
            print(f"Failed to rebuild embeddings: {error}")

    # --------------------------------------------------
    # TOTAL USERS
    # --------------------------------------------------

    def get_user_count(self) -> int:
        """Return total number of registered users."""
        return len(self.list_users())

    # --------------------------------------------------
    # RENAME USER
    # --------------------------------------------------

    def rename_user(
        self,
        old_name: str,
        new_name: str
    ) -> bool:
        """
        Rename a user's dataset folder and
        rebuild embeddings.

        Returns True on success, False otherwise.
        """
        old_folder = DATASET_FOLDER / old_name
        new_folder = DATASET_FOLDER / new_name

        if not old_folder.exists():
            print(f"User '{old_name}' not found.")
            return False

        if new_folder.exists():
            print(f"User '{new_name}' already exists.")
            return False

        old_folder.rename(new_folder)
        print(f"Renamed '{old_name}' → '{new_name}'.")

        self._rebuild_embeddings()
        return True
