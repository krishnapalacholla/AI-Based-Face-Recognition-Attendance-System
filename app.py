from registration.register_user import register_user
from recognition.face_encoder import FaceEncoder
from recognition.face_recognizer import FaceRecognizer
from attendance.attendance_manager import AttendanceManager


def display_menu():
    """
    Display the application menu.
    """

    print("\n")
    print("=" * 45)
    print(" Face Recognition Attendance System")
    print("=" * 45)

    print("1. Register User")
    print("2. Generate Embeddings")
    print("3. Start Attendance")
    print("4. View Attendance")
    print("5. Export Attendance to Excel")
    print("6. Exit")


def main():
    """
    Main application function.
    """

    while True:

        # -------------------------
        # Display Menu
        # -------------------------
        display_menu()

        # -------------------------
        # Get User Choice
        # -------------------------
        choice = input(
            "\nEnter your choice: "
        ).strip()

        # -------------------------
        # REGISTER USER
        # -------------------------
        if choice == "1":

            register_user()

        # -------------------------
        # GENERATE EMBEDDINGS
        # -------------------------
        elif choice == "2":

            encoder = FaceEncoder()

            encoder.generate_embeddings()

        # -------------------------
        # START ATTENDANCE
        # -------------------------
        elif choice == "3":

            recognizer = FaceRecognizer()

            recognizer.start()

        # -------------------------
        # VIEW ATTENDANCE
        # -------------------------
        elif choice == "4":

            attendance_manager = (
                AttendanceManager()
            )

            attendance_manager.view_attendance()

        # -------------------------
        # EXPORT TO EXCEL
        # -------------------------
        elif choice == "5":

            attendance_manager = (
                AttendanceManager()
            )

            attendance_manager.export_to_excel()

        # -------------------------
        # EXIT
        # -------------------------
        elif choice == "6":

            print(
                "\nExiting Face Recognition "
                "Attendance System."
            )

            break

        # -------------------------
        # INVALID CHOICE
        # -------------------------
        else:

            print(
                "\nInvalid choice. "
                "Please enter a number "
                "between 1 and 6."
            )


if __name__ == "__main__":
    main()