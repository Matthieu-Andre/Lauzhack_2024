from __future__ import annotations
import os
import cv2
import sqlite3
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json
from clothing import *


# Define the base class for all models
Base = declarative_base()


class SQLUser(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)  # user_id as primary key
    clothes = Column(String)  # Store serialized list as string

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_clothes()
    
    def _init_clothes(self) -> None:
        self._set_clothes([])
        
    def _set_clothes(self, clothes: list[int]) -> None:
        self.clothes = json.dumps(clothes)  # Convert list to JSON string

    def get_clothes(self) -> list[int]:
        return json.loads(self.clothes) if self.clothes else []
    
    def clothes_append(self, item: Clothing) -> None:
        clothes = self.get_clothes()
        clothes.append(item.id)
        self._set_clothes(clothes)
    
    
    
class SQLClothing(Base):
    __tablename__ = "clothes"
    
    id = Column(Integer, primary_key=True)
    descriptor = Column(String)
    category = Column(Integer)
    color = Column(Integer)
    weather_compatibilities = Column(str)
    last_used_date = Column(String)
    image_path = Column(String)
    
    @classmethod
    def from_python(cls, clothing: Clothing) -> SQLClothing:
        return cls(
            id=clothing.id,
            descriptor=clothing.descriptor,
            category=clothing.category.name,
            color=clothing.color.name,
            weather_compatibilities=json.dumps([comp.name for comp in clothing.weather_compatibilities]),
            last_used_date=str(clothing.last_used_date),
            image_path=clothing.image_path
        )
    
    def to_python(self) -> Clothing:
        return Clothing(
            category=ClothingCategory.from_name(self.category),
            descriptor=self.descriptor,
            color=Color.from_name(self.color),
            weather_compatibilities=list(map(Weather.from_name, json.loads(self.weather_compatibilities))),
            last_used_date=datetime.fromisoformat(self.last_used_date),
            image_path=self.image_path
        )


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
    def __init__(self, *, name: str = "wearit.db", images_path: str = "images/"):
        self.name = name
        create_directory(images_path)
        self.images_path = images_path

        self.engine = create_engine("sqlite:///" + name, echo=True)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        # TODO: call self.session.close() somewhere
    
    def commit(self) -> None:
        self.session.commit()

    def add_user(self, id: str) -> None:
        user = SQLUser(id=id, clothes="[]")
        self.session.add(user)
        self.commit()
    
    def user_id_exists(self, id: str) -> bool:
        result = self.session.query(SQLUser).filter_by(id=id).first()
        return result is not None
    
    def ensure_user_exists(self, id: str) -> None:
        if not self.user_id_exists(id):
            self.add_user(id)
    
    def get_user(self, id: str) -> SQLUser:
        self.ensure_user_exists(id)
        return self.session.query(SQLUser).filter_by(id=id).first()
    
    def add_clothing(self, user_id: str, item: Clothing) -> None:
        self.store_image(item.image_path)
        user = self.get_user(user_id)
        self.session.add(SQLClothing.from_python(item))
        user.clothes_append(item)
        self.commit()
    
    def get_garderobe(self, user_id: str) -> list[Clothing]:
        user = self.get_user(user_id)
        clothe_ids = user.get_clothes()
        clothes = self.session.query(SQLClothing).filter(SQLClothing.id.in_(clothe_ids)).all()
        return clothes
    
    def store_image(self, image: cv2.typing.MatLike, name: str) -> None:
        success = cv2.imwrite(os.path.join(self.images_path, name), image)
        if not success:
            print("Failed to save image")


