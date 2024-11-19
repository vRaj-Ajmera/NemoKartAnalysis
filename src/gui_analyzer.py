import tkinter as tk
from tkinter import ttk
import pandas as pd
import os
import datetime

# Get the directory of the current script
script_dir = os.path.dirname(__file__)

# Relative path to results.csv
results_file = os.path.join(script_dir, "../output/results.csv")

# Load results data
def load_results():
    if not os.path.exists(results_file):
        return pd.DataFrame(columns=["Date", "Time", "Map Name", "Azhan Placement", "Raj Placement",
                                     "Sameer Placement", "Azhan Kart", "Raj Kart", "Sameer Kart"])
    return pd.read_csv(results_file)

# Calculate points based on placement
def calculate_points(placement):
    points_table = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4}
    return points_table.get(placement, 0)

# Analyze data
def analyze_data():
    df = load_results()

    if df.empty:
        update_table(daily_table, [])
        update_table(total_table, [])
        return

    # Get selected date or default to today
    selected_date = date_combobox.get()
    if selected_date == "All":
        selected_date = df["Date"].max()  # Default to most recent date if "All" is selected

    # Calculate stats for a player
    def calculate_player_stats(df, player_column):
        valid_placements = df[player_column].apply(lambda x: int(x) if str(x).isdigit() and 1 <= int(x) <= 8 else None)
        total_races = valid_placements.notna().sum()
        total_points = valid_placements.dropna().apply(calculate_points).sum()
        avg_points = total_points / total_races if total_races > 0 else 0
        return total_races, total_points, avg_points

    # Daily stats
    daily_df = df[df["Date"] == selected_date]
    daily_azhan = calculate_player_stats(daily_df, "Azhan Placement")
    daily_raj = calculate_player_stats(daily_df, "Raj Placement")
    daily_sameer = calculate_player_stats(daily_df, "Sameer Placement")

    # Total stats
    azhan_total = calculate_player_stats(df, "Azhan Placement")
    raj_total = calculate_player_stats(df, "Raj Placement")
    sameer_total = calculate_player_stats(df, "Sameer Placement")

    # Update tables
    update_table(
        daily_table,
        [
            ["Azhan", daily_azhan[0], daily_azhan[1], f"{daily_azhan[2]:.2f}"],
            ["Raj", daily_raj[0], daily_raj[1], f"{daily_raj[2]:.2f}"],
            ["Sameer", daily_sameer[0], daily_sameer[1], f"{daily_sameer[2]:.2f}"],
        ]
    )

    update_table(
        total_table,
        [
            ["Azhan", azhan_total[0], azhan_total[1], f"{azhan_total[2]:.2f}"],
            ["Raj", raj_total[0], raj_total[1], f"{raj_total[2]:.2f}"],
            ["Sameer", sameer_total[0], sameer_total[1], f"{sameer_total[2]:.2f}"],
        ]
    )

# Update table data
def update_table(table, data):
    # Clear existing data
    for row in table.get_children():
        table.delete(row)
    # Insert new data
    for row in data:
        table.insert("", "end", values=row)

# GUI setup
root = tk.Tk()
root.title("Nemokart Data Analyzer")

# Date Selection Frame
date_frame = tk.Frame(root, padx=5, pady=5)
date_frame.grid(row=0, column=0, columnspan=2, sticky="ew")

tk.Label(date_frame, text="Select Date:").pack(side="left", padx=5)
dates = load_results()["Date"].unique().tolist()
dates = ["All"] + dates
today_date = datetime.datetime.now().strftime("%Y-%m-%d")

date_combobox = ttk.Combobox(date_frame, values=dates, state="readonly", width=10)
date_combobox.set(today_date if today_date in dates else "All")
date_combobox.pack(side="left", padx=5)

analyze_button = tk.Button(date_frame, text="Analyze", command=analyze_data, width=10)
analyze_button.pack(side="left", padx=5)

# Daily Stats Frame
daily_frame = tk.LabelFrame(root, text="Daily Stats", padx=5, pady=5)
daily_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

daily_table = ttk.Treeview(daily_frame, columns=("Player", "Races", "Points", "PPR"), show="headings", height=4)
daily_table.heading("Player", text="Player")
daily_table.heading("Races", text="Races")
daily_table.heading("Points", text="Points")
daily_table.heading("PPR", text="PPR")
daily_table.column("Player", width=80, anchor="center")
daily_table.column("Races", width=50, anchor="center")
daily_table.column("Points", width=50, anchor="center")
daily_table.column("PPR", width=50, anchor="center")
daily_table.pack(fill="both", expand=True)

# Total Stats Frame
total_frame = tk.LabelFrame(root, text="Total Stats", padx=5, pady=5)
total_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

total_table = ttk.Treeview(total_frame, columns=("Player", "Races", "Points", "PPR"), show="headings", height=4)
total_table.heading("Player", text="Player")
total_table.heading("Races", text="Races")
total_table.heading("Points", text="Points")
total_table.heading("PPR", text="PPR")
total_table.column("Player", width=80, anchor="center")
total_table.column("Races", width=50, anchor="center")
total_table.column("Points", width=50, anchor="center")
total_table.column("PPR", width=50, anchor="center")
total_table.pack(fill="both", expand=True)

# Legend Frame
legend_frame = tk.LabelFrame(root, text="Legend", padx=5, pady=5)
legend_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

legend_table = ttk.Treeview(legend_frame, columns=("Placement", "Points"), show="headings", height=8)
legend_table.heading("Placement", text="Placement")
legend_table.heading("Points", text="Points")
legend_table.column("Placement", width=80, anchor="center")
legend_table.column("Points", width=80, anchor="center")
legend_table.pack(fill="both", expand=True)

# Populate legend table
legend_data = [
    (1, 25), (2, 18), (3, 15), (4, 12),
    (5, 10), (6, 8), (7, 6), (8, 4)
]
update_table(legend_table, legend_data)

# Run initial analysis
analyze_data()

root.mainloop()
