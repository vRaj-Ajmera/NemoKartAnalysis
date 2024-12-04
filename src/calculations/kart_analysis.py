import pandas as pd
import os
import json

# Base directory and file paths
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
results_file = os.path.join(base_dir, "output/results.csv")
elo_tracker_file = os.path.join(base_dir, "output/elo_tracker.csv")
kart_leaderboards_file = os.path.join(base_dir, "output/kart_leaderboards.json")
kart_adjacency_file = os.path.join(base_dir, "output/kart_adjacency.json")

# Constants
DEFAULT_ELO = 1000  # Default Elo rating for normalization

def load_csv(file_path, default_columns=None):
    """Load a CSV file, creating a new DataFrame if it doesn't exist."""
    if not os.path.exists(file_path):
        if default_columns:
            return pd.DataFrame(columns=default_columns)
        else:
            return pd.DataFrame()
    return pd.read_csv(file_path)

def compute_kart_leaderboard(map_name, map_results, elo_data, karts_list):
    """Compute the top 5 karts for a given map."""
    kart_stats = {kart: {"score": 0, "races": 0} for kart in karts_list}

    # Filter map_results by the specified map_name
    map_specific_results = map_results[map_results["Map Name"] == map_name]

    # Loop through each race on the map
    for _, race in map_specific_results.iterrows():
        for kart in karts_list:
            placement_col = f"{kart} Placement"
            if placement_col in race and race[placement_col] != "DNR":
                placement = race[placement_col]
                player_col = f"{kart} Player"
                player = race.get(player_col, None)

                # Get player's Elo at the time of the race
                if player and player in elo_data:
                    player_elo = float(elo_data[player])
                else:
                    player_elo = DEFAULT_ELO  # Default Elo if player data is missing

                # Normalize performance by Elo and placement
                placement = int(placement)
                kart_score = (player_elo / DEFAULT_ELO) * (1 / placement)

                kart_stats[kart]["score"] += kart_score
                kart_stats[kart]["races"] += 1

    # Compute average score and normalize to 0–100
    for kart in kart_stats:
        if kart_stats[kart]["races"] > 0:
            avg_score = kart_stats[kart]["score"] / kart_stats[kart]["races"]
            kart_stats[kart]["average_score"] = avg_score * 100  # Normalize to 0–100
        else:
            kart_stats[kart]["average_score"] = 0

    # Sort and return the top 5 karts
    sorted_karts = sorted(kart_stats.items(), key=lambda x: x[1]["average_score"], reverse=True)
    return [{"kart": kart, "average_score": stats["average_score"]} for kart, stats in sorted_karts[:5]]

def compute_kart_adjacency_matrix(map_name, map_results, elo_data, karts_list):
    """Compute the adjacency matrix of kart pairwise performance."""
    kart_pairs = {kart: {other_kart: {"win": 0, "loss": 0} for other_kart in karts_list} for kart in karts_list}

    for _, race in map_results.iterrows():
        placements = {kart: race.get(f"{kart} Placement", None) for kart in karts_list}
        elos = {kart: float(elo_data.get(race.get(f"{kart} Player", ""), DEFAULT_ELO)) for kart in karts_list}

        # Pairwise comparison for each kart
        for kart_a in karts_list:
            for kart_b in karts_list:
                if kart_a == kart_b:
                    continue

                placement_a, placement_b = placements[kart_a], placements[kart_b]
                if placement_a is None or placement_b is None or placement_a == "DNR" or placement_b == "DNR":
                    continue

                placement_a, placement_b = int(placement_a), int(placement_b)
                if placement_a < placement_b:
                    kart_pairs[kart_a][kart_b]["win"] += 1
                else:
                    kart_pairs[kart_a][kart_b]["loss"] += 1

    # Normalize pairwise scores to a scale of 1–10
    adjacency_matrix = {}
    for kart_a, comparisons in kart_pairs.items():
        adjacency_matrix[kart_a] = {}
        for kart_b, results in comparisons.items():
            total = results["win"] + results["loss"]
            if total == 0:
                adjacency_matrix[kart_a][kart_b] = "DNR"  # No races
            else:
                win_rate = results["win"] / total
                adjacency_matrix[kart_a][kart_b] = round(win_rate * 10, 2)  # Scale to 1–10

    return adjacency_matrix


def main():
    # Load necessary data
    results = load_csv(results_file)
    elo_tracker = load_csv(elo_tracker_file)
    karts_data = load_csv(os.path.join(base_dir, "data/karts.csv"))

    # Extract kart list from karts.csv
    karts_list = karts_data["Kart Name"].tolist()

    # Get player Elo ratings
    elo_data = {}
    if not elo_tracker.empty:
        for _, row in elo_tracker.iterrows():
            for player, elo in row.items():
                if player not in ["Date", "Time", "Map Name"]:
                    elo_data[player] = elo

    # Get unique maps from results
    unique_maps = results["Map Name"].unique()

    # Initialize JSON outputs
    kart_leaderboards = {}
    kart_adjacency = {}

    # Process each map
    for map_name in unique_maps:
        map_results = results[results["Map Name"] == map_name]

        # Compute leaderboard and adjacency matrix
        kart_leaderboards[map_name] = compute_kart_leaderboard(map_name, map_results, elo_data, karts_list)
        kart_adjacency[map_name] = compute_kart_adjacency_matrix(map_name, map_results, elo_data, karts_list)

    # Save results to JSON files
    with open(kart_leaderboards_file, "w") as leaderboard_file:
        json.dump(kart_leaderboards, leaderboard_file, indent=4)
    with open(kart_adjacency_file, "w") as adjacency_file:
        json.dump(kart_adjacency, adjacency_file, indent=4)

    print(f"Kart leaderboards saved to {kart_leaderboards_file}")
    print(f"Kart adjacency matrix saved to {kart_adjacency_file}")

if __name__ == "__main__":
    main()

