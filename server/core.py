###Code grouping functions to characterize clothing, recommand clothing and wrap clothes on body image

from openai import OpenAI
import base64
import json
from db import *

from meteostat import Stations, Daily
import datetime
import random


class OpenAIClient:
    # Load API key from JSON file
    with open("apikey.json", "r") as config_file:
        config = json.load(config_file)
        api_key = config["openai_api_key"]

    client = OpenAI(api_key=api_key)



class ClothingIdentifier:
    def __init__(self):
        # Pre-prompt so that we get exactly what we want in the format we want
        
        self.pre_prompt = "Analyze the following image and provide the response in this strict format: object name, category, dominant color, [weather suitability]. Categories: footwear, lower_body_clothing, upper_body_clothing_, over_upper_body_clothing. Colors: Red, Blue, Green, Yellow, Purple, Orange, Brown, White, Black, Grey, Pink. Weather suitability: hot, cold, rain, wind, or a combination (e.g., [hot, rain])." "You cannot say that you cannot help, if you do not knwo you have to guess an item that could be realistic."

        # "If the image is too difficult to analyze or there are too much things to describe, please only return a single clothing item with the strict format discussed: object name, category, dominant color, (weather suitabilities)."


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
            response = OpenAIClient.client.chat.completions.create(
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
                seed = 2
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

            # Clean the guess string by removing explicit labels
            cleaned_string = guess_string.replace("Object name:", "").replace("Category:", "").replace("Dominant color:", "").replace("Weather suitability:", "")

            # Initialize variables for result and weather suitability
            result = []
            temp = ""
            found_bracket = False
            must_finalize = True

            # Process the string character by character
            for char in cleaned_string:
                if char == "[":
                    found_bracket = True
                    if temp.strip():
                        result.extend(item.strip() for item in temp.split(",") if item.strip())
                    temp = ""  # Reset temp to start collecting weather suitability
                elif char == "]" and len(result) >= 3:  # Stop if ] is found and at least 4 elements exist
                    if temp.strip():
                        weather_suitability = [item.strip() for item in temp.split(",") if item.strip()]
                        result.append(weather_suitability)
                    must_finalize = False
                    break
                else:
                    temp += char

            if must_finalize:
                # Finalize the parsing if no `]` was encountered
                if temp.strip():
                    result.extend(item.strip() for item in temp.split(",") if item.strip())

            data: tuple[str, str, str, tuple[str]] = tuple(result)
            print("DATA: ", data)
            descriptor = data[0]
            category_map = {
                "footwear": "SHOES",
                "lower_body_clothing": "BOTTOM",
                "upper_body_clothing": "TOP",
                "over_upper_body_clothing": "OVER_TOP"
            }
            category = ClothingCategory.from_name(category_map[data[1]], default=ClothingCategory.UNKNOWN)
            color = Color.from_name(data[2].upper(), default=Color.UNKNOWN)
            weather_compatibilities = list(filter(bool, map(lambda w: Weather.from_name(w.upper(), default=False), data[3])))
            
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



#Function that checks meteo to get booleans such as cold, hot, rain, wind
def get_meteo():
    # Define location and time period
    time = datetime.datetime.now().strftime('%Y-%m-%d')
    location = Stations().nearby(46.5197, 6.6323).fetch(1)  # Lausanne coordinates
    today = datetime.datetime.now()
    data = Daily(location, today - datetime.timedelta(days=1), today)
    data = data.fetch()

    # Extract values for the explicit date (today)
    tavg = data.loc[time, 'tavg'] if time in data.index else None
    prcp = data.loc[time, 'prcp'] if time in data.index else None
    wspd = data.loc[time, 'wspd'] if time in data.index else None

    # Initialize booleans
    cold = False
    hot = False
    rain = False
    wind = False

    # Perform checks
    if tavg is not None:
        if tavg < 15:
            cold = True
        if tavg > 25:
            hot = True

    if prcp is not None and prcp > 0:  # Check for any precipitation
        rain = True

    if wspd is not None and wspd > 5:  # Adjust wind threshold as needed
        wind = True

    # Return weather indicators as a dictionary
    return {
        Weather.COLD: cold,
        Weather.HOT: hot,
        Weather.RAIN: rain,
        Weather.WIND: wind
    }



def outfit_recommendation(items: list[Clothing]) -> list[Clothing]:
    if not items:
        raise ValueError("You are poor")
    weather_conditions = get_meteo()
    initial_item = pick_random_suitable_item(items, weather_conditions)
    outfit = complete_outfit_with_openai(initial_item, items, weather_conditions)
    print(outfit)
    outfit.append(initial_item)
    print(items)
    return outfit


def pick_random_suitable_item(items: list[Clothing], weather_conditions: dict) -> list[Clothing]:
    recommended = []
    # categories = ['footwear', 'lower_body_clothing', 'upper_body_clothing', 'over_upper_body_clothing']
    categories = list(ClothingCategory.__members__.values())

    # Filter items by weather suitability
    suitable_items = [
        item for item in items if any(condition in weather_conditions for condition in item.weather_compatibilities)
    ]

    if not suitable_items:
        return random.choice(items)
        raise ValueError("No suitable items found for the current weather conditions.")

    # Start with a random item
    initial_item = random.choice(suitable_items)
    return initial_item
    recommended.append(initial_item)

    # Complete missing categories
    for category in categories:
        if not any(item.category == category for item in recommended):
            candidates = [
                item for item in suitable_items if item.category == category
            ]
            if candidates:
                recommended.append(random.choice(candidates))  # Pick randomly for now

    if recommended:
        return random.choice(recommended)
    return random.choice(items)
    return [f"{item.descriptor}, {item.category}, {item.color}, suitable for {item.weather_compatibilities}" for item in recommended]


#function that takes list of clothes and an initial item to return recomanded clothes
#return 3 clothes if possible
def complete_outfit_with_openai(
    initial_item: Clothing,
    items: list[Clothing],
    weather_conditions: dict
) -> list[Clothing]:
    # categories = ['footwear', 'lower_body_clothing', 'upper_body_clothing', 'over_upper_body_clothing']
    categories = list(ClothingCategory.__members__.values())

    # Exclude the category of the initial item
    missing_categories = [cat for cat in categories if cat != initial_item.category]
    #print(f"Missing categories: {missing_categories}")

    # Prepare lists for each category
    recommendations = []  # Final recommended items for each category

    for category in missing_categories:
        # Filter items by category
        items_in_category = [item for item in items if item.category == category]

        # Find weather-suitable items in this category
        weather_suitable_items = [
            item for item in items_in_category
            if any(cond in weather_conditions for cond in item.weather_compatibilities)
        ]

        # If weather-suitable items exist, restrict to them; otherwise, use all items in this category
        final_items = weather_suitable_items if weather_suitable_items else items_in_category
        #print(f"Category: {category}, Final items: {[item.descriptor for item in final_items]}")

        # Prepare data for OpenAI API
        item_descriptions = [
            f"{item.descriptor} ({item.category.name.lower()}, {item.color.name.lower()}, suitable for {[comp.name.lower() for comp in item.weather_compatibilities]})"
            for item in final_items
        ]

        # OpenAI prompt to select the best style
        prompt = (
            f"Select the best clothing item for a stylish outfit in the {category.name.lower()} category. "
            f"Available options: {', '.join(item_descriptions)}"
            "The ouptut has to be a strict format as: object name, category, dominant color, [weather suitability]." "Say nothing else."
        )

        # Use OpenAI to select the best item
        try:
            print("GPTTTTTTTTTTTTT")
            response = OpenAIClient.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a fashion expert."},
                    {"role": "user", "content": prompt}
                ],
                seed = 2,
                max_tokens=100,
            )
            selected_item_name = response.choices[0].message.content.strip()
            print("GPTTTTTTTTTTTTT", response.choices, selected_item_name)
            #print(f"OpenAI response for {category}: {selected_item_name}")

            # Find the selected item by name
            selected_item = next((item for item in final_items if item.descriptor in selected_item_name), None)
            if selected_item:
                recommendations.append(selected_item)
                #print(f"Added {selected_item.descriptor} to recommendations.")

        except Exception as e:
            print(f"Error with OpenAI API for category {category}: {e}")
            continue

    #print(f"Final recommendations: {[item.descriptor for item in recommendations]}")
    return recommendations



# To test alone
# if __name__ == "__main__":
#     image_path = "MyCode/matthias.jpg"
#     my_cloth = ClothingIdentifier()
#     result = my_cloth.analyze_image(image_path)
#     parsed_result = my_cloth.parse_output_to_list(result)
#     print(parsed_result)
 


###Code to try
if __name__ == "__main__":
    # Define clothing items
    clothes = [
        # Clothing("Rain Boots", "footwear", "black", ["rain", "cold"]),
        # Clothing("Sneakers", "footwear", "white", ["hot", "wind"]),
        Clothing("Jeans", "lower_body_clothing", "blue", ["cold", "wind"]),
        # Clothing("Shorts", "lower_body_clothing", "red", ["hot"]),
        Clothing("T-Shirt", "upper_body_clothing", "white", ["hot"]),
        # Clothing("Jacket", "over_upper_body_clothing", "black", ["cold", "rain"]),
        # Clothing("Raincoat", "over_upper_body_clothing", "yellow", ["rain"]),
        # Clothing("Pullover", "upper_body_clothing", "Brown", ["rain"]),
    ]

    # Get current weather conditions
    weather_conditions = get_meteo()
    print(f"Weather Conditions: {weather_conditions}")

    # Start with an initial item (e.g., Rain Boots)
    initial_item = clothes[0]  # Assume the first item is chosen
    print(f"Initial Item: {initial_item.descriptor} ({initial_item.category}, {initial_item.color}, {initial_item.weather_compatibilities})")

    # Generate the complete outfit
    recommendations = complete_outfit_with_openai(initial_item, clothes, weather_conditions)

    print("Recommended Outfit:")
    for rec in recommendations:
        print(f"{rec.descriptor} ({rec.category}, {rec.color}, {rec.weather_compatibilities})")
