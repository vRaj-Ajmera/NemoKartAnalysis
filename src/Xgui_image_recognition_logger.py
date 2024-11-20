import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image
import pytesseract
import pandas as pd
import os
import re
from pathlib import Path

# Get the directory of the current script
script_dir = os.path.dirname(__file__)

# Relative file paths
kart_images = os.path.join(script_dir, "../data/Kart Images/")  # Kart images directory
kart_file = os.path.join(script_dir, "../data/karts.csv")
map_file = os.path.join(script_dir, "../data/maps.csv")
output_file = os.path.join(script_dir, "../output/image_rec_output.csv")
race_screenshots_file = os.path.join(script_dir, "../data/Race_Screenshots/")  # Race screenshots directory

# Kart database mapping (kart image filenames to kart names)
kart_database = {
    "Puppy_kart.png": "Puppy",
    "TheKart_kart.png": "The Kart"
}

# Initialize CSV if it doesn't exist
if not os.path.exists(output_file):
    pd.DataFrame(columns=["Map Name", "Player", "Placement", "Kart", "Race Time"]).to_csv(output_file, index=False)

# Function to recognize kart from stored database
def recognize_kart(image_path):
    # Match filename to kart name
    kart_name = kart_database.get(Path(image_path).name, "Unknown Kart")
    return kart_name

# Function to extract race data from an image
def extract_race_data(image_path, map_name):
    image = Image.open(image_path).convert("L")  # Convert to grayscale
    raw_text = pytesseract.image_to_string(image)

    # Regex to extract placement, player, and time
    race_data = []
    lines = raw_text.split("\n")
    for line in lines:
        match = re.match(r"(\d+)\s+([\w\s]+)\s+(\d+:\d{2}\.\d{2})", line)
        if match:
            placement = int(match.group(1))
            player = match.group(2).strip()
            race_time = match.group(3).strip()

            # Recognize kart (currently set to "Unknown Kart")
            kart = "Unknown Kart"
            race_data.append({
                "Map Name": map_name,
                "Player": player,
                "Placement": placement,
                "Kart": kart,
                "Race Time": race_time
            })

    return race_data

# Function to log data to CSV
def log_data_to_csv(data):
    df = pd.DataFrame(data)
    df.to_csv(output_file, mode="a", header=False, index=False)

# Function to process and log images
def process_and_log_images(map_name, images):
    if not map_name or map_name == "-- Select --":
        status_label.config(text="Error: Select a map first!", fg="red")
        return

    all_race_data = []
    for image_path in images:
        race_data = extract_race_data(image_path, map_name)
        all_race_data.extend(race_data)

    if all_race_data:
        log_data_to_csv(all_race_data)
        status_label.config(text=f"Logged {len(all_race_data)} entries from {len(images)} images.", fg="green")
    else:
        status_label.config(text="No valid data found in images.", fg="red")

# Function to handle drag-and-drop images
def add_images():
    file_paths = filedialog.askopenfilenames(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    for file_path in file_paths:
        image_listbox.insert(tk.END, file_path)

# Function to clear selected images
def clear_images():
    image_listbox.delete(0, tk.END)

# GUI Setup
root = tk.Tk()
root.title("Image Recognition Logger")

# Map Selection
tk.Label(root, text="Select Map:").grid(row=0, column=0, padx=10, pady=5)
map_combobox = ttk.Combobox(root, values=["-- Select --", "Shanghai", "Snowville", "Shanghai by Night"], state="readonly")
map_combobox.grid(row=0, column=1, padx=10, pady=5)
map_combobox.set("-- Select --")  # Default value

# Image Listbox
tk.Label(root, text="Images to Process:").grid(row=1, column=0, padx=10, pady=5, sticky="nw")
image_listbox = tk.Listbox(root, width=50, height=10)
image_listbox.grid(row=1, column=1, padx=10, pady=5)

# Add/Remove Buttons
button_frame = tk.Frame(root)
button_frame.grid(row=1, column=2, padx=10, pady=5, sticky="n")

add_button = tk.Button(button_frame, text="Add Images", command=add_images)
add_button.pack(fill="x", pady=2)
clear_button = tk.Button(button_frame, text="Clear Images", command=clear_images)
clear_button.pack(fill="x", pady=2)

# Log Button
log_button = tk.Button(root, text="Log Data", command=lambda: process_and_log_images(map_combobox.get(), image_listbox.get(0, tk.END)))
log_button.grid(row=2, column=1, pady=10)

# Status Label
status_label = tk.Label(root, text="", fg="green")
status_label.grid(row=3, column=0, columnspan=3, pady=5)

root.mainloop()
