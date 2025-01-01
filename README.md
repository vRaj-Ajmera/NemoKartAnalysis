# **NemoKartAnalysis**

NemoKartAnalysis is a project designed to log and analyze races in the game "Nemokart."

View Project Site: https://vraj-ajmera.github.io/NemoKartAnalysis/ 

## **Setup Instructions**

### **Step 1: Install Required Libraries**

**EasyOCR** requires PyTorch. Install PyTorch according to your system and Python version by visiting [PyTorch's installation page](https://pytorch.org/get-started/locally/).

Before running the project, ensure the following libraries are installed. The following instructions are for **Windows**. For other platforms, additional setup may be required (see below):

#### **Windows**
Use `pip` to install the required libraries:

```bash
pip install pandas numpy easyocr opencv-python rapidfuzz seaborn matplotlib tkinterdnd2
```

#### **Linux**
For Linux, ensure your system has the following prerequisites before running the `pip` command:

1. Install `tkinter` if it's not already installed (it may not be included by default):
   ```bash
   sudo apt-get install python3-tk
   ```

2. Install `cv2` dependencies (required for OpenCV):
   ```bash
   sudo apt-get install libopencv-dev python3-opencv
   ```

3. Then install the Python libraries:
   ```bash
   pip install pandas numpy easyocr opencv-python rapidfuzz seaborn matplotlib tkinterdnd2
   ```

#### **MacOS**
For macOS, you may need to install `tkinter` using `brew` if it's not pre-installed:

1. Install `tkinter`:
   ```bash
   brew install python-tk
   ```

2. Then install the Python libraries:
   ```bash
   pip install pandas numpy easyocr opencv-python rapidfuzz seaborn matplotlib tkinterdnd2
   ```


#### Explanation of the Libraries

- **`pandas`**: For data manipulation and handling CSV files.
- **`numpy`**: For numerical operations and array manipulations.
- **`easyocr`**: For Optical Character Recognition (OCR) of race screenshots.
- **`opencv-python`**: For image preprocessing.
- **`rapidfuzz`**: For fuzzy string matching to match player aliases.
- **`seaborn`**: For data visualization (used in graph generation).
- **`matplotlib`**: For creating graphs and visualizations.
- **`tkinterdnd2`**: For drag-and-drop support in the Tkinter GUI.
- **`Pillow (PIL)`**: For working with images and clipboard pasting functionality.
- **`shutil` and `subprocess`**: For handling file and directory operations and executing system commands.

These libraries will ensure your project has all the required capabilities for both GUI logging and image-based OCR race data extraction.

### **Step 2: Populate Input Files**

#### **players.csv**
- Contains the names of all players to be logged.
- Format:
  ```csv
  Player Name
  Raj
  Azhan
  Sameer
  ```

#### **player_aliases.json**
- Maps aliases (nicknames/gamertags) to players for OCR matching.
- Example:
  ```json
  {
    "Raj": ["DaTrixta", "Trickster"],
    "Azhan": ["highzahawk", "Hawk"],
    "Sameer": ["sourpanda", "PandaEater55"]
  }
  ```

#### **maps.csv**
- Contains the names of all race maps.
- Format:
  ```csv
  Map Name
  Shanghai
  Snowville
  Formula Wild
  ```

#### **karts.csv**
- Contains the names of all karts and their details.
- Format:
  ```csv
  Kart Name,CC
  Bat Kart,118
  Dino Kart,118
  Grey Blocks,141
  ```

### **Step 3: Clear Output Files**

Delete any existing data **ONLY if you are setting up your own race tracker with new players**. Verify results.csv is empty. Verify player_graphs folder is empty.

  ```
  output/results.csv
  output/player_graphs/
  ```

## Run Instructions

### **Step 1: Running the Logger**
- Run **gui_logger.py** for manual logging.
- Run **gui_OCR_logger.py** for OCR-based logging. Drag and drop race result screenshots or paste them from the clipboard. Ensure relevant players, maps, and karts are pre-populated in the input files.

### **Step 2: Analyze the Results**
- After logging, run **analyze_all.py** to process the logged race results into structured analysis outputs.

### **Step 3: View Analysis**
- Open **index.html** with a live server to view the analysis. Install a live server extension and right-click **index.html** to open it with the live server.

## **File Structure**

```plaintext
NemoKartAnalysis/
├── data/
│   ├── karts.csv                   # Kart names/CC
│   ├── maps.csv                    # Map names
│   ├── players.csv                 # Player names
│   ├── powerups.csv                # Power-ups (unused in analysis)
│   ├── player_aliases.json         # Player Aliases
├── docs/                           # Public GitHub Pages
│   ├── assets/
│   │   ├── css/
│   │   │   ├── style.css           # Main styling
│   │   ├── icons/                  # Player pfps stored here
│   │   ├── js/
│   │   │   ├── main.js             # JS for index.html
│   │   │   ├── player_stats.js     # JS for player_stats.html
│   │   │   ├── kart_stats.js       # JS for kart_stats.html
│   │   ├── player_graphs/          # Player-rating graphs, rendered in player_stats
│   │   ├── kart_graphs/            # Kart stats graphs, rendered in kart_stats
│   │   ├── videos/                 # Videos for background, rendered in index
│   ├── index.html                  # Home page
│   ├── player_stats.html           # Player stats page
│   ├── kart_stats.html             # Kart stats page
│   ├── post_analysis.json          # Shared data for rendering index.html
│   ├── elo_post_analysis.json      # Shared data for rendering player_stats.html
│   ├── results.json                # Used in rendering "Races Together" table
├── output/
│   ├── img_processing/             # OCR inputs go here
│   ├── results.csv                 # Race results from gui_logger.py here
│   ├── results.json                # Main analysis output, json version of results.csv with DNR columns filtered out
│   ├── post_analysis.json          # Main analysis output
│   ├── elo_post_analysis.json      # Elo analysis ouput
│   ├── elo_tracker.csv             # Elo tracker race by race
│   ├── player_graphs/              # Player-rating graphs
│   ├── kart_graphs/                # Kart-statistics graphs
│   ├── dummy_results.csv           # For testing
├── src/
│   ├── gui_logger.py               # GUI for race logging without OCR.
│   ├── gui_OCR_logger.py           # GUI for race logging with OCR.
│   ├── analyze_all.py              # Runs all calculations and updates json/graphs for website. RUN AFTER LOGGING.
│   ├── calculations/
│   │   ├── analysis.py             # Generates post_analysis.json and results.json
│   │   ├── elo_analysis.py         # ELO and player-by-player calculations, writes elo_post_analysis.json and elo_tracker.csv and generates player_graphs
│   │   ├── kart_analysis.py        # Kart performance rankings generates graphs to kart_graphs
├── .gitignore                      # Git configuration
├── README.md                       # Project documentation
