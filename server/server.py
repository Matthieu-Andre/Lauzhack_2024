from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import cv2
import base64
import numpy as np
from db import DataBase

app = FastAPI(title="aaaa")


class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None


class Server:
    def __init__(self):
        self.db = DataBase()

    @app.post("/image")
    def hello(self, frame_data: str):
        decoded_bytes = base64.b64decode(frame_data)
        # Convert bytes to a numpy array
        np_array = np.frombuffer(decoded_bytes, np.uint8)
        # Decode the numpy array back to an image
        decoded_image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        self.db.store_image(decoded_image, "test.jpg")
        return "image saved"
