from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import cv2
import base64
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from db import *
from core import *

app = FastAPI(title="aaaa")

# Add CORS Middleware to allow requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this to specific domains in production for security.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.mount("/images", StaticFiles(directory="images"), name="images")


class Image(BaseModel):
    frame_data: str


@app.get("/{user_id}/outfit_of_the_day")
def outfit_of_the_day(user_id: str, reload: bool):
    pass


@app.get("/{user_id}/garderobe")
def get_garderobe(user_id: str) -> dict[int, str]:
    clothes = server.db.get_garderobe(user_id)
    return {item.id: f"{item.image_path}" for item in clothes}
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


@app.post("/{user_id}/image")
async def upload_file(user_id: str, file: UploadFile = File(...)):
    print("BBBBBBBBB")
    user_images_path = f"./users/{user_id}/images"
    os.makedirs(user_images_path, exist_ok=True)
    try:
        content = await file.read()
        server.new_clothing_from_image(user_id, content)
        return JSONResponse(
            content={"message": "File uploaded successfully"}, status_code=200
        )
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)



class Server:
    def __init__(self):
        self.db = DataBase()
        self.identifier = ClothingIdentifier()
    
    def new_clothing_from_image(self, user_id: str, image: bytes) -> None:
        image_path = self.db.complete_image_path(Clothing.next_image_path())
        self.db.store_image_from_bytes(image, image_path)
        item = self.identifier.process(image_path)
        self.db.add_clothing(user_id, item)

    def outfit_recommendation(self, user_id: str) -> list[Clothing]:
        return outfit_recommendation(self.db.get_garderobe(user_id))


server = Server()


# if __name__ == "__main__":
#     with open("temp/jacket.jpg", "rb") as f:
#         a = f.read()
#     server.new_clothing_from_image("sloan", a)
#     outfit = server.outfit_recommendation("sloan")
#     print("Recommended outfit: ")
#     for i, x in enumerate(outfit):
#         print(f"{i}.", x)
