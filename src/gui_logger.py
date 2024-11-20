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
maps_best_times_file = os.path.join(script_dir, "../output/maps_best_times.csv")
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

# Initialize output CSVs if not already present
def initialize_csvs():
    # Race results CSV
    if not os.path.exists(output_file) or os.stat(output_file).st_size == 0:
        pd.DataFrame(columns=["Date", "Time", "Map Name", "Azhan Placement", "Raj Placement",
                              "Sameer Placement", "Azhan Kart", "Raj Kart", "Sameer Kart",
                              "Azhan Racetime", "Raj Racetime", "Sameer Racetime"]).to_csv(output_file, index=False)

    # Maps best times CSV
    if not os.path.exists(maps_best_times_file) or os.stat(maps_best_times_file).st_size == 0:
        pd.DataFrame([{"Map Name": map_name, "Best Time": "3:00.00", 
                       "AzhanBestTime": "3:00.00", "RajBestTime": "3:00.00", "SameerBestTime": "3:00.00"} 
                      for map_name in maps]).to_csv(maps_best_times_file, index=False)

# Validate placement and kart inputs
def validate_inputs(placement, kart_combobox, race_time):
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
    if placement > 0 and not race_time:
        return False, "Race time must be entered for placements 1-8."
    return True, ""

# Convert race time string to seconds
def time_to_seconds(race_time):
    minutes, seconds = map(float, race_time.split(":"))
    return minutes * 60 + seconds

# Save data to CSV and update best times
def save_data():
    map_name = map_combobox.get()
    azhan_placement = azhan_entry.get()
    raj_placement = raj_entry.get()
    sameer_placement = sameer_entry.get()
    azhan_kart = azhan_kart_combobox.get()
    raj_kart = raj_kart_combobox.get()
    sameer_kart = sameer_kart_combobox.get()
    azhan_racetime = azhan_time_entry.get()
    raj_racetime = raj_time_entry.get()
    sameer_racetime = sameer_time_entry.get()

    if map_name == "-- Select --" or not map_name:
        status_label.config(text="Error: Map must be selected!", fg="red")
        return

    # Validate inputs for each player
    validations = [
        validate_inputs(azhan_placement, azhan_kart_combobox, azhan_racetime),
        validate_inputs(raj_placement, raj_kart_combobox, raj_racetime),
        validate_inputs(sameer_placement, sameer_kart_combobox, sameer_racetime),
    ]
    for is_valid, error_message in validations:
        if not is_valid:
            status_label.config(text=error_message, fg="red")
            return

    # Get current date and time
    now = datetime.datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")

    # Load maps_best_times.csv
    maps_best_times_df = pd.read_csv(maps_best_times_file)

    # Check and update personal bests and overall bests
    new_pb = {"Azhan": False, "Raj": False, "Sameer": False}
    new_record = False
    for player, race_time, col in [("Azhan", azhan_racetime, "AzhanBestTime"),
                                   ("Raj", raj_racetime, "RajBestTime"),
                                   ("Sameer", sameer_racetime, "SameerBestTime")]:
        if race_time and race_time != "DNR":
            # Update personal best
            current_pb = maps_best_times_df.loc[maps_best_times_df["Map Name"] == map_name, col].iloc[0]
            if time_to_seconds(race_time) < time_to_seconds(current_pb):
                maps_best_times_df.loc[maps_best_times_df["Map Name"] == map_name, col] = race_time
                new_pb[player] = True

            # Update overall best
            current_best = maps_best_times_df.loc[maps_best_times_df["Map Name"] == map_name, "Best Time"].iloc[0]
            if time_to_seconds(race_time) < time_to_seconds(current_best):
                maps_best_times_df.loc[maps_best_times_df["Map Name"] == map_name, "Best Time"] = race_time
                new_record = True

    # Save updated best times
    maps_best_times_df.to_csv(maps_best_times_file, index=False)

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
        "Sameer Kart": sameer_kart,
        "Azhan Racetime": azhan_racetime,
        "Raj Racetime": raj_racetime,
        "Sameer Racetime": sameer_racetime
    }])

    # Load existing CSV or create a new DataFrame if empty
    try:
        existing_data = pd.read_csv(output_file)
    except pd.errors.EmptyDataError:
        existing_data = pd.DataFrame(columns=new_data.columns)

    # Count the total number of races and races for the current day
    daily_races = len(existing_data[existing_data["Date"] == current_date]) + 1
    total_races = len(existing_data) + 1

    # Concatenate the new data with the existing data
    updated_data = pd.concat([existing_data, new_data], ignore_index=True)

    # Save back to the CSV
    updated_data.to_csv(output_file, index=False)

    # Prepare the status message
    status_message = f"Race #{daily_races} today logged!\nTotal Races: {total_races}."
    if new_pb["Azhan"]:
        status_message += "\nAzhan new PB."
    if new_pb["Raj"]:
        status_message += "\nRaj new PB."
    if new_pb["Sameer"]:
        status_message += "\nSameer new PB."
    if new_record:
        status_message += f"\nNew race record for {map_name}!"

    # Reset the map dropdown to "-- Select --"
    map_combobox.set("-- Select --")

    # Update status label
    status_label.config(text=status_message, fg="green")

# GUI setup
initialize_csvs()
root = tk.Tk()
root.title(f"Nemokart Race Logger - Logging to: {os.path.basename(output_file)}")

# Map selection
tk.Label(root, text="Select Map:").grid(row=0, column=0, padx=10, pady=5)
map_combobox = ttk.Combobox(root, values=maps_with_empty, state="readonly")
map_combobox.grid(row=0, column=1, padx=10, pady=5)
map_combobox.set("-- Select --")  # Default value

# Race Time Example Label
tk.Label(root, text="(Example Input - 1:23.45)", fg="gray").grid(row=0, column=3, columnspan=2, padx=10, pady=5)

# Azhan placement, kart, and time
tk.Label(root, text="Azhan Placement:").grid(row=1, column=0, padx=10, pady=5)
azhan_entry = ttk.Entry(root)
azhan_entry.grid(row=1, column=1, padx=10, pady=5)
azhan_kart_combobox = ttk.Combobox(root, values=karts_with_empty, state="readonly")
azhan_kart_combobox.grid(row=1, column=2, padx=10, pady=5)
azhan_kart_combobox.set("-- Select --")  # Default value
tk.Label(root, text="Azhan Race Time:").grid(row=1, column=3, padx=10, pady=5)
azhan_time_entry = ttk.Entry(root)
azhan_time_entry.grid(row=1, column=4, padx=10, pady=5)

# Raj placement, kart, and time
tk.Label(root, text="Raj Placement:").grid(row=2, column=0, padx=10, pady=5)
raj_entry = ttk.Entry(root)
raj_entry.grid(row=2, column=1, padx=10, pady=5)
raj_kart_combobox = ttk.Combobox(root, values=karts_with_empty, state="readonly")
raj_kart_combobox.grid(row=2, column=2, padx=10, pady=5)
raj_kart_combobox.set("-- Select --")  # Default value
tk.Label(root, text="Raj Race Time:").grid(row=2, column=3, padx=10, pady=5)
raj_time_entry = ttk.Entry(root)
raj_time_entry.grid(row=2, column=4, padx=10, pady=5)

# Sameer placement, kart, and time
tk.Label(root, text="Sameer Placement:").grid(row=3, column=0, padx=10, pady=5)
sameer_entry = ttk.Entry(root)
sameer_entry.grid(row=3, column=1, padx=10, pady=5)
sameer_kart_combobox = ttk.Combobox(root, values=karts_with_empty, state="readonly")
sameer_kart_combobox.grid(row=3, column=2, padx=10, pady=5)
sameer_kart_combobox.set("-- Select --")  # Default value
tk.Label(root, text="Sameer Race Time:").grid(row=3, column=3, padx=10, pady=5)
sameer_time_entry = ttk.Entry(root)
sameer_time_entry.grid(row=3, column=4, padx=10, pady=5)

# Log Button
log_button = tk.Button(root, text="Log Race", command=save_data)
log_button.grid(row=4, column=0, columnspan=5, pady=10)

# Status Label
status_label = tk.Label(root, text="")
status_label.grid(row=5, column=0, columnspan=5, pady=5)

root.mainloop()
