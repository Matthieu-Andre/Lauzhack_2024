###Code grouping functions to characterize clothing, recommand clothing and wrap clothes on body image

from openai import OpenAI
import base64
import json
from db import *



def create_recommendation(items: list[Clothing]) -> list[Clothing]:
    # TODO Sloan
    raise NotImplementedError




class ClothingIdentifier:
    def __init__(self):  
        # Load API key from JSON file
        with open("apikey.json", "r") as config_file:
            config = json.load(config_file)
            api_key = config["openai_api_key"]

        self.client = OpenAI(api_key=api_key)
        # Pre-prompt so that we get exactly what we want in the format we want
        self.pre_prompt = "Analyze the following image and provide the response in this strict format: object name, category, dominant color, [weather suitability]. Categories: footwear, lower_body_clothing, upper_body_clothing, over_upper_body_clothing. Colors: Red, Blue, Green, Yellow, Purple, Orange, Brown, White, Black, Grey, Pink. Weather suitability: hot, cold, rain, wind, or a combination (e.g., [hot, rain])."

    #Function to analyze an image using OpenAI Vision API
    #Returns object name, category, dominant color, [weather suitability]
    def analyze_image(self, image_path):
        try:
            # Read the image file and encode it in base64
            with open(image_path, "rb") as img_file:
                img_b64_str = base64.b64encode(img_file.read()).decode("utf-8")
            
            # Prepare the data URI
            img_type = "image/jpeg"  # Update if using a different image format
            data_uri = f"data:{img_type};base64,{img_b64_str}"

            # Use Vision API to analyze the image
            response = self.client.chat.completions.create(
                model="gpt-4o-2024-08-06",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": self.pre_prompt},
                            {"type": "image_url", "image_url": {"url": data_uri}},
                        ],
                    }
                ],
            )

            # Extract and return the result
            guess = response.choices[0].message.content
            return image_path, {"guess": guess}

        except Exception as e:
            return {"error": str(e)}
    

    #Function to convert openAI garbage output to usable list
    #Returns a list like: ['cap', 'upper_body_clothing', 'Black', ('hot', 'wind')]    
    def parse_output_to_list(self, image_path: str, guess):
        try:
            print("aaa1")
            # Extract the actual string from the dictionary
            guess_string = guess.get("guess", "")
            if not guess_string:
                raise ValueError("The 'guess' key is missing or empty.")

            print("aaa2")
            # Split the string by the first square bracket to isolate weather suitability
            parts = guess_string.split("[", 1)
            before_bracket = parts[0].strip()  # Part before the square bracket
            within_bracket = parts[1].rstrip("]").strip() if len(parts) > 1 else ""  # Content within the square bracket

            print("aaa3")
            # Split the part before the square bracket by commas
            result = [item.strip() for item in before_bracket.split(",") if item.strip()]

            print("aaa4")
            # Parse the weather suitability as a tuple
            weather_suitability = tuple(item.strip() for item in within_bracket.split(",") if item.strip())
            result.append(weather_suitability)
            data: tuple[str, str, str, tuple[str]] = tuple(result)

            print("aaa5")
            print(data)
            descriptor = data[0]
            category_map = {
                "footwear": "SHOES",
                "lower_body_clothing": "BOTTOM",
                "upper_body_clothing": "TOP",
                "over_upper_body_clothing": "OVER_TOP"
            }
            print("aaa6")
            category = ClothingCategory.from_name(category_map[data[1]], default=ClothingCategory.UNKNOWN)
            print("aaa7")
            color = Color.from_name(data[2].upper(), default=Color.UNKNOWN)
            print("aaa8")
            weather_compatibilities = list(filter(bool, map(lambda w: Weather.from_name(w.upper(), default=None), data[3])))
            
            print("aaa9")
            return Clothing(
                descriptor=descriptor,
                category=category,
                color=color,
                weather_compatibilities=weather_compatibilities,
                image_path=image_path
            )
        
        except Exception as e:
            raise
            print(f"got error: {e}")
            return Clothing(image_path=image_path)
            raise ValueError(f"Failed to parse the output: {e}")
        
    def process(self, image_path: str) -> Clothing:
        return self.parse_output_to_list(
            *self.analyze_image(image_path)
        )


if __name__ == "__main__":
    image_path = "MyCode/casquette.jpg"
    identifier = ClothingIdentifier()
    result = identifier.analyze_image(image_path)
    parsed_result = identifier.parse_output_to_list(result)
    print(parsed_result)
