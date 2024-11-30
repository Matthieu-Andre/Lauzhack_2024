from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import cv2
import base64
import numpy as np
from db import DataBase

app = FastAPI(title="aaaa")


class Image(BaseModel):
    frame_data: str


@app.post("/{user_id}/image}")
def hello(user_id: str, image: Image):
    decoded_bytes = base64.b64decode(image.frame_data)
    # Convert bytes to a numpy array
    np_array = np.frombuffer(decoded_bytes, np.uint8)
    # Decode the numpy array back to an image
    decoded_image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    server.db.store_image(decoded_image, f"{user_id}_test.jpg")
    return "image saved"


class Server:
    def __init__(self):
        self.db = DataBase()


server = Server()
