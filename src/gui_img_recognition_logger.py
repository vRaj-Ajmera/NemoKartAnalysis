import tkinter as tk
from tkinter import ttk
import pandas as pd
import os
import datetime
import re
from tkinterdnd2 import DND_FILES, TkinterDnD
import numpy as np
import easyocr
import cv2
import json
from rapidfuzz import process, fuzz
from PIL import ImageGrab, Image
from tkinter import messagebox
import yaml
import sys
import subprocess

MAX_RACERS=8

# Get the directory of the current script
script_dir = os.path.dirname(__file__)

# Add the `yolov5` directory to `sys.path` as a root for its submodules
yolov5_path = os.path.join(script_dir, "model/yolov5")
sys.path.append(yolov5_path)

from model.yolov5.utils.general import non_max_suppression
from model.yolov5.models.common import DetectMultiBackend

# Relative file paths
kart_file = os.path.join(script_dir, "../data/karts.csv")
map_file = os.path.join(script_dir, "../data/maps.csv")
players_file = os.path.join(script_dir, "../data/players.csv")
output_file = os.path.join(script_dir, "../output/results.csv")
preprocessed_image_file_path = os.path.join(script_dir, "../output/img_processing/preprocessed_img.png")
clipboard_image_file_path = os.path.join(script_dir, "../output/img_processing/clipboard_img.png")
player_aliases_path = os.path.join(script_dir, "../data/player_aliases.json")
karts_class_IDs_path = os.path.join(script_dir, "model/data.yaml")

# Path to YOLOv5 model
weights_path = os.path.join(script_dir, "model/best.pt")
yolo_model = DetectMultiBackend(weights_path)

# karts_img_prediction_file_path = os.path.join(script_dir, "../output/img_processing/karts_prediction.png")

def load_kart_names(data_yaml_path):
    """
    Load kart names from the YOLO data.yaml file.

    Args:
        data_yaml_path (str): Path to the YOLO data.yaml file.

    Returns:
        list: List of kart names in the order of class IDs.
    """
    try:
        with open(data_yaml_path, "r") as f:
            data_yaml = yaml.safe_load(f)
            return data_yaml["names"]
    except FileNotFoundError:
        print(f"Error: {data_yaml_path} not found.")
        return []
    except Exception as e:
        print(f"Unexpected error while loading data.yaml: {e}")
        return []


def detect_karts_with_yolo(image_path, data_yaml_path):
    """
    Use YOLOv5's built-in detect.py to identify karts and save the output image.
    Overwrites the labels file for each new image processed.

    Args:
        image_path (str): Path to the image to be processed.
        data_yaml_path (str): Path to the YOLO data.yaml file for class names.
    
    Returns:
        List of detected kart names extracted from the labels file, sorted by y-values.
    """
    try:
        # Load kart names from data.yaml
        kart_names = load_kart_names(data_yaml_path)
        if not kart_names:
            print("Error: Kart names could not be loaded.")
            return []

        # Path to YOLOv5's detect.py script
        detect_script_path = os.path.join(yolov5_path, "detect.py")
        
        # Output path for detection results
        output_dir = os.path.join(script_dir, "../output/img_processing/karts_predictions")
        
        # Clear existing label files in the output directory
        label_files_path = os.path.join(output_dir, "labels")
        if os.path.exists(label_files_path):
            for file in os.listdir(label_files_path):
                os.remove(os.path.join(label_files_path, file))
        
        # Command to execute YOLO detection
        command = [
            "python",
            detect_script_path,
            "--weights", weights_path,
            "--img", "640",  # Resize input image to 640x640
            "--conf", "0.25",  # Confidence threshold
            "--source", image_path,  # Input image path
            "--save-txt",  # Save results to .txt
            "--save-conf",  # Save confidence scores
            "--project", output_dir,  # Detection results directory
            "--name", "",  # Empty name avoids subfolder creation
            "--exist-ok"  # Avoid overwriting errors
        ]

        # Run the command using subprocess
        subprocess.run(command, check=True)
        print(f"YOLO detection completed. Check the output folder for results.")

        # Parse the labels file to extract kart names
        detected_karts_set = []  # To store rows with y-values, confidence, and kart names
        labels_path = os.path.join(output_dir, "labels")
        
        if os.path.exists(labels_path):
            for label_file in os.listdir(labels_path):
                if label_file.endswith(".txt"):
                    with open(os.path.join(labels_path, label_file), "r") as f:
                        for line in f.readlines():
                            parts = line.split()
                            if len(parts) < 6:
                                continue  # Skip invalid rows

                            class_id = int(parts[0])  # Extract class ID
                            x = float(parts[1])  # x-center (normalized)
                            y = float(parts[2])  # y-center (normalized)
                            width = float(parts[3])  # Width (normalized)
                            height = float(parts[4])  # Height (normalized)
                            confidence = float(parts[5])  # Confidence score

                            kart_name = kart_names[class_id]  # Map class ID to kart name
                            detected_karts_set.append((y, confidence, kart_name))  # Append raw data

        # Resolve overlabeling by grouping y-values within a 0.04 range and keeping the highest confidence
        filtered_karts = {}
        for y, conf, kart in detected_karts_set:
            # Find if there's already a close y-value in the filtered_karts
            close_y = next((key for key in filtered_karts if abs(key - y) < 0.04), None)
            if close_y is None:
                # No close y-value found, add a new entry
                filtered_karts[y] = (conf, kart)
            else:
                # Close y-value found, update if confidence is higher
                if conf > filtered_karts[close_y][0]:
                    filtered_karts[close_y] = (conf, kart)

        # Sort by y-value and extract kart names
        sorted_karts = [kart for _, (_, kart) in sorted(filtered_karts.items())]
        #print(f"Detected karts (sorted): {sorted_karts}")

        return sorted_karts

    except subprocess.CalledProcessError as e:
        print(f"Error during YOLO detection: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

# Load data from files
def load_data():
    try:
        karts_df = pd.read_csv(kart_file)
        maps_df = pd.read_csv(map_file)
        players_df = pd.read_csv(players_file)
        karts = karts_df["Kart Name"].tolist()
        maps = maps_df["Map Name"].tolist()
        players = players_df["Player Name"].tolist()
        return karts, maps, players
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return [], [], []

karts, maps, players = load_data()
karts_with_empty = ["-- Select --"] + karts
maps_with_empty = ["-- Select --"] + maps

# Initialize output CSV and ensure columns are aligned with the players list
def initialize_csv():
    # Define the expected columns based on the current players.csv file
    expected_columns = ["Date", "Time", "Map Name"]  # Start with static columns
    
    # Add player-specific columns in the desired order
    for player in players:
        expected_columns.extend([
            f"{player} Placement",
            f"{player} Kart",
            f"{player} Racetime"
        ])

    if not os.path.exists(output_file) or os.stat(output_file).st_size == 0:
        # If the file doesn't exist, create it with the correct columns
        pd.DataFrame(columns=expected_columns).to_csv(output_file, index=False)
    else:
        # Read the existing file
        existing_df = pd.read_csv(output_file)

        # Check for missing columns
        missing_columns = [col for col in expected_columns if col not in existing_df.columns]

        # Add missing columns with default "DNR" values
        if missing_columns:
            for col in missing_columns:
                existing_df[col] = "DNR"

            # Save the updated DataFrame back to the file
            existing_df.to_csv(output_file, index=False)

initialize_csv()

# Validate input for each player
def validate_player_inputs(player, placement, kart, race_time):
    if player == "-- Select --":
        return True, ""
    if placement == "-- Select --" or not placement.isdigit() or int(placement) not in range(1, 9):
        return False, f"Placement for {player} must be a number between 1 and 8."
    if kart == "-- Select --":
        return False, f"Kart for {player} must be selected."
    # Validate race time format using regex
    time_pattern = r"^\d:[0-5]\d\.\d{2}$"  # M:SS.xx format
    if not race_time or not re.match(time_pattern, race_time):
        return False, f"Race time for {player} must be in the format M:SS.xx (e.g., 1:23.45)."
    return True, ""

# Save data to CSV
def save_data():
    map_name = map_combobox.get()
    if map_name == "-- Select --":
        status_label.config(text="Error: Map must be selected!", fg="red")
        return

    now = datetime.datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")

    row_data = {"Date": current_date, "Time": current_time, "Map Name": map_name}
    selected_players = {}
    selected_players_list = []  # Track selected players
    placements_used = set()  # Track used placements

    # Collect data for selected players
    for widgets in player_widgets:
        player = widgets["player"].get()
        placement = widgets["placement"].get()
        kart = widgets["kart"].get()
        race_time = widgets["race_time"].get()

        # Validate unique player selection
        if player in selected_players_list and player != "-- Select --":
            status_label.config(text=f"Error: {player} is selected more than once!", fg="red")
            return
        selected_players_list.append(player)

        if player == "-- Select --":
            continue

        # Validate inputs
        is_valid, error_message = validate_player_inputs(player, placement, kart, race_time)
        if not is_valid:
            status_label.config(text=error_message, fg="red")
            return

        if placement in placements_used:
            status_label.config(text=f"Placement {placement} is already used by another player!", fg="red")
            return

        placements_used.add(placement)
        selected_players[player] = {"Placement": placement, "Kart": kart, "Racetime": race_time}

    # Ensure at least one player is selected
    if not selected_players:
        status_label.config(text="Error: At least one player must be selected!", fg="red")
        return

    # Validate that higher placement has faster race times
    race_data = []

    # Construct a list of placement and race time objects
    for player, data in selected_players.items():
        placement = int(data["Placement"])
        race_time_parts = data["Racetime"].split(":")
        current_time = float(race_time_parts[0]) * 60 + float(race_time_parts[1])

        race_data.append({"Placement": placement, "Race Time": current_time})

    # Compare each player's race time with all other players
    for i in range(len(race_data)):
        for j in range(len(race_data)):
            if i == j:  # Skip comparing the same player
                continue
            if race_data[i]["Placement"] < race_data[j]["Placement"]:  # Higher placement (lower number)
                if race_data[i]["Race Time"] > race_data[j]["Race Time"]:  # Slower race time
                    status_label.config(
                        text=f"Error: Placement {race_data[i]['Placement']} ({race_data[i]['Race Time']:.2f}s) has a slower time "
                            f"than placement {race_data[j]['Placement']} ({race_data[j]['Race Time']:.2f}s)!",
                        fg="red"
                    )
                    return

    # Fill DNR for unselected players
    for player in players:
        if player in selected_players:
            row_data[f"{player} Placement"] = selected_players[player]["Placement"]
            row_data[f"{player} Kart"] = selected_players[player]["Kart"]
            row_data[f"{player} Racetime"] = selected_players[player]["Racetime"]
        else:
            row_data[f"{player} Placement"] = "DNR"
            row_data[f"{player} Kart"] = "DNR"
            row_data[f"{player} Racetime"] = "DNR"

    # Append data to results CSV
    try:
        results_df = pd.read_csv(output_file)
    except pd.errors.EmptyDataError:
        results_df = pd.DataFrame()

    # Ensure columns are updated with any new players
    expected_columns = ["Date", "Time", "Map Name"] + \
                       [f"{player} Placement" for player in players] + \
                       [f"{player} Kart" for player in players] + \
                       [f"{player} Racetime" for player in players]

    for col in expected_columns:
        if col not in results_df.columns:
            results_df[col] = "DNR"

    new_row_df = pd.DataFrame([row_data])
    results_df = pd.concat([results_df, new_row_df], ignore_index=True)

    # Save back to file
    results_df.to_csv(output_file, index=False)
    status_label.config(text="Race logged successfully!", fg="green")

    # Reset inputs
    map_combobox.set("-- Select --")
    for widgets in player_widgets:
        widgets["placement"].set("-- Select --")
        widgets["race_time"].delete(0, tk.END)

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

def fill_GUI_with_results(logged_rows, detected_karts):
    """
    Logs race data (times, placements, and players) in the GUI textboxes.
    """
    # Clear all fields initially
    for widgets in player_widgets:
        widgets["player"].set("-- Select --")
        widgets["placement"].set("-- Select --")
        widgets["race_time"].delete(0, tk.END)
        widgets["kart"].set("-- Select --")

    # Fill GUI fields with logged rows data
    for row in logged_rows:
        placement = row["placement"]
        name = row["player_name"]
        race_time = row["race_time"]
        kart = detected_karts[placement - 1]

        # log in the row equal to the placement
        widgets = player_widgets[placement - 1]
        widgets["placement"].set(str(placement))
        widgets["player"].set(name)
        widgets["race_time"].insert(0, race_time)
        widgets["kart"].set(kart)


def preprocess_image(image_path, output_path=preprocessed_image_file_path):
    """
    Preprocess the image to keep only colors with RGB values greater than [245, 238, 229].
    Save the processed image for verification.
    """
    try:
        # Load the image in RGB
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert to RGB

        # Define the lower threshold
        lower_threshold = np.array([245, 238, 229], dtype=np.uint8)

        # Create a mask for pixels greater than the threshold
        mask = cv2.inRange(image_rgb, lower_threshold, np.array([255, 255, 255], dtype=np.uint8))

        # Apply the mask to keep only the specified range
        processed_image = cv2.bitwise_and(image, image, mask=mask)

        # Convert the processed image to grayscale
        grayscale_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2GRAY)

        # Save the preprocessed image for verification
        cv2.imwrite(output_path, grayscale_image)
        print(f"Preprocessed image saved to {output_path}")

        return output_path
    except Exception as e:
        print(f"Error during preprocessing: {e}")
        return None


def process_image(image_path):
    """
    Process the image, perform OCR and kart detection, and update the GUI.
    """
    try:
        # Preprocess the image for OCR
        preprocessed_image_path = preprocess_image(image_path)
        if not preprocessed_image_path:
            print("Error during preprocessing. Skipping OCR.")
            return

        # OCR processing
        reader = easyocr.Reader(['en'])  # Initialize EasyOCR reader
        ocr_results = reader.readtext(preprocessed_image_path, detail=1)

        print("\n--- EasyOCR Results ---\n")
        for result in ocr_results:
            text, confidence = result[1], result[2]
            print(f"Detected Text: {text} (Confidence: {confidence})")
        print("\n--- End of EasyOCR Results ---\n")

        # Parse and filter OCR results
        parsed_rows = parse_ocr_results(ocr_results)
        logged_rows = filter_logged_rows(parsed_rows)
        print(f"Parsed rows: {parsed_rows}")
        print(f"Logged rows: {logged_rows}")

        # Perform kart detection
        detected_karts = detect_karts_with_yolo(image_path, data_yaml_path=karts_class_IDs_path)
        print(f"Detected Karts: {detected_karts}")

        # Fill GUI fields with OCR and Kart Img recognition results
        fill_GUI_with_results(logged_rows, detected_karts)

        status_label.config(text="OCR and kart detection completed!", fg="green")
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def paste_image_from_clipboard():
    """
    Check for an image in the clipboard and process it.
    """
    try:
        # Attempt to grab the image from the clipboard
        clipboard_image = ImageGrab.grabclipboard()

        if isinstance(clipboard_image, Image.Image):  # Check if the clipboard contains an image
            # Save the clipboard image temporarily
            clipboard_image.save(clipboard_image_file_path, "PNG")
            # Process the image
            process_image(clipboard_image_file_path)
            status_label.config(text="Image pasted and processed from clipboard!", fg="green")
        else:
            messagebox.showwarning("No Image Found", "The clipboard does not contain a valid image.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while pasting the image: {e}")

# GUI Setup
root = TkinterDnD.Tk()
root.title(f"Nemokart Race Logger - Logging to: {os.path.basename(output_file)}")

# Map Selection
tk.Label(root, text="Select Map:").grid(row=0, column=0, padx=10, pady=5)
map_combobox = ttk.Combobox(root, values=maps_with_empty, state="readonly", width=20)
map_combobox.grid(row=0, column=1, padx=10, pady=5)
map_combobox.set("-- Select --")

tk.Label(root, text="(Example Input - 1:23.45)", fg="gray").grid(row=0, column=2, columnspan=2, padx=10, pady=5)

# Dynamic Player Rows
player_widgets = []
for i in range(MAX_RACERS):
    player = tk.StringVar(value="-- Select --")
    placement = tk.StringVar(value="-- Select --")
    kart = tk.StringVar(value="-- Select --")

    ttk.Combobox(root, textvariable=player, values=["-- Select --"] + players, state="readonly", width=20).grid(row=i + 1, column=0, padx=10, pady=5)
    ttk.Combobox(root, textvariable=placement, values=[f"{x}" for x in range(1, 9)], state="readonly", width=10).grid(row=i + 1, column=1, padx=10, pady=5)
    ttk.Combobox(root, textvariable=kart, values=karts_with_empty, state="readonly", width=20).grid(row=i + 1, column=2, padx=10, pady=5)
    race_time_entry = tk.Entry(root, width=15)
    race_time_entry.grid(row=i + 1, column=3, padx=10, pady=5)

    player_widgets.append({"player": player, "placement": placement, "kart": kart, "race_time": race_time_entry})

# Drag-and-Drop Area
drag_and_drop_label = tk.Label(root, text="Drag and drop an image here", bg="lightgray", width=50, height=2)
drag_and_drop_label.grid(row=MAX_RACERS + 2, column=0, columnspan=4, pady=10)

def handle_drop(event):
    file_path = event.data.strip()
    if os.path.isfile(file_path) and file_path.lower().endswith((".png", ".jpg", ".jpeg")):
        process_image(file_path)
    else:
        status_label.config(text="Invalid file type. Please drop an image file.", fg="red")

drag_and_drop_label.drop_target_register(DND_FILES)
drag_and_drop_label.dnd_bind("<<Drop>>", handle_drop)

# Log Button
tk.Button(root, text="Log Race", command=save_data).grid(row=MAX_RACERS + 4, column=0, columnspan=4, pady=10)

# Add a button for pasting images from the clipboard
paste_button = tk.Button(root, text="Paste Image from Clipboard", command=paste_image_from_clipboard, bg="lightgray", padx=10, pady=5)
paste_button.grid(row=MAX_RACERS + 3, column=1, columnspan=2, pady=10)

# Status Label
status_label = tk.Label(root, text="", fg="green")
status_label.grid(row=MAX_RACERS + 5, column=0, columnspan=4, pady=5)

root.mainloop()