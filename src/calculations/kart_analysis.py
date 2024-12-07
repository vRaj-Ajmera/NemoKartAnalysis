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

def generate_kart_racetime_box_plots():
    """Generate box plots of kart race times for each map."""
    # Load necessary data
    results = load_csv(results_file)
    maps_data = load_csv(maps_file)
    karts_data = load_csv(karts_file)
    
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
            for i in range(3, len(race), 3):  # Iterate over Placement, Kart, Racetime columns
                kart_col = race.index[i + 1]  # Kart column
                time_col = race.index[i + 2]  # Racetime column
                
                kart_name = race[kart_col]
                racetime = race[time_col]

                # Skip if the player didn't race or if the kart isn't in the kart list
                if kart_name == "DNR" or racetime == "DNR" or kart_name not in karts_list:
                    continue

                try:
                    # Convert time string (e.g., "2:58.18") to seconds
                    time_parts = racetime.split(":")
                    kart_time_in_seconds = float(time_parts[0]) * 60 + float(time_parts[1])
                    kart_times[kart_name].append(kart_time_in_seconds)
                except Exception as e:
                    print(f"Error parsing time for kart {kart_name} in race: {race}")
                    continue

        # Prepare data for plotting
        plot_data = []
        kart_counts = {}  # To store race counts for each kart
        for kart, times in kart_times.items():
            kart_counts[kart] = len(times)
            for time in times:
                plot_data.append({"Kart": kart, "Race Time (s)": time})
        
        # If no data exists for this map, skip plotting
        if not plot_data:
            print(f"No data available for map: {map_name}, skipping plot.")
            continue
        
        # Convert plot data to DataFrame
        plot_df = pd.DataFrame(plot_data)

        # Compute median times for each kart and sort by median
        kart_order = (
            plot_df.groupby("Kart")["Race Time (s)"]
            .median()
            .sort_values()
            .index
            .map(lambda kart: f"{kart} ({kart_counts[kart]})")
            .tolist()
        )
        plot_df["Kart"] = plot_df["Kart"].map(lambda kart: f"{kart} ({kart_counts[kart]})")


        # Create a box plot with the sorted kart order
        plt.figure(figsize=(12, 8))
        sns.boxplot(
            data=plot_df, 
            x="Race Time (s)", 
            y="Kart", 
            orient="h", 
            order=kart_order
        )
        plt.title(f"Racetimes on {map_name}", fontsize=16)
        plt.xlabel("Race Time (seconds)", fontsize=14)
        plt.ylabel("Karts", fontsize=14)
        plt.grid(axis='x', linestyle='--', alpha=0.7)

        # Save the plot to the kart_graphs directory
        graph_path = os.path.join(kart_graphs_dir, f"{map_name}_kart_racetimes.png")
        plt.tight_layout()
        plt.savefig(graph_path, dpi=150)
        plt.close()
        print(f"Saved kart performance box plot for {map_name} at {graph_path}")

def generate_kart_placement_plots():
    """Generate box plots of kart placements for each map."""
    # Load necessary data
    results = load_csv(results_file)
    maps_data = load_csv(maps_file)
    karts_data = load_csv(karts_file)
    
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
        
        # Initialize a dictionary to hold kart placements
        kart_placements = {kart: [] for kart in karts_list}

        # Parse placements for each kart
        for _, race in map_results.iterrows():
            for i in range(3, len(race), 3):  # Iterate over Placement, Kart, Racetime columns
                kart_col = race.index[i + 1]  # Kart column
                placement_col = race.index[i]  # Placement column
                
                kart_name = race[kart_col]
                placement = race[placement_col]

                # Skip if the player didn't race or if the kart isn't in the kart list
                if kart_name == "DNR" or placement == "DNR" or kart_name not in karts_list:
                    continue

                try:
                    # Convert placement to integer and store it
                    kart_placements[kart_name].append(int(placement))
                except Exception as e:
                    print(f"Error parsing placement for kart {kart_name} in race: {race}")
                    continue

        # Prepare data for plotting
        plot_data = []
        kart_counts = {}  # To store race counts for each kart
        for kart, placements in kart_placements.items():
            kart_counts[kart] = len(placements)
            for placement in placements:
                plot_data.append({"Kart": kart, "Placement": placement})
        
        # If no data exists for this map, skip plotting
        if not plot_data:
            print(f"No placement data available for map: {map_name}, skipping plot.")
            continue
        
        # Convert plot data to DataFrame
        plot_df = pd.DataFrame(plot_data)

        # Compute median placements for each kart and sort by median
        kart_order = (
            plot_df.groupby("Kart")["Placement"]
            .median()
            .sort_values()
            .index
            .map(lambda kart: f"{kart} ({kart_counts[kart]})")
            .tolist()
        )
        plot_df["Kart"] = plot_df["Kart"].map(lambda kart: f"{kart} ({kart_counts[kart]})")

        # Create a box plot with the sorted kart order
        plt.figure(figsize=(12, 8))
        sns.violinplot(
            data=plot_df, 
            x="Placement", 
            y="Kart", 
            orient="h", 
            order=kart_order,
            inner=None
        )
        plt.title(f"Placements on {map_name}", fontsize=16)
        plt.xlabel("Placement (1 = Best, 8 = Worst)", fontsize=14)
        plt.ylabel("Karts", fontsize=14)
        plt.grid(axis='x', linestyle='--', alpha=0.7)

        # Save the plot to the kart_graphs directory
        graph_path = os.path.join(kart_graphs_dir, f"{map_name}_kart_placements.png")
        plt.tight_layout()
        plt.savefig(graph_path, dpi=150)
        plt.close()
        print(f"Saved kart placement box plot for {map_name} at {graph_path}")

def main():
    generate_kart_racetime_box_plots()
    generate_kart_placement_plots()

if __name__ == "__main__":
    main()
