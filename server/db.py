import os
import cv2


def create_directory(path: str) -> None:
    """
    Create a directory if it doesn't exist.
    """
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except Exception as e:
        print(f"An error occurred: {e}")


class DataBase:
    def __init__(self, *, images_path: str = "images/"):
        create_directory(images_path)
        self.images_path = images_path
    
    def store_image(self, image: cv2.typing.MatLike, id: str) -> None:
        success = cv2.imwrite(os.path.join(self.images_path, id), image)
        if not success:
            print("Failed to save image")
