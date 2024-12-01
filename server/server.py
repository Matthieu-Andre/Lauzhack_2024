from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import cv2
import base64
import numpy as np
from db import *

app = FastAPI(title="aaaa")


class Image(BaseModel):
    frame_data: str


@app.get("/{user_id}/outfit_of_the_day")
def outfit_of_the_day(user_id: str, reload: bool):
    pass


@app.get("/{user_id}/garderobe")
def get_garderobe(user_id: str) -> dict[int, str]:
    clothes = server.db.get_garderobe(user_id)
    return {item.id: item.get_encoded_image() for item in clothes}


@app.get("/{user_id}/garderobe/{clothing_id}")
def get_garderobe_item(user_id: str, clothing_id: int) -> dict[int, str]:
    item = server.db.get_item(user_id, clothing_id)
    return {item.id: item.get_encoded_image()}


@app.post("/{user_id}/garderobe")
def image(user_id: str, image: Image):
    decoded_bytes = base64.b64decode(image.frame_data)
    # Convert bytes to a numpy array
    np_array = np.frombuffer(decoded_bytes, np.uint8)
    # Decode the numpy array back to an image
    decoded_image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    server.new_clothing_from_image(decoded_image, f"{user_id}_test.jpg")
    return "image saved"


class Server:
    def __init__(self):
        self.db = DataBase()
    
    def new_clothing_from_image(self, user_id: str, image: cv2.typing.MatLike) -> None:
        item = Clothing()
        self.db.store_image(image, item.image_path)
        self.db.add_clothing(user_id, item)


server = Server()
