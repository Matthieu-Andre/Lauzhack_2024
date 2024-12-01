from __future__ import annotations
from enum import Enum
from datetime import datetime
import cv2
import base64


class EnumPlus(Enum):
    def from_name(self, name: str) -> EnumPlus:
        return EnumPlus.__members__[name]


class ClothingCategory(EnumPlus):
    UNKNOWN = -1
    TOP = 0
    BOTTOM = 1
    SHOES = 2


class Color(EnumPlus):
    UNKNOWN = -1
    BLACK = 0
    BLUE = 1
    BROWN = 2
    GRAY = 3
    GREEN = 4
    ORANGE = 5
    PINK = 6
    PURPLE = 7
    RED = 8
    WHITE = 9
    YELLOW = 10


class Weather(EnumPlus):
    HOT = 0
    COLD = 1
    RAIN = 2
    WIND = 3

    
class Clothing:
    _CLOTHES_COUNT = 0
    
    @classmethod
    def generate_id(cls) -> int:
        cls._CLOTHES_COUNT += 1
        return cls._CLOTHES_COUNT - 1
        
    def __init__(self,
                 descriptor: str = "",
                 category: ClothingCategory = ClothingCategory.UNKNOWN,
                 color: Color = Color.UNKNOWN,
                 weather_compatibilities: list[Weather] = None,
                 last_used_date: datetime = None,
                 image_path: str = None
        ):
        
        self._id = Clothing.generate_id()
        if weather_compatibilities is None:
            weather_compatibilities = []
        if last_used_date is None:
            last_used_date = datetime.now()
        if image_path is None:
            image_path = f"item{self._id}.jpg"
            
        self.descriptor = descriptor
        self.category = category
        self.color = color
        self.weather_compatibilities = weather_compatibilities
        self.last_used_date = last_used_date
        self._image_path = image_path
    
    @property
    def id(self) -> int:
        return self._id
    
    def has_image(self) -> bool:
        return bool(self._image_path)
    
    def set_image_path(self, path: str) -> None:
        self._image_path = path
    
    @property
    def image_path(self) -> str:
        if not self.has_image():
            raise RuntimeError("the clothing does not provide an image")
        return self._image_path
    
    def get_image(self) -> cv2.typing.MatLike:
        return cv2.imread(self.image_path)
    
    def get_encoded_image(self) -> str:
        _, buffer = cv2.imencode('.jpg', self.get_image())
        # Convert to base64 string
        image_data = base64.b64encode(buffer).decode('utf-8')
        return image_data
