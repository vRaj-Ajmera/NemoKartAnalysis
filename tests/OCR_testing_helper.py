import cv2
import numpy as np
import easyocr
import os
import re
from rapidfuzz import process, fuzz
import json

# Directory to save processed images
processed_dir = "tests/Preprocessed_Imgs"
os.makedirs(processed_dir, exist_ok=True)

# Base directory
base_dir = os.path.dirname(os.path.dirname(__file__))

# Player aliases
player_aliases_path = os.path.join(base_dir, "data", "player_aliases.json")

def load_player_aliases():
    """
    Load player aliases from player_aliases.json and create a dictionary mapping aliases to player names.
    """
    aliases_mapping = {}
    try:
        with open(player_aliases_path, "r") as file:
            aliases_data = json.load(file)
            for player_name, aliases in aliases_data.items():
                for alias in aliases:
                    aliases_mapping[alias.lower()] = player_name  # Map each alias to the player's name
                aliases_mapping[player_name.lower()] = player_name  # Include the player's name as an alias
        return aliases_mapping
    except Exception as e:
        print(f"Error loading player aliases: {e}")
        return {}

aliases_mapping = load_player_aliases()
aliases_list = list(aliases_mapping.keys())  # Prepare a list of all aliases for matching

def fuzzy_match_player_name(detected_text):
    """
    Use fuzzy matching to find the closest player alias to the detected OCR text.

    Args:
        detected_text (str): The text detected by OCR.

    Returns:
        str: The actual player's name if a match is found, otherwise the original detected text.
    """
    # Use RapidFuzz to find the best match
    match = process.extractOne(detected_text.lower(), aliases_list, scorer=fuzz.ratio)
    if match and match[1] > 80:  # Threshold for similarity score
        matched_alias = match[0]
        actual_name = aliases_mapping[matched_alias]
        return actual_name
    return detected_text

def parse_ocr_results(ocr_results):
    """
    Parse OCR results to extract structured information such as placement, player names, 
    and race times from the raw OCR output.

    Args:
        ocr_results (list): A list of OCR results from EasyOCR, where each entry is a tuple 
                            containing detected text, bounding box coordinates, and confidence score.

    Returns:
        list: A list of dictionaries where each dictionary represents a row with the following fields:
              - 'placement': The placement of the player in the race (int).
              - 'player_name': The name of the player (str), determined via fuzzy matching to aliases.
              - 'race_time': The race completion time in "MM:SS.SS" format (str).
    Details:
        - Starts parsing after encountering the "TIME" label in OCR results.
        - Uses regular expressions to identify race times and a fuzzy matching function to 
          determine player names.
        - Ensures low-confidence results (confidence < 0.01) are skipped.
        - Processes the data row-by-row, resetting after each complete row of information is parsed.
    """
    found_time_label = False  # Flag to indicate "TIME" label found
    current_placement = 1  # Start with first place
    parsed_rows = []  # Store rows as dictionaries
    temp_row = {"placement": current_placement, "player_name": None, "race_time": None}

    for result in ocr_results:
        detected_text, confidence = result[1], result[2]
        if confidence < 0.01:  # Skip low-confidence results
            continue

        # Check for the "TIME" label
        if detected_text.strip().lower() == "time":
            found_time_label = True
            continue

        if not found_time_label:
            # Skip everything until "TIME" is found
            continue
        
        if temp_row["placement"] is None and detected_text.strip().isdigit() and len(detected_text.strip()) == 1:
            temp_row["placement"] = current_placement
            continue

        # Extract race time
        time_match = re.search(r"(\d{1,2})[:.*,]*?(\d{2})[:.*,]*?(\d{2})", detected_text)
        if time_match:
            minutes, seconds, milliseconds = time_match.groups()
            race_time = f"{int(minutes)}:{seconds}.{milliseconds}"
            if temp_row["race_time"] is None:  # Only fill race time if empty
                temp_row["race_time"] = race_time
        else:
            # Use fuzzy matching to determine player name
            matched_name = fuzzy_match_player_name(detected_text)
            if temp_row["player_name"] is None:
                temp_row["player_name"] = matched_name

        # If a complete row is filled, add placement, add to parsed rows, and reset temp_row
        if temp_row["player_name"] and temp_row["race_time"]:
            temp_row["placement"] = current_placement
            parsed_rows.append(temp_row.copy())
            temp_row = {"placement": None, "player_name": None, "race_time": None}
            current_placement += 1  # Increment placement

    return parsed_rows

def filter_logged_rows(parsed_rows):
    """
    Filter parsed rows to only include players listed in the aliases file.

    Args:
        parsed_rows (list): List of parsed rows from OCR results.

    Returns:
        list: Filtered list of logged rows containing placement, player_name, and race_time.
    """
    try:
        
        logged_rows = []

        # Fill logged rows with parsed data
        for i, row in enumerate(parsed_rows):
            if i >= 8:
                break  # Ignore extra rows if they exceed the GUI capacity

            # Check if the player is in aliases_mapping
            if row["player_name"] not in aliases_mapping.values():
                continue

            logged_rows.append(row)
        
        return logged_rows

    except Exception as e:
        print(f"Error filtering logged rows: {e}")
        return []

def preprocess_image(image_path):
    """
    Preprocess the image to keep only colors with RGB values greater than [245, 238, 229].
    Save the processed image for verification.
    """
    try:
        # Load the image in RGB
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert to RGB

        # Define the lower threshold (optimum threshold)
        lower_threshold = np.array([245, 238, 229], dtype=np.uint8)

        # bad threshold for testing
        #lower_threshold = np.array([255, 238, 248], dtype=np.uint8)

        # Create a mask for pixels greater than the threshold
        mask = cv2.inRange(image_rgb, lower_threshold, np.array([255, 255, 255], dtype=np.uint8))

        # Apply the mask to keep only the specified range
        processed_image = cv2.bitwise_and(image, image, mask=mask)

        # Convert the processed image to grayscale
        grayscale_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2GRAY)

        # Save the preprocessed image
        base_name = os.path.basename(image_path)
        preprocessed_image_path = os.path.join(processed_dir, base_name.replace(".png", "_processed.png"))
        cv2.imwrite(preprocessed_image_path, grayscale_image)
        print(f"Preprocessed image saved to {preprocessed_image_path}")

        return preprocessed_image_path
    except Exception as e:
        print(f"Error during preprocessing: {e}")
        return None

def process_image(image_path):
    """
    Process the image, extract text using EasyOCR, parse it, and filter logged rows.

    Args:
        image_path (str): Path to the image to process.

    Returns:
        list: Filtered logged rows.
    """
    try:
        # Preprocess the image
        preprocessed_image_path = preprocess_image(image_path)

        if not preprocessed_image_path:
            print("Error during preprocessing. Skipping OCR.")
            return None

        # Initialize EasyOCR Reader
        reader = easyocr.Reader(['en'])  # Use 'en' for English

        # Read the text from the preprocessed image
        ocr_results = reader.readtext(preprocessed_image_path, detail=1)

        # Parse the OCR results
        parsed_rows = parse_ocr_results(ocr_results)
        print(f"Parsed rows: {parsed_rows}")

        # Filter logged rows
        logged_rows = filter_logged_rows(parsed_rows)
        print(f"Logged rows: {logged_rows}")
        return logged_rows

    except Exception as e:
        print(f"Error processing image: {e}")
        return None
