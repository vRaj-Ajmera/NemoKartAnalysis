import pandas as pd
import os
import matplotlib.pyplot as plt
import json

# Base directory and file paths
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
results_file = os.path.join(base_dir, "output/results.csv")
elo_tracker_file = os.path.join(base_dir, "output/elo_tracker.csv")
player_graphs_dir = os.path.join(base_dir, "output/player_graphs")

# Constants
BASE_ELO = 1000
K_FACTOR_INITIAL = 40  # Initial K-factor for the first 10 races
K_FACTOR_AFTER = 24  # Lower K-factor for subsequent races
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
    :param elo_ratings: Current Elo ratings (dict).
    :param race_results: DataFrame of players and their placements in a race.
    :param race_counts: Current number of races for each player (dict).
    :return: Updated Elo ratings (dict).
    """
    participants = race_results["Player"].tolist()
    placements = race_results["Placement"].tolist()

    # Calculate the number of known players
    known_players = [player for player in participants if player in elo_ratings]
    num_known = len(known_players)

    if num_known == 0:
        # If no known players, skip the Elo calculation
        return elo_ratings

    # Increment race counts for participants
    for player in participants:
        if player in elo_ratings:
            race_counts[player] += 1

    # Temporary structure to hold Elo changes
    elo_changes = {player: 0 for player in participants}

    # Pairwise comparisons based on placements
    for i, player_a in enumerate(participants):
        for j, player_b in enumerate(participants):
            if i != j:
                # Only calculate adjustments if both players are known
                if player_a in elo_ratings and player_b in elo_ratings:
                    expected_a = calculate_expected_score(elo_ratings[player_a], elo_ratings[player_b])
                    actual_a = 1 if placements[i] < placements[j] else 0  # Player A wins if placement is better (lower)
                    k_factor = determine_k_factor(race_counts[player_a])
                    
                    # Apply proportional adjustment based on known players
                    if (num_known == 1):
                        proportional_factor = 0.05
                    elif (num_known == 2):
                        proportional_factor = 0.35
                    elif (num_known == 3):
                        proportional_factor = 0.80
                    elif (num_known == 4):
                        proportional_factor = 0.95
                    elif (num_known >= 5 and num_known <= 7):
                        proportional_factor = 0.997
                    else:
                        proportional_factor = 1.0

                    elo_changes[player_a] += proportional_factor * k_factor * (actual_a - expected_a)

    # Apply Elo changes simultaneously
    for player in elo_changes:
        if player in elo_ratings:
            elo_ratings[player] += elo_changes[player]

    return elo_ratings


def process_races():
    """Process all races in results.csv and update Elo ratings in elo_tracker.csv."""
    # Load results
    results = load_csv(results_file)
    default_players = ["Raj", "Azhan", "Sameer", "Zetaa", "Adi", "Dylan", "Parum", "EnderRobot", "Lynden"]

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
    """Generate Elo progression graphs for each player, with all races in blue and last race of the day highlighted in red."""
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

        # Group Elo tracker by Date
        grouped = player_elo.groupby("Date")

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
