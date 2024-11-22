import pandas as pd
import os

# Define file paths
script_dir = os.path.dirname(__file__)
input_file = os.path.join(script_dir, "../output/results.csv")
output_file = os.path.join(script_dir, "../output/updated_results.csv")
players_file = os.path.join(script_dir, "../data/players.csv")

# Load existing results and players
results_df = pd.read_csv(input_file)
players_df = pd.read_csv(players_file)

# Get the list of players
players = players_df["Player Name"].tolist()

# Define the new column order
new_columns = ["Date", "Time", "Map Name"]
for player in players:
    new_columns += [
        f"{player} Placement",
        f"{player} Kart",
        f"{player} Racetime"
    ]

# Ensure all columns are present in the existing data
for player in players:
    for suffix in ["Placement", "Kart", "Racetime"]:
        column_name = f"{player} {suffix}"
        if column_name not in results_df.columns:
            results_df[column_name] = "DNR"  # Fill with "DNR" if column is missing

# Reorganize the columns
reorganized_df = results_df[new_columns]

# Save the updated results to a new CSV file
reorganized_df.to_csv(output_file, index=False)

print(f"Updated results file saved to: {output_file}")
