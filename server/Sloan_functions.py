###Code grouping functions to characterize clothing, recommand clothing and wrap clothes on body image

#pip install openai
from openai import OpenAI
#We technically can't send image, we first convert them to base64 to bypass that
import base64
#json to import the key from another json file so that it is more secure you know
import json

# Load API key from JSON file
with open("MyCode/apikey.json", "r") as config_file:
    config = json.load(config_file)
    api_key = config["openai_api_key"]

client = OpenAI(api_key=api_key)
 # Pre-prompt so that we get exactly what we want in the format we want
pre_prompt = "Analyze the following image and provide the response in this strict format: object name, category, dominant color, [weather suitability]. Categories: footwear, lower_body_clothing, upper_body_clothing_, over_upper_body_clothing. Colors: Red, Blue, Green, Yellow, Purple, Orange, Brown, White, Black, Grey, Pink. Weather suitability: hot, cold, rain, wind, or a combination (e.g., [hot, rain])."

#Function to analyze an image using OpenAI Vision API
#Returns object name, category, dominant color, [weather suitability]
def analyze_image(image_path):
    try:
        # Read the image file and encode it in base64
        with open(image_path, "rb") as img_file:
            img_b64_str = base64.b64encode(img_file.read()).decode("utf-8")
        
        # Prepare the data URI
        img_type = "image/jpeg"  # Update if using a different image format
        data_uri = f"data:{img_type};base64,{img_b64_str}"

        # Use Vision API to analyze the image
        response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": pre_prompt},
                        {"type": "image_url", "image_url": {"url": data_uri}},
                    ],
                }
            ],
        )

        # Extract and return the result
        guess = response.choices[0].message.content
        return {"guess": guess}

    except Exception as e:
        return {"error": str(e)}
    

#Function to convert openAI garbage output to usable list
#Returns a list like: ['cap', 'upper_body_clothing', 'Black', ('hot', 'wind')]    
def parse_output_to_list(guess):
    try:
        # Extract the actual string from the dictionary
        guess_string = guess.get("guess", "")
        if not guess_string:
            raise ValueError("The 'guess' key is missing or empty.")

        # Split the string by the first square bracket to isolate weather suitability
        parts = guess_string.split("[", 1)
        before_bracket = parts[0].strip()  # Part before the square bracket
        within_bracket = parts[1].rstrip("]").strip() if len(parts) > 1 else ""  # Content within the square bracket

        # Split the part before the square bracket by commas
        result = [item.strip() for item in before_bracket.split(",") if item.strip()]

        # Parse the weather suitability as a tuple
        weather_suitability = tuple(item.strip() for item in within_bracket.split(",") if item.strip())
        result.append(weather_suitability)

        return result
    except Exception as e:
        raise ValueError(f"Failed to parse the output: {e}")

# # To test alone
# if __name__ == "__main__":
#     image_path = "MyCode/casquette.jpg"
#     result = analyze_image(image_path)
#     parsed_result = parse_output_to_list(result)
#     print(parsed_result)





