import pandas as pd
import os
import matplotlib.pyplot as plt
import json

# Base directory and file paths
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
results_file = os.path.join(base_dir, "output/results.csv")
players_file = os.path.join(base_dir, "data/players.csv")
elo_tracker_file = os.path.join(base_dir, "output/elo_tracker.csv")
maps_file = os.path.join(base_dir, "data/maps.csv")
player_graphs_dir = os.path.join(base_dir, "output/player_graphs")

# Constants
UNKNOWN_PLAYER_ELO = 2000
BASE_ELO = 1000
K_FACTOR_INITIAL = 24  # Initial K-factor for the first 10 races
K_FACTOR_AFTER = 8  # Lower K-factor for subsequent races
MAX_RACERS = 8

# Create the player_graphs directory if it doesn't exist
os.makedirs(player_graphs_dir, exist_ok=True)

def load_csv(file_path, default_columns=None):
    """Load a CSV file, creating a new DataFrame if it doesn't exist."""
    if not os.path.exists(file_path):
        if default_columns:
            return pd.DataFrame(columns=default_columns)
        else:
            return pd.DataFrame()
    return pd.read_csv(file_path)

# Calculate points based on placement
def calculate_points(placement):
    points_table = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4}
    return points_table.get(placement, 0)

def process_kart_usage(player, results):
    """Calculate the top 5 karts used by a player for each map."""
    player_kart_stats = {}

    maps_list = load_csv(maps_file)
    for map_name in maps_list["Map Name"]:
        map_results = results[results["Map Name"] == map_name]
        kart_usage = {}

        for _, row in map_results.iterrows():
            placement_col = f"{player} Placement"
            kart_col = f"{player} Kart"
            racetime_col = f"{player} Racetime"

            if placement_col in row and kart_col in row and racetime_col in row:
                placement = row[placement_col]
                kart = row[kart_col]
                racetime = row[racetime_col]

                if placement != "DNR" and kart != "DNR" and racetime != "DNR":
                    # Initialize kart stats
                    if kart not in kart_usage:
                        kart_usage[kart] = {"Races": 0, "Points": 0, "Positions": [], "Times": []}
                    
                    # Update stats
                    kart_usage[kart]["Races"] += 1
                    kart_usage[kart]["Points"] += calculate_points(int(placement))
                    kart_usage[kart]["Positions"].append(int(placement))
                    
                    # Convert racetime to seconds
                    time_parts = racetime.split(":")
                    kart_time = float(time_parts[0]) * 60 + float(time_parts[1])
                    kart_usage[kart]["Times"].append(kart_time)

        # Compute aggregated stats for each kart
        kart_stats = []
        for kart, stats in kart_usage.items():
            avg_position = sum(stats["Positions"]) / len(stats["Positions"])
            ppr = stats["Points"] / stats["Races"]  # Points per race
            kart_stats.append({
                "Kart": kart,
                "Races": stats["Races"],
                "Points": stats["Points"],
                "PPR": round(ppr, 2),
                "Avg Position": round(avg_position, 2),
            })

        # Sort by PPR and take the top 5
        kart_stats = sorted(kart_stats, key=lambda x: x["Races"], reverse=True)[:5]
        player_kart_stats[map_name] = kart_stats

    return player_kart_stats

def initialize_elo_tracker(results, default_players):
    """Initialize the Elo tracker file if it doesn't exist."""
    if not os.path.exists(elo_tracker_file):
        # Create a new DataFrame with the correct headers
        columns = ["Date", "Time", "Map Name"] + default_players
        elo_tracker = pd.DataFrame(columns=columns)
        elo_tracker.to_csv(elo_tracker_file, index=False)
        print(f"Initialized elo_tracker.csv with columns: {columns}")

def calculate_expected_score(elo_a, elo_b):
    """Calculate the expected score between two players."""
    return 1 / (1 + 10 ** ((elo_b - elo_a) / 400))

def determine_k_factor(player_race_count):
    """Determine the K-factor based on the player's number of races."""
    return K_FACTOR_INITIAL if player_race_count <= 10 else K_FACTOR_AFTER

def update_elo_ratings(elo_ratings, race_results, race_counts):
    """
    Update Elo ratings for a single race with dynamic K-factor scaling and proportional adjustments.
    Assumes unknown players have a default rating and accounts for their placements.
    :param elo_ratings: Current Elo ratings (dict).
    :param race_results: DataFrame of players and their placements in a race.
    :param race_counts: Current number of races for each player (dict).
    :return: Updated Elo ratings (dict).
    """
    participants = race_results["Player"].tolist()
    placements = race_results["Placement"].tolist()

    # Calculate the number of known players
    num_known = len(participants)

    all_racers_list = [f"Unknown_{i}" for i in range(MAX_RACERS)]
    all_placements_list = list(range(1, MAX_RACERS + 1))

    for i in range(len(participants)):
        placement = placements[i]
        all_racers_list[placement-1] = participants[i]

    # Add unknown players to participants and placements
    participants = all_racers_list
    placements = all_placements_list

    # Increment race counts for known participants
    for player in participants:
        if player in elo_ratings:
            race_counts[player] += 1

    # Temporary structure to hold Elo changes
    elo_changes = {player: 0 for player in participants}
    unknown_elo = UNKNOWN_PLAYER_ELO

    # Define proportionality factors based on the number of known players
    if num_known == 1:
        proportional_factor = 0.3  # Single known player -> very low Elo adjustment
    elif num_known == 2:
        proportional_factor = 0.65  # Two known players -> moderate adjustment
    elif num_known == 3:
        proportional_factor = 0.95  # Three known players -> stronger adjustment
    elif 4 <= num_known <= 7:
        proportional_factor = 0.997  # Five to seven known players -> high adjustment
    else:
        proportional_factor = 1.0  # All players are known -> full adjustment

    # Pairwise comparisons based on placements
    for i, player_a in enumerate(participants):
        for j, player_b in enumerate(participants):
            if i != j:
                # Determine Elo values for each participant
                elo_a = elo_ratings[player_a] if player_a in elo_ratings else unknown_elo
                elo_b = elo_ratings[player_b] if player_b in elo_ratings else unknown_elo

                # Calculate expected score and actual score
                expected_a = calculate_expected_score(elo_a, elo_b)
                actual_a = 1 if placements[i] < placements[j] else 0  # Player A wins if placement is better (lower)

                # Apply K-factor scaling for known players
                if player_a in elo_ratings:
                    k_factor = determine_k_factor(race_counts[player_a])
                    elo_changes[player_a] += (
                        proportional_factor * k_factor * (actual_a - expected_a)
                    )

    # Apply Elo changes simultaneously
    for player in elo_changes:
        if player in elo_ratings:
            elo_ratings[player] += elo_changes[player]

    return elo_ratings



def process_races():
    """Process all races in results.csv and update Elo ratings in elo_tracker.csv."""
    # Load results
    results = load_csv(results_file)
    players = load_csv(players_file, default_columns=["Player Name"])
    maps = load_csv(maps_file, default_columns=["Map Name"])
    default_players = players["Player Name"].tolist()
    map_list = maps["Map Name"].tolist()

    # Clear and initialize the elo_tracker
    columns = ["Date", "Time", "Map Name"] + default_players
    elo_tracker = pd.DataFrame(columns=columns)
    elo_tracker.to_csv(elo_tracker_file, index=False)  # Save the cleared file

    # Initialize Elo ratings with BASE_ELO and race counts
    current_elo = {player: BASE_ELO for player in default_players}
    race_counts = {player: 0 for player in default_players}  # Tracks the number of races per player
    peak_elo = {player: BASE_ELO for player in default_players}

    # Process each race
    for _, race in results.iterrows():
        race_date = race["Date"]
        race_time = race["Time"]
        map_name = race["Map Name"]

        # Extract race participants and their placements
        race_results = []
        for player in default_players:
            placement_col = f"{player} Placement"
            if placement_col in race and race[placement_col] != "DNR":
                race_results.append({"Player": player, "Placement": int(race[placement_col])})
                race_counts[player] += 1  # Increment race count

        if not race_results:  # Skip if no participants
            continue

        # Update Elo ratings based on this race
        race_results_df = pd.DataFrame(race_results)
        current_elo = update_elo_ratings(current_elo, race_results_df, race_counts)

        # Update peak Elo for each player
        for player in default_players:
            peak_elo[player] = max(peak_elo[player], current_elo[player])

        # Create a new row for this race in the Elo tracker
        new_row = {
            "Date": race_date,
            "Time": race_time,
            "Map Name": map_name,
            **{player: current_elo[player] for player in default_players}
        }
        if elo_tracker.empty:
            elo_tracker = pd.DataFrame([new_row])
        else:
            elo_tracker = pd.concat([elo_tracker, pd.DataFrame([new_row])], ignore_index=True)

    # Save updated Elo tracker
    elo_tracker.to_csv(elo_tracker_file, index=False)
    print(f"Elo tracker updated and saved to {elo_tracker_file}")

    # Generate Elo graphs
    generate_elo_graphs(default_players)

    # Generate Elo post-analysis JSON
    elo_post_analysis = {
        "Player Ratings": {
            player: {
                "Peak Rating": round(peak_elo[player]),
                "Current Rating": round(current_elo[player]),
                "Kart Usage": process_kart_usage(player, results)  # Add kart usage stats here
            }
            for player in default_players
        }
    }

    # Save Elo post-analysis to JSON file
    elo_post_analysis_file = os.path.join(base_dir, "output/elo_post_analysis.json")
    with open(elo_post_analysis_file, "w") as json_file:
        json.dump(elo_post_analysis, json_file, indent=4)
    print(f"Elo post-analysis saved to {elo_post_analysis_file}")



def generate_elo_graphs(default_players):
    """Generate Elo progression graphs for each player, with the most recent 5 race days."""
    # Load elo_tracker and results
    elo_tracker = load_csv(elo_tracker_file)
    results = load_csv(results_file)

    # Ensure Date columns are treated as datetime objects
    elo_tracker["Date"] = pd.to_datetime(elo_tracker["Date"])
    results["Date"] = pd.to_datetime(results["Date"])

    for player in default_players:
        # Skip if player column is not in the tracker
        if player not in elo_tracker.columns:
            continue

        # Determine the player's participation days
        player_column = f"{player} Placement"
        valid_results = results.dropna(subset=[player_column])  # Drop rows where player did not participate
        valid_results = valid_results[valid_results[player_column] != "DNR"]  # Exclude "DNR"

        if valid_results.empty:
            # Skip graph generation if the player never participated
            continue

        # Get the participation dates
        participation_dates = valid_results["Date"].unique()

        # Filter Elo tracker for the player's participation days only
        player_elo = elo_tracker[elo_tracker["Date"].isin(participation_dates)][["Date", player]]

        # Get the most recent 5 unique dates
        recent_dates = sorted(player_elo["Date"].unique())[-6:]
        recent_player_elo = player_elo[player_elo["Date"].isin(recent_dates)]

        # Group Elo tracker by Date
        grouped = recent_player_elo.groupby("Date")

        # Initialize lists to store data for plotting
        all_dates = []
        all_elos = []
        last_dates = []
        last_elos = []

        for date, group in grouped:
            all_dates.extend(group["Date"])
            all_elos.extend(group[player])
            last_dates.append(group["Date"].iloc[-1])  # Last entry for the day
            last_elos.append(group[player].iloc[-1])  # Last Elo for the day

        # Generate Elo graph for the player
        plt.figure(figsize=(8, 5))  # Adjusted size for smaller graph

        # Plot all Elo points for the player in blue triangles
        plt.plot(all_dates, all_elos, marker="^", linestyle="--", color="blue", label="All Races")

        # Highlight the last Elo point of each day in red
        plt.scatter(last_dates, last_elos, color="red", label="End of Day Rating", zorder=5)

        # Add a red dotted line connecting the end-of-day ratings
        plt.plot(last_dates, last_elos, linestyle=":", color="red", linewidth=2, label="Day-to-Day Progression")

        plt.title(f"Elo Progression: {player}", fontsize=14, fontweight='bold', color='black')
        plt.xlabel("Date", fontsize=12, fontweight='bold', color='black')
        plt.ylabel("Elo Rating", fontsize=12, fontweight='bold', color='black')
        plt.xticks(rotation=45, fontsize=10, color='black')
        plt.yticks(fontsize=10, color='black')
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.legend(loc="best")
        plt.tight_layout()

        # Save the graph to player_graphs directory
        graph_path = os.path.join(player_graphs_dir, f"{player}_elo_progression.png")
        plt.savefig(graph_path, dpi=150)  # High-resolution graph
        plt.close()
        print(f"Saved Elo graph for {player} at {graph_path}")



def main():
    process_races()

if __name__ == "__main__":
    main()
