import cv2


class Camera:
    """
    Handles webcam operations.

    """
    

    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None
        
    def get_camera(self):
        """
        Return the OpenCV VideoCapture object.
        """
        return self.cap

    def start(self):
        """
        Open the webcam.
        """
        self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap.isOpened():
            raise Exception("Unable to open webcam.")

        print("[OK] Camera Started")

    def read_frame(self):
        """
        Read a frame from the webcam.
        """
        success, frame = self.cap.read()

        if not success:
            return None

        return frame

    def show_frame(self, frame):
        """
        Display the frame.
        """
        cv2.imshow("Face Recognition Attendance System", frame)

    def stop(self):
        """
        Release camera resources.
        """
        if self.cap:
            self.cap.release()

        cv2.destroyAllWindows()
    


def main():

    camera = Camera()

    camera.start()

    while True:

        frame = camera.read_frame()

        if frame is None:
            print("Failed to capture frame.")
            break

        camera.show_frame(frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    camera.stop()


if __name__ == "__main__":
    main()