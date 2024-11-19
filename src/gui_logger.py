import tkinter as tk
from tkinter import ttk
import pandas as pd
import os
import datetime

# Get the directory of the current script
script_dir = os.path.dirname(__file__)

# Relative file paths
kart_file = os.path.join(script_dir, "../data/karts.csv")
map_file = os.path.join(script_dir, "../data/maps.csv")
output_file = os.path.join(script_dir, "../output/results.csv")

# Load data from files
def load_data():
    try:
        karts_df = pd.read_csv(kart_file)
        maps_df = pd.read_csv(map_file)
        karts = karts_df["Kart Name"].tolist()
        maps = maps_df["Map Name"].tolist()
        return karts, maps
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return [], []

karts, maps = load_data()

# Prepend empty selection to kart and map options
karts_with_empty = ["-- Select --"] + karts
maps_with_empty = ["-- Select --"] + maps

# Initialize output CSV if not already present
def initialize_output_csv():
    if not os.path.exists(output_file) or os.stat(output_file).st_size == 0:
        # Create DataFrame with required columns
        df = pd.DataFrame(columns=["Date", "Time", "Map Name", "Azhan Placement", "Raj Placement",
                                   "Sameer Placement", "Azhan Kart", "Raj Kart", "Sameer Kart"])
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        df.to_csv(output_file, index=False)

# Validate placement input and kart selection
def validate_inputs(placement, kart_combobox):
    if not placement:
        return False, "Placement field cannot be empty."
    try:
        placement = int(placement)
    except ValueError:
        return False, "Placement must be a number between 0 and 8."
    if placement < 0 or placement > 8:
        return False, "Placement must be between 0 and 8."
    if placement > 0 and (kart_combobox.get() == "-- Select --" or not kart_combobox.get()):
        return False, "Kart must be selected for placements 1-8."
    return True, ""

# Save data to CSV
def save_data():
    map_name = map_combobox.get()
    azhan_placement = azhan_entry.get()
    raj_placement = raj_entry.get()
    sameer_placement = sameer_entry.get()
    azhan_kart = azhan_kart_combobox.get()
    raj_kart = raj_kart_combobox.get()
    sameer_kart = sameer_kart_combobox.get()

    if map_name == "-- Select --" or not map_name:
        status_label.config(text="Error: Map must be selected!", fg="red")
        return

    # Validate inputs for each player
    validations = [
        validate_inputs(azhan_placement, azhan_kart_combobox),
        validate_inputs(raj_placement, raj_kart_combobox),
        validate_inputs(sameer_placement, sameer_kart_combobox),
    ]
    for is_valid, error_message in validations:
        if not is_valid:
            status_label.config(text=error_message, fg="red")
            return

    # Get current date and time
    now = datetime.datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")
    
    # Explicitly handle DNR for non-racers
    azhan_kart = azhan_kart if int(azhan_placement) > 0 else "DNR"
    raj_kart = raj_kart if int(raj_placement) > 0 else "DNR"
    sameer_kart = sameer_kart if int(sameer_placement) > 0 else "DNR"

    # Create new row data as a DataFrame
    new_data = pd.DataFrame([{
        "Date": current_date,
        "Time": current_time,
        "Map Name": map_name,
        "Azhan Placement": azhan_placement,
        "Raj Placement": raj_placement,
        "Sameer Placement": sameer_placement,
        "Azhan Kart": azhan_kart,
        "Raj Kart": raj_kart,
        "Sameer Kart": sameer_kart
    }])

    # Load existing CSV or create a new DataFrame if empty
    try:
        existing_data = pd.read_csv(output_file)
    except pd.errors.EmptyDataError:
        existing_data = pd.DataFrame(columns=["Date", "Time", "Map Name", "Azhan Placement", "Raj Placement",
                                              "Sameer Placement", "Azhan Kart", "Raj Kart", "Sameer Kart"])

    # Count the total number of races and races for the current day
    daily_races = len(existing_data[existing_data["Date"] == current_date]) + 1
    total_races = len(existing_data) + 1

    # Concatenate the new data with the existing data
    updated_data = pd.concat([existing_data, new_data], ignore_index=True)

    # Save back to the CSV
    updated_data.to_csv(output_file, index=False)

    # Reset the map dropdown to "-- Select --"
    map_combobox.set("-- Select --")

    # Status message
    status_label.config(
        text=f"Race #{daily_races} today logged!\nTotal Races: {total_races}",
        fg="green"
    )

# GUI setup
initialize_output_csv()
root = tk.Tk()
root.title("Nemokart Race Logger")

# Map selection
tk.Label(root, text="Select Map:").grid(row=0, column=0, padx=10, pady=5)
map_combobox = ttk.Combobox(root, values=maps_with_empty, state="readonly")
map_combobox.grid(row=0, column=1, padx=10, pady=5)
map_combobox.set("-- Select --")  # Default value

# Azhan placement and kart
tk.Label(root, text="Azhan Placement:").grid(row=1, column=0, padx=10, pady=5)
azhan_entry = ttk.Entry(root)
azhan_entry.grid(row=1, column=1, padx=10, pady=5)
azhan_kart_combobox = ttk.Combobox(root, values=karts_with_empty, state="readonly")
azhan_kart_combobox.grid(row=1, column=2, padx=10, pady=5)
azhan_kart_combobox.set("-- Select --")  # Default value

# Raj placement and kart
tk.Label(root, text="Raj Placement:").grid(row=2, column=0, padx=10, pady=5)
raj_entry = ttk.Entry(root)
raj_entry.grid(row=2, column=1, padx=10, pady=5)
raj_kart_combobox = ttk.Combobox(root, values=karts_with_empty, state="readonly")
raj_kart_combobox.grid(row=2, column=2, padx=10, pady=5)
raj_kart_combobox.set("-- Select --")  # Default value

# Sameer placement and kart
tk.Label(root, text="Sameer Placement:").grid(row=3, column=0, padx=10, pady=5)
sameer_entry = ttk.Entry(root)
sameer_entry.grid(row=3, column=1, padx=10, pady=5)
sameer_kart_combobox = ttk.Combobox(root, values=karts_with_empty, state="readonly")
sameer_kart_combobox.grid(row=3, column=2, padx=10, pady=5)
sameer_kart_combobox.set("-- Select --")  # Default value

# Log Button
log_button = tk.Button(root, text="Log Race", command=save_data)
log_button.grid(row=4, column=0, columnspan=3, pady=10)

# Status Label
status_label = tk.Label(root, text="")
status_label.grid(row=5, column=0, columnspan=3, pady=5)

root.mainloop()
