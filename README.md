# **NemoKartAnalysis**

NemoKartAnalysis is a project designed to log and analyze races in the game "Nemokart."

View Project Site: https://vraj-ajmera.github.io/NemoKartAnalysis/ 

## **Setup Instructions**

### **Step 1: Install Required Libraries**

Before running the project, ensure the following libraries are installed. Use `pip` to install them:

```bash
pip install pandas numpy easyocr opencv-python rapidfuzz seaborn matplotlib tkinterdnd2
```

- **EasyOCR** requires PyTorch. Install PyTorch according to your system and Python version by visiting [PyTorch's installation page](https://pytorch.org/get-started/locally/).

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
- Maps aliases (nicknames) to players for OCR matching.
- Example:
  ```json
  {
    "Raj": ["DaTrixta"],
    "Azhan": ["highzahawk"],
    "Sameer": ["sourpanda"]
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
  Bat Kart
  Dino Kart
  Grey Blocks
  ```

### **Step 3: Running the Logger**
- Run **gui_logger.py** for manual logging.
- Run **gui_OCR_logger.py** for OCR-based logging. Drag and drop race result screenshots or paste them from the clipboard. Ensure relevant players, maps, and karts are pre-populated in the input files.

### **Step 4: Analyze the Results**
- After logging, run **analyze_all.py** to process the logged race results into structured analysis outputs.

### **Step 5: View Analysis**
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
├── output/
│   ├── img_processing/             # OCR inputs go here
│   ├── results.csv                 # Race results from gui_logger.py here
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
│   │   ├── analysis.py             # Generates post_analysis.json
│   │   ├── elo_analysis.py         # ELO and player-by-player calculations, writes elo_post_analysis.json and elo_tracker.csv and generates player_graphs
│   │   ├── kart_analysis.py        # Kart performance rankings generates graphs to kart_graphs
├── .gitignore                      # Git configuration
├── README.md                       # Project documentation
