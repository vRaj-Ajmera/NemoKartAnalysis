import pandas as pd
import os
import matplotlib.pyplot as plt
import json
from trueskill import Rating, rate, setup

# Base directory and file paths
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
results_file = os.path.join(base_dir, "output/results.csv")
players_file = os.path.join(base_dir, "data/players.csv")
trueskill_tracker_file = os.path.join(base_dir, "output/trueskill_tracker.csv")
player_graphs_dir = os.path.join(base_dir, "output/player_graphs")

# TrueSkill environment setup
setup(draw_probability=0.00)  # Assumes no ties in races

# Constants
DEFAULT_MU = 1000  # Default skill mean
DEFAULT_SIGMA = 333  # Default skill standard deviation
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

def initialize_trueskill_tracker(results, default_players):
    """Initialize the TrueSkill tracker file if it doesn't exist."""
    if not os.path.exists(trueskill_tracker_file):
        # Create a new DataFrame with the correct headers
        columns = ["Date", "Time", "Map Name"] + default_players
        trueskill_tracker = pd.DataFrame(columns=columns)
        trueskill_tracker.to_csv(trueskill_tracker_file, index=False)
        print(f"Initialized trueskill_tracker.csv with columns: {columns}")

def update_trueskill_ratings(ratings, race_results):
    """
    Update TrueSkill ratings based on race results.
    :param ratings: Current TrueSkill ratings (dict of `trueskill.Rating` objects).
    :param race_results: DataFrame of players and their placements in a race.
    :return: Updated TrueSkill ratings (dict).
    """
    # Prepare the race results for TrueSkill
    ranked_groups = []
    for placement in sorted(race_results["Placement"].unique()):
        group = [
            ratings[player]
            for player in race_results.loc[race_results["Placement"] == placement, "Player"]
        ]
        ranked_groups.append(group)
    
    # Update the ratings using TrueSkill
    new_ratings = rate(ranked_groups)
    
    # Update the original ratings dictionary
    flattened_results = race_results.sort_values(by="Placement")["Player"].tolist()
    updated_ratings = {player: new_ratings[i // len(group)][i % len(group)] for i, group in enumerate(ranked_groups) for player in group}

    return updated_ratings

def process_races():
    """Process all races in results.csv and update TrueSkill ratings in trueskill_tracker.csv."""
    # Load results and players
    results = load_csv(results_file)
    players = load_csv(players_file, default_columns=["Player Name"])
    default_players = players["Player Name"].tolist()

    # Clear and initialize the trueskill_tracker
    columns = ["Date", "Time", "Map Name"] + default_players
    trueskill_tracker = pd.DataFrame(columns=columns)
    trueskill_tracker.to_csv(trueskill_tracker_file, index=False)  # Save the cleared file

    # Initialize TrueSkill ratings for players
    current_ratings = {player: Rating(mu=DEFAULT_MU, sigma=DEFAULT_SIGMA) for player in default_players}

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

        if not race_results:  # Skip if no participants
            continue

        # Update TrueSkill ratings based on this race
        race_results_df = pd.DataFrame(race_results)
        current_ratings = update_trueskill_ratings(current_ratings, race_results_df)

        # Create a new row for this race in the TrueSkill tracker
        new_row = {
            "Date": race_date,
            "Time": race_time,
            "Map Name": map_name,
            **{player: current_ratings[player].mu for player in default_players}
        }
        if trueskill_tracker.empty:
            trueskill_tracker = pd.DataFrame([new_row])
        else:
            trueskill_tracker = pd.concat([trueskill_tracker, pd.DataFrame([new_row])], ignore_index=True)

    # Save updated TrueSkill tracker
    trueskill_tracker.to_csv(trueskill_tracker_file, index=False)
    print(f"TrueSkill tracker updated and saved to {trueskill_tracker_file}")

    # Generate TrueSkill graphs
    generate_trueskill_graphs(default_players)

def generate_trueskill_graphs(default_players):
    """Generate TrueSkill progression graphs for each player."""
    # Load trueskill_tracker
    trueskill_tracker = load_csv(trueskill_tracker_file)

    # Ensure Date column is treated as a datetime object
    trueskill_tracker["Date"] = pd.to_datetime(trueskill_tracker["Date"])

    for player in default_players:
        # Skip if player column is not in the tracker
        if player not in trueskill_tracker.columns:
            continue

        # Group by Date and take the last TrueSkill value of each day
        daily_trueskill = (
            trueskill_tracker.groupby("Date")[player]
            .last()
            .reset_index()
        )

        # Generate TrueSkill graph for the player
        plt.figure(figsize=(8, 5))
        plt.plot(
            daily_trueskill["Date"], daily_trueskill[player],
            marker="^", linestyle="--", color="blue", label="TrueSkill Rating"
        )
        plt.title(f"TrueSkill Progression: {player}", fontsize=14, fontweight='bold', color='black')
        plt.xlabel("Date", fontsize=12, fontweight='bold', color='black')
        plt.ylabel("TrueSkill Rating (μ)", fontsize=12, fontweight='bold', color='black')
        plt.xticks(rotation=45, fontsize=10, color='black')
        plt.yticks(fontsize=10, color='black')
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.legend(loc="best")
        plt.tight_layout()

        # Save the graph to player_graphs directory
        graph_path = os.path.join(player_graphs_dir, f"{player}_trueskill_progression.png")
        plt.savefig(graph_path, dpi=150)
        plt.close()
        print(f"Saved TrueSkill graph for {player} at {graph_path}")

def main():
    process_races()

if __name__ == "__main__":
    main()
