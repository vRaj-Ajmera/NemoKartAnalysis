import pandas as pd
import os
import json
import matplotlib.pyplot as plt
import seaborn as sns

# Base directory and file paths
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
results_file = os.path.join(base_dir, "output/results.csv")
maps_file = os.path.join(base_dir, "data/maps.csv")
karts_file = os.path.join(base_dir, "data/karts.csv")

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

def generate_kart_box_plots():
    """Generate box plots of kart race times for each map."""
    # Load necessary data
    results = load_csv(results_file)
    maps_data = load_csv(os.path.join(base_dir, "data/maps.csv"))
    karts_data = load_csv(os.path.join(base_dir, "data/karts.csv"))
    
    # Extract kart and map information
    karts_list = karts_data["Kart Name"].tolist()
    maps_list = maps_data["Map Name"].tolist()
    
    # Directory for saving graphs
    kart_graphs_dir = os.path.join(base_dir, "output/kart_graphs")
    os.makedirs(kart_graphs_dir, exist_ok=True)

    # Iterate through each map
    for map_name in maps_list:
        # Filter results for the current map
        map_results = results[results["Map Name"] == map_name]
        
        # Initialize a dictionary to hold kart race times
        kart_times = {kart: [] for kart in karts_list}

        # Parse race times for each kart
        for _, race in map_results.iterrows():
            for kart in karts_list:
                # Find race time column for the kart
                kart_time_col = f"{kart} Racetime"
                if kart_time_col in race and race[kart_time_col] != "DNR" and isinstance(race[kart_time_col], str):
                    # Convert time string (e.g., "2:58.18") to seconds
                    time_parts = race[kart_time_col].split(":")
                    kart_time_in_seconds = float(time_parts[0]) * 60 + float(time_parts[1])
                    kart_times[kart].append(kart_time_in_seconds)

        # Prepare data for plotting
        plot_data = []
        for kart, times in kart_times.items():
            for time in times:
                plot_data.append({"Kart": kart, "Race Time (s)": time})
        
        # If no data exists for this map, skip plotting
        if not plot_data:
            continue
        
        # Convert plot data to DataFrame
        plot_df = pd.DataFrame(plot_data)

        # Create a box plot
        plt.figure(figsize=(12, 8))
        sns.boxplot(data=plot_df, x="Race Time (s)", y="Kart", orient="h")
        plt.title(f"Kart Performance on {map_name}", fontsize=16)
        plt.xlabel("Race Time (seconds)", fontsize=14)
        plt.ylabel("Karts", fontsize=14)
        plt.grid(axis='x', linestyle='--', alpha=0.7)

        # Save the plot to the kart_graphs directory
        graph_path = os.path.join(kart_graphs_dir, f"{map_name}_kart_performance.png")
        plt.tight_layout()
        plt.savefig(graph_path, dpi=150)
        plt.close()
        print(f"Saved kart performance box plot for {map_name} at {graph_path}")
