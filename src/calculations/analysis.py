import pandas as pd
import numpy as np
import os
import json

# Base directory
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# File paths
results_file = os.path.join(base_dir, "output/results.csv")
results_json_file = os.path.join(base_dir, "output/results.json")
post_analysis_file = os.path.join(base_dir, "output/post_analysis.json")
#post_analysis_file2 = os.path.join(base_dir, "docs/post_analysis.json")
players_file = os.path.join(base_dir, "data/players.csv")
maps_file = os.path.join(base_dir, "data/maps.csv")
karts_file = os.path.join(base_dir, "data/karts.csv")

# Load CSV files
def load_csv(file_path, default_columns=None):
    if not os.path.exists(file_path):
        if default_columns:
            print(f"{file_path} not found. Returning empty DataFrame.")
            return pd.DataFrame(columns=default_columns)
        else:
            print(f"{file_path} not found. Returning empty DataFrame.")
            return pd.DataFrame()
    return pd.read_csv(file_path)

# Load required data
def load_data():
    results = load_csv(results_file)
    players = load_csv(players_file, default_columns=["Player Name"])
    maps = load_csv(maps_file, default_columns=["Map Name"])
    karts = load_csv(karts_file, default_columns=["Kart Name"])
    return results, players, maps, karts

# Calculate points based on placement
def calculate_points(placement):
    points_table = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4}
    return points_table.get(placement, 0)

def calculate_daily_stats(df, players):
    """Calculate daily stats for players who raced on a given day."""
    daily_stats = {}
    for date in df["Date"].unique():
        daily_df = df[df["Date"] == date]
        stats_for_date = {}

        for player in players["Player Name"]:
            player_column = f"{player} Placement"
            pd.set_option('future.no_silent_downcasting', True)
            valid_placements = daily_df[player_column].replace("DNR", np.nan).dropna().astype(int)
            total_races = valid_placements.count()
            
            if total_races > 0:  # Only include players who raced
                total_points = valid_placements.apply(calculate_points).sum()
                ppr = total_points / total_races
                avg_position = valid_placements.mean()
                stats_for_date[player] = {
                    "Races": total_races,
                    "Points": total_points,
                    "PPR": round(ppr, 2),
                    "Avg Race Position": round(avg_position, 2)
                }

        # Only add the stats for this date if there are any players
        if stats_for_date:
            daily_stats[date] = stats_for_date

    return daily_stats

# Generate all-time stats
def calculate_all_time_stats(df, players):
    all_time_stats = {}
    for player in players["Player Name"]:
        player_column = f"{player} Placement"
        valid_placements = df[player_column].replace("DNR", np.nan).dropna().astype(int)
        total_races = valid_placements.count()
        total_points = valid_placements.apply(calculate_points).sum()
        ppr = total_points / total_races if total_races > 0 else 0
        avg_position = valid_placements.mean() if total_races > 0 else None
        all_time_stats[player] = {
            "Races": total_races,
            "Points": total_points,
            "PPR": round(ppr, 2),
            "Avg Race Position": round(avg_position, 2) if avg_position is not None else None
        }
    return all_time_stats

# Generate leaderboard for best race times
def calculate_best_race_times(df, maps, players):
    leaderboard = {}
    for map_name in maps["Map Name"]:
        map_df = df[df["Map Name"] == map_name]
        race_entries = []
        for _, row in map_df.iterrows():
            for player in players["Player Name"]:
                race_time_col = f"{player} Racetime"
                kart_col = f"{player} Kart"
                race_time = row.get(race_time_col)
                if race_time != "DNR" and pd.notna(race_time):
                    race_entries.append((race_time, f"{race_time} by {player} in {row.get(kart_col)}"))
        # Sort entries by race time (convert MM:SS.xx to seconds for sorting)
        race_entries.sort(key=lambda x: tuple(map(float, x[0].split(":"))))
        leaderboard[map_name] = [entry[1] for entry in race_entries[:10]]  # Top 10 times
    return leaderboard

def calculate_individual_best_times(df, maps, players):
    """Calculate each player's individual best time for each map, ordered from best to worst."""
    individual_best_times = {}
    for map_name in maps["Map Name"]:
        map_df = df[df["Map Name"] == map_name]
        player_best_times = {}

        for _, row in map_df.iterrows():
            for player in players["Player Name"]:
                race_time_col = f"{player} Racetime"
                kart_col = f"{player} Kart"
                race_time = row.get(race_time_col)

                if race_time != "DNR" and pd.notna(race_time):
                    time_in_seconds = sum(float(x) * 60 ** i for i, x in enumerate(reversed(race_time.split(":"))))
                    if player not in player_best_times or time_in_seconds < player_best_times[player]["time"]:
                        player_best_times[player] = {
                            "time": time_in_seconds,
                            "record": f"{race_time} by {player} in {row.get(kart_col)}"
                        }

        # Sort the best times from best to worst and save only the records
        sorted_best_times = sorted(player_best_times.values(), key=lambda x: x["time"])
        individual_best_times[map_name] = [data["record"] for data in sorted_best_times]

    return individual_best_times

def convert_results_to_json():
    """Convert results.csv to results.json while removing DNR rows."""
    
    if not os.path.exists(results_file):
        print(f"{results_file} not found. Ensure the file exists and try again.")
        return
    
    try:
        # Read the CSV file
        results_df = pd.read_csv(results_file)
        
        # Function to filter out "DNR" entries in each row
        def filter_dnr(row):
            filtered_row = {
                key: value
                for key, value in row.items()
                if not (isinstance(value, str) and value == "DNR")
            }
            return filtered_row

        # Apply the filtering to each row
        filtered_results = [filter_dnr(row) for row in results_df.to_dict(orient="records")]
        
        # Write the filtered results to JSON
        with open(results_json_file, "w") as json_file:
            json.dump(filtered_results, json_file, indent=4)
        
        print(f"Results successfully converted to JSON and saved to {results_json_file}.")
    except Exception as e:
        print(f"An error occurred while converting results to JSON: {e}")


# Main function to generate post_analysis.json
def main():
    results, players, maps, karts = load_data()
    if results.empty:
        print("No results found. Exiting analysis.")
        return

    post_analysis = {
        "Daily Stats": calculate_daily_stats(results, players),
        "All Time Stats": calculate_all_time_stats(results, players),
        "Legend": {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4},
        "Best Race Times": calculate_best_race_times(results, maps, players),
        "Individual Player Best Times": calculate_individual_best_times(results, maps, players)
    }

    convert_results_to_json()

    # Ensure JSON serializable
    def convert_to_serializable(obj):
        if isinstance(obj, (np.integer, int)):
            return int(obj)
        elif isinstance(obj, (np.floating, float)):
            return float(obj)
        elif isinstance(obj, pd.Timestamp):
            return str(obj)
        return obj

    # Write to post_analysis.json
    with open(post_analysis_file, "w") as json_file:
        json.dump(post_analysis, json_file, indent=4, default=convert_to_serializable)

    print(f"Post analysis saved to {post_analysis_file}")

if __name__ == "__main__":
    main()
