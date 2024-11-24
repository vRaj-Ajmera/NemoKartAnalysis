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
players_file = os.path.join(script_dir, "../data/players.csv")
output_file = os.path.join(script_dir, "../output/dummy_results.csv")

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
    expected_columns = ["Date", "Time", "Map Name"] + \
                       [f"{player} Placement" for player in players] + \
                       [f"{player} Kart" for player in players] + \
                       [f"{player} Racetime" for player in players]

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
    if not race_time or ":" not in race_time:
        return False, f"Race time for {player} must be in the format MM:SS.xx."
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

# GUI Setup
root = tk.Tk()
root.title(f"Nemokart Race Logger - Logging to: {os.path.basename(output_file)}")

# Map Selection
tk.Label(root, text="Select Map:").grid(row=0, column=0, padx=10, pady=5)
map_combobox = ttk.Combobox(root, values=maps_with_empty, state="readonly", width=20)
map_combobox.grid(row=0, column=1, padx=10, pady=5)
map_combobox.set("-- Select --")

tk.Label(root, text="(Example Input - 1:23.45)", fg="gray").grid(row=0, column=2, columnspan=2, padx=10, pady=5)

# Dynamic Player Rows
player_widgets = []
for i in range(len(players)):
    player = tk.StringVar(value="-- Select --")
    placement = tk.StringVar(value="-- Select --")
    kart = tk.StringVar(value="-- Select --")

    ttk.Combobox(root, textvariable=player, values=["-- Select --"] + players, state="readonly", width=20).grid(row=i + 1, column=0, padx=10, pady=5)
    ttk.Combobox(root, textvariable=placement, values=[f"{x}" for x in range(1, 9)], state="readonly", width=10).grid(row=i + 1, column=1, padx=10, pady=5)
    ttk.Combobox(root, textvariable=kart, values=karts_with_empty, state="readonly", width=20).grid(row=i + 1, column=2, padx=10, pady=5)
    race_time_entry = tk.Entry(root, width=15)
    race_time_entry.grid(row=i + 1, column=3, padx=10, pady=5)

    player_widgets.append({"player": player, "placement": placement, "kart": kart, "race_time": race_time_entry})

# Log Button
tk.Button(root, text="Log Race", command=save_data).grid(row=len(players) + 1, column=0, columnspan=4, pady=10)

# Status Label
status_label = tk.Label(root, text="", fg="green")
status_label.grid(row=len(players) + 2, column=0, columnspan=4, pady=5)

root.mainloop()
