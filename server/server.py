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
    allow_origins=[
        "*"
    ],  # Allows all origins, use specific IPs/domains if needed for security
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)


app.mount("/images", StaticFiles(directory="images"), name="images")


class Image(BaseModel):
    frame_data: str


@app.get("/users")
def users():
    return server.db.user_list()


@app.get("/{user_id}/outfit_of_the_day")
def outfit_of_the_day(user_id: str, reload: bool = False) -> list[tuple[int, str]]:
    if server.db.has_outfit_of_the_day(user_id) and reload == False:
        outfit = server.db.get_outfit_of_the_day(user_id)
    else:
        outfit = server.outfit_recommendation(user_id)

    return [(item.id, item.image_path) for item in outfit]


@app.post("/{user_id}/outfit_of_the_day/confirm")
def outfit_of_the_day_confirm(user_id: str, item_list: list[int]):
    outfit = [server.db.get_item(user_id, item_id) for item_id in item_list]
    server.db.set_outfit_of_the_day(user_id, outfit)


@app.get("/{user_id}/garderobe")
def get_garderobe(user_id: str) -> list[str]:
    clothes = server.db.get_garderobe(user_id)
    return [f"{item.image_path}" for item in clothes]


# @app.get("/{user_id}/garderobe/{clothing_id}")
# def get_garderobe_item(user_id: str, clothing_id: int) -> dict[int, str]:
#     item = server.db.get_item(user_id, clothing_id)
#     return {item.id: item.get_encoded_image()}


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

    def new_clothing_from_path(self, user_id: str, image_path: str) -> None:
        with open(image_path, "rb") as f:
            a = f.read()
        self.new_clothing_from_image(user_id, a)

    def outfit_recommendation(self, user_id: str) -> list[Clothing]:
        return outfit_recommendation(self.db.get_garderobe(user_id))


server = Server()


if __name__ == "__main__":
    # for x in ["crocs.jpg", "green_tshirt.jpg", "hat.jpg", "jacket.jpg", "jeans.jpg", "pants.jpg", "skirt.jpg", "thongs.jpg", "white_tshirt.jpg", "woman.jpg"]:
    #     server.new_clothing_from_path("sloan", os.path.join("temp/", x))

    outfit = server.outfit_recommendation("sloan")

    print("Recommended outfit:")
    for rec in outfit:
        print(
            f"{rec.descriptor} ({rec.category}, {rec.color}, {rec.weather_compatibilities})"
        )
