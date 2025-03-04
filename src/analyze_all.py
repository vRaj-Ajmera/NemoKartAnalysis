import os
import shutil
import subprocess
import csv
import json
import re

# Base directory
base_dir = os.path.dirname(os.path.dirname(__file__))

# Define file paths
players_csv_path = os.path.join(base_dir, "data", "players.csv")
main_js_path = os.path.join(base_dir, "docs", "assets", "js", "main.js")
player_stats_js_path = os.path.join(base_dir, "docs", "assets", "js", "player_stats.js")

def run_script(script_path):
    """Run a Python script."""
    subprocess.run(["python", script_path], check=True)

def copy_file(src, dest):
    """Copy a file from src to dest."""
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy(src, dest)

def copy_directory(src, dest):
    """Copy all files from src directory to dest directory."""
    if os.path.exists(src):
        os.makedirs(dest, exist_ok=True)
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dest, item)
            if os.path.isfile(s):
                shutil.copy(s, d)

def update_js_with_players(js_path, players):
    """Update the players array in the specified JS file."""
    try:
        with open(js_path, "r") as file:
            content = file.read()

        # Replace the players array
        new_players_array = f"const players = {players};"
        updated_content = re.sub(r"const players = \[.*?\];", new_players_array, content, flags=re.DOTALL)

        with open(js_path, "w") as file:
            file.write(updated_content)
        print(f"Updated players in {js_path}")
    except Exception as e:
        print(f"Error updating {js_path}: {e}")

def main():
    # Load players from CSV
    if not os.path.exists(players_csv_path):
        print(f"Players CSV file not found at {players_csv_path}")
        return

    try:
        with open(players_csv_path, "r") as file:
            reader = csv.reader(file)
            players = [row[0] for row in reader if row]  # Extract player names, ignoring empty rows
            players.pop(0)  # Remove the header
    except Exception as e:
        print(f"Error reading players CSV: {e}")
        return
 
    # Update JS files
    players_js_array = json.dumps(players, indent=4)
    update_js_with_players(main_js_path, players_js_array)
    update_js_with_players(player_stats_js_path, players_js_array)

    # 1. Run src/calculations/analysis.py
    analysis_script = os.path.join(base_dir, "src", "calculations", "analysis.py")
    run_script(analysis_script)

    # 2. Copy output/post_analysis.json to docs/post_analysis.json
    post_analysis_src = os.path.join(base_dir, "output", "post_analysis.json")
    post_analysis_dest = os.path.join(base_dir, "docs", "post_analysis.json")
    copy_file(post_analysis_src, post_analysis_dest)

    # 3. Copy output/results.json to docs/results.json
    results_src = os.path.join(base_dir, "output", "results.json")
    results_dest = os.path.join(base_dir, "docs", "results.json")
    copy_file(results_src, results_dest)

    # 4. Run src/calculations/elo_analysis.py
    elo_analysis_script = os.path.join(base_dir, "src", "calculations", "elo_analysis.py")
    run_script(elo_analysis_script)

    # 5. Copy output/elo_post_analysis.json to docs/elo_post_analysis.json
    elo_post_analysis_src = os.path.join(base_dir, "output", "elo_post_analysis.json")
    elo_post_analysis_dest = os.path.join(base_dir, "docs", "elo_post_analysis.json")
    copy_file(elo_post_analysis_src, elo_post_analysis_dest)

    # 6. Copy all graphs from output/player_graphs/ to docs/assets/player_graphs/
    player_graphs_src = os.path.join(base_dir, "output", "player_graphs")
    player_graphs_dest = os.path.join(base_dir, "docs", "assets", "player_graphs")
    copy_directory(player_graphs_src, player_graphs_dest)

    # 7. Run src/calculations/kart_analysis.py
    kart_analysis_script = os.path.join(base_dir, "src", "calculations", "kart_analysis.py")
    run_script(kart_analysis_script)

    # 8. Copy all graphs from output/kart_graphs/ to docs/assets/kart_graphs/
    kart_graphs_src = os.path.join(base_dir, "output", "kart_graphs")
    kart_graphs_dest = os.path.join(base_dir, "docs", "assets", "kart_graphs")
    copy_directory(kart_graphs_src, kart_graphs_dest)

    print("All analysis tasks completed successfully.")

if __name__ == "__main__":
    main()
