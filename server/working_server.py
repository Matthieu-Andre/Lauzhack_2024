from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
import cv2
import base64
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import base64
from db import DataBase
import shutil

app = FastAPI(title="aaaa")


# Add CORS Middleware to allow requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this to specific domains in production for security.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Image(BaseModel):
    frame_data: str


# @app.post("/{user_id}/image}")
# def hello(user_id: str, image: Image):
#     decoded_bytes = base64.b64decode(image.frame_data)
#     # Convert bytes to a numpy array
#     np_array = np.frombuffer(decoded_bytes, np.uint8)
#     # Decode the numpy array back to an image
#     decoded_image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
#     server.db.store_image(decoded_image, f"{user_id}_test.jpg")
#     return "image saved"


class Server:
    def __init__(self):
        self.db = DataBase()


server = Server()


@app.get("/")
def hello():
    return "Hello Clothes!"


# @app.post("/upload-photo/")
@app.post("/{user_id}/image")
async def upload_file(user_id: str, file: UploadFile = File(...)):
    user_images_path = f"./users/{user_id}/images"
    os.makedirs(user_images_path, exist_ok=True)
    try:
        # Read the uploaded file
        content = await file.read()

        # Save the file (optional)
        with open(
            os.path.join(user_images_path, f"uploaded_{file.filename}"), "wb"
        ) as f:
            f.write(content)

        return JSONResponse(
            content={"message": "File uploaded successfully"}, status_code=200
        )
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
