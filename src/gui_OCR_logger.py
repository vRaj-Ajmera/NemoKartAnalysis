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
from rapidfuzz import fuzz

MAX_RACERS=8

# Get the directory of the current script
script_dir = os.path.dirname(__file__)

# Relative file paths
kart_file = os.path.join(script_dir, "../data/karts.csv")
map_file = os.path.join(script_dir, "../data/maps.csv")
players_file = os.path.join(script_dir, "../data/players.csv")
output_file = os.path.join(script_dir, "../output/results.csv")
preprocessed_image_file = os.path.join(script_dir, "../output/img_processing/preprocessed_image.png")

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

def load_player_aliases():
    """
    Load player aliases from player_aliases.json and create a dictionary mapping aliases to player names.
    """
    aliases_file = os.path.join(script_dir, "../data/player_aliases.json")
    aliases_mapping = {}
    try:
        with open(aliases_file, "r") as file:
            aliases_data = json.load(file)
            for player_name, aliases in aliases_data.items():
                for alias in aliases:
                    aliases_mapping[alias.lower()] = player_name  # Map each alias to the player's name
                aliases_mapping[player_name.lower()] = player_name  # Include the player's name as an alias
        return aliases_mapping
    except FileNotFoundError as e:
        print(f"Error loading aliases: {e}")
        return {}
    except Exception as e:
        print(f"Unexpected error loading aliases: {e}")
        return {}

# Load player aliases
aliases_mapping = load_player_aliases()

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

def preprocess_image(image_path, output_path=preprocessed_image_file):
    """
    Preprocess the image to keep only colors with RGB values greater than [255, 248, 229].
    Save the processed image for verification.
    """
    try:
        # Load the image in RGB
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert to RGB

        # Define the lower threshold
        lower_threshold = np.array([255, 248, 229], dtype=np.uint8)

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
    Process the image and extract text using EasyOCR with the preprocessed image.
    """
    try:
        # Preprocess the image to isolate specified colors
        preprocessed_image_path = preprocess_image(image_path)

        if not preprocessed_image_path:
            print("Error during preprocessing. Skipping OCR.")
            return

        # Initialize EasyOCR Reader
        reader = easyocr.Reader(['en'])  # Use 'en' for English

        # Read the text from the preprocessed image
        ocr_results = reader.readtext(preprocessed_image_path, detail=1)

        print("\n--- EasyOCR Results ---\n")
        for result in ocr_results:
            text, confidence = result[1], result[2]
            print(f"Detected Text: {text} (Confidence: {confidence})")
        print("\n--- End of EasyOCR Results ---\n")

        # Fill dropdowns with the parsed OCR results
        #fill_dropdowns_with_ocr_results(ocr_results)
        #status_label.config(text="Dropdowns updated with OCR results!", fg="green")
        
        # Log race times in the GUI for debugging
        fill_race_data_with_ocr_results(ocr_results, aliases_mapping)

        status_label.config(text="Race times logged from OCR results!", fg="green")


    except Exception as e:
        print(f"Error processing image: {e}")


def fill_race_data_with_ocr_results(ocr_results, aliases_mapping):
    """
    Logs race data (times, placements, and players) in the GUI textboxes
    by sequentially parsing OCR results and aligning the data.
    """
    # Clear all fields initially
    for widgets in player_widgets:
        widgets["player"].set("-- Select --")
        widgets["placement"].set("-- Select --")
        widgets["race_time"].delete(0, tk.END)

    
    found_time_label = False  # Flag to indicate that "TIME" label has been encountered
    current_placement = 1  # Start with first place
    parsed_rows = []  # Store rows as (placement, player_name, race_time)
    temp_row = {"placement": current_placement, "player_name": None, "race_time": None}

    for result in ocr_results:
        detected_text, confidence = result[1], result[2]
        if confidence < 0.001:  # Skip low-confidence results
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
        time_match = re.search(r"(\d{1,2})[:.*](\d{2})[:.*](\d{2})", detected_text)
        if time_match:
            minutes, seconds, milliseconds = time_match.groups()
            race_time = f"{int(minutes)}:{seconds}.{milliseconds}"
            if temp_row["race_time"] is None:  # Only fill race time if empty
                temp_row["race_time"] = race_time
        else:
            # Match player name using aliases
            for alias, actual_name in aliases_mapping.items():
                if alias in detected_text.lower():
                    if temp_row["player_name"] is None:  # Only fill player name if empty
                        temp_row["player_name"] = actual_name
                    break
            if temp_row["player_name"] is None:
                temp_row["player_name"] = detected_text.lower()

        # If a complete row is filled, add placement, add to parsed rows, and reset temp_row
        if temp_row["player_name"] and temp_row["race_time"] and temp_row["placement"]:
            parsed_rows.append(temp_row.copy())
            temp_row = {"placement": None, "player_name": None, "race_time": None}
            current_placement += 1  # Increment placement

    # Handle any remaining row TEST
    #if temp_row["player_name"] and temp_row["race_time"]:
    #    temp_row["placement"] = current_placement
    #    parsed_rows.append(temp_row)


    # Fill GUI fields with parsed data
    for i, row in enumerate(parsed_rows):
        if i >= len(player_widgets):
            break  # Ignore extra rows if they exceed the GUI capacity

        widgets = player_widgets[i]
        widgets["placement"].set(str(row["placement"]) if row["placement"] else "-- Select --")
        widgets["player"].set(row["player_name"] if row["player_name"] else "-- Select --")
        if row["race_time"]:
            widgets["race_time"].insert(0, row["race_time"])

    print(f"Parsed rows: {parsed_rows}")  # Debugging output

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
tk.Button(root, text="Log Race", command=save_data).grid(row=MAX_RACERS + 3, column=0, columnspan=4, pady=10)

# Status Label
status_label = tk.Label(root, text="", fg="green")
status_label.grid(row=MAX_RACERS + 4, column=0, columnspan=4, pady=5)

root.mainloop()