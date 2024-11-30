from enum import Enum
from datetime import datetime
import cv2


class ClothingCategory(Enum):
    TOP = 0
    BOTTOM = 1
    SHOES = 2


class Color(Enum):
    UNKNOWN = -1
    RED = 0
    GREEN = 1
    BLUE = 2


class Clothing:
    _CLOTHES_COUNT = 0
    
    @classmethod
    def generate_id(cls) -> int:
        cls._CLOTHES_COUNT += 1
        return cls._CLOTHES_COUNT - 1
        
    def __init__(self, category: ClothingCategory, color: Color = Color.UNKNOWN, last_used_date: datetime = None, image_path: str = ""):
        if last_used_date is None:
            last_used_date = datetime.now()
        self.category = category
        self.color = color
        self.last_used_date = last_used_date
        self._image_path = image_path
        self._id = Clothing.generate_id()
    
    def has_image(self) -> bool:
        return bool(self._image_path)
    
    @property
    def image_path(self) -> str:
        if not self.has_image():
            raise RuntimeError("the clothing does not provide an image")
        return self._image_path
    
    def get_image(self) -> cv2.typing.MatLike:
        return cv2.imread(self.image_path)
