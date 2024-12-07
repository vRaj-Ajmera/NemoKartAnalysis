import os
import shutil
import subprocess

# Base directory
base_dir = os.path.dirname(os.path.dirname(__file__))

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

def main():
    # 1. Run src/calculations/analysis.py
    analysis_script = os.path.join(base_dir, "src", "calculations", "analysis.py")
    run_script(analysis_script)

    # 2. Copy output/post_analysis.json to docs/post_analysis.json
    post_analysis_src = os.path.join(base_dir, "output", "post_analysis.json")
    post_analysis_dest = os.path.join(base_dir, "docs", "post_analysis.json")
    copy_file(post_analysis_src, post_analysis_dest)

    # 3. Run src/calculations/elo_analysis.py
    elo_analysis_script = os.path.join(base_dir, "src", "calculations", "elo_analysis.py")
    run_script(elo_analysis_script)

    # 4. Copy output/elo_post_analysis.json to docs/elo_post_analysis.json
    elo_post_analysis_src = os.path.join(base_dir, "output", "elo_post_analysis.json")
    elo_post_analysis_dest = os.path.join(base_dir, "docs", "elo_post_analysis.json")
    copy_file(elo_post_analysis_src, elo_post_analysis_dest)

    # 5. Copy all graphs from output/player_graphs/ to docs/assets/player_graphs/
    player_graphs_src = os.path.join(base_dir, "output", "player_graphs")
    player_graphs_dest = os.path.join(base_dir, "docs", "assets", "player_graphs")
    copy_directory(player_graphs_src, player_graphs_dest)

    # 6. Run src/calculations/kart_analysis.py
    kart_analysis_script = os.path.join(base_dir, "src", "calculations", "kart_analysis.py")
    run_script(kart_analysis_script)

    # 7. Copy all graphs from output/kart_graphs/ to docs/assets/kart_graphs/
    kart_graphs_src = os.path.join(base_dir, "output", "kart_graphs")
    kart_graphs_dest = os.path.join(base_dir, "docs", "assets", "kart_graphs")
    copy_directory(kart_graphs_src, kart_graphs_dest)

    print("All analysis tasks completed successfully.")

if __name__ == "__main__":
    main()
