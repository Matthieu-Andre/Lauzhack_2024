import requests

# Replace with your FastAPI server address
API_URL = "http://127.0.0.1:8000/upload-photo/"

# File path to the image you want to test with
FILE_PATH = "./test_image/test.jpg"


def test_upload_photo():
    try:
        # Open the file to be uploaded
        with open(FILE_PATH, "rb") as file:
            # Prepare the file payload
            files = {"file": (FILE_PATH.split("/")[-1], file, "image/jpeg")}

            # Send the request to the backend
            response = requests.post(API_URL, files=files)

            # Print the response from the backend
            if response.status_code == 200:
                print("Test passed: Photo uploaded successfully")
                print("Response:", response.json())
            else:
                print(f"Test failed with status code {response.status_code}")
                print("Response:", response.text)

    except FileNotFoundError:
        print(f"Error: The file '{FILE_PATH}' was not found.")
    except requests.exceptions.RequestException as e:
        print(f"Error: An exception occurred during the request - {str(e)}")


if __name__ == "__main__":
    test_upload_photo()
