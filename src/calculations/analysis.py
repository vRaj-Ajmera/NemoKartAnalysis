import pandas as pd
import numpy as np
import os
import json

# Base directory
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# File paths
results_file = os.path.join(base_dir, "output/dummy_results.csv")
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

# Generate daily stats
def calculate_daily_stats(df, players):
    daily_stats = {}
    for date in df["Date"].unique():
        daily_df = df[df["Date"] == date]
        stats_for_date = {}
        for player in players["Player Name"]:
            player_column = f"{player} Placement"
            valid_placements = daily_df[player_column].replace("DNR", np.nan).dropna().astype(int)
            total_races = valid_placements.count()
            total_points = valid_placements.apply(calculate_points).sum()
            ppr = total_points / total_races if total_races > 0 else 0
            avg_position = valid_placements.mean() if total_races > 0 else None
            stats_for_date[player] = {
                "Races": total_races,
                "Points": total_points,
                "PPR": round(ppr, 2),
                "Avg Race Position": round(avg_position, 2) if avg_position is not None else None
            }
        daily_stats[date] = stats_for_date
    return daily_stats

# Generate stats for races where all players participated
def calculate_together_stats(df, players):
    together_stats = {}
    player_columns = [f"{player} Placement" for player in players["Player Name"]]
    together_df = df.dropna(subset=player_columns)  # Drop rows with missing data for any player
    together_df = together_df[~together_df[player_columns].isin(["DNR"]).any(axis=1)]  # Exclude races with "DNR"

    for player in players["Player Name"]:
        player_column = f"{player} Placement"
        valid_placements = together_df[player_column].replace("DNR", np.nan).dropna().astype(int)
        total_races = valid_placements.count()
        total_points = valid_placements.apply(calculate_points).sum()
        ppr = total_points / total_races if total_races > 0 else 0
        avg_position = valid_placements.mean() if total_races > 0 else None
        together_stats[player] = {
            "Races": total_races,
            "Points": total_points,
            "PPR": round(ppr, 2),
            "Avg Race Position": round(avg_position, 2) if avg_position is not None else None
        }
    return together_stats

# Generate stats for races where Raj, Azhan, and Sameer participated together
def calculate_together_stats_RAS(df):
    target_players = ["Raj", "Azhan", "Sameer"]  # Specify the players to track
    player_columns = [f"{player} Placement" for player in target_players]
    
    # Filter rows where all specified players have valid placements (no "DNR")
    together_df = df.dropna(subset=player_columns)  # Drop rows with missing data for target players
    together_df = together_df[~together_df[player_columns].isin(["DNR"]).any(axis=1)]  # Exclude races with "DNR"

    together_stats = {}
    for player in target_players:
        player_column = f"{player} Placement"
        valid_placements = together_df[player_column].replace("DNR", np.nan).dropna().astype(int)
        total_races = valid_placements.count()
        total_points = valid_placements.apply(calculate_points).sum()
        ppr = total_points / total_races if total_races > 0 else 0
        avg_position = valid_placements.mean() if total_races > 0 else None
        together_stats[player] = {
            "Races": total_races,
            "Points": total_points,
            "PPR": round(ppr, 2),
            "Avg Race Position": round(avg_position, 2) if avg_position is not None else None
        }
    return together_stats


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

# Main function to generate post_analysis.json
def main():
    results, players, maps, karts = load_data()
    if results.empty:
        print("No results found. Exiting analysis.")
        return

    post_analysis = {
        "Daily Stats": calculate_daily_stats(results, players),
        "Races Together": calculate_together_stats_RAS(results),
        "All Time Stats": calculate_all_time_stats(results, players),
        "Legend": {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4},
        "Best Race Times": calculate_best_race_times(results, maps, players)
    }

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
