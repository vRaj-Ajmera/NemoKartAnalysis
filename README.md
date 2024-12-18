# **NemoKartAnalysis**

NemoKartAnalysis is a project designed to log and analyze races in the game "Nemokart."

View Project Site: https://vraj-ajmera.github.io/NemoKartAnalysis/ 

## **Run Instructions**
1. **gui_logger.py**: Run **gui_logger.py** and enter relevant information. Select a car if the player raced. Enter a race time (ex. 1:23.45) if the player raced. Results are logged to **results.csv**.
2. **analyze_all.py**: Run **analyze_all.py** to analyze results.csv data into all the relevant files.
3. Get the live server extension and right click index.html and select "Open With Live Server".

## **File Structure**

```plaintext
NemoKartAnalysis/
├── data/
│   ├── karts.csv                   # Kart details
│   ├── maps.csv                    # Map details
│   ├── players.csv                 # Player details
│   ├── powerups.csv                # Power-ups (optional)
├── docs/                           # Public GitHub Pages
│   ├── assets/
│   │   ├── css/
│   │   │   ├── style.css           # Main styling
│   │   ├── js/
│   │   │   ├── main.js             # JS for index.html
│   │   │   ├── player_stats.js     # JS for player_stats.html
│   │   │   ├── kart_stats.js       # JS for kart_stats.html
│   │   ├── player_graphs/          # Player-rating graphs, rendered in player_stats.html
│   │   ├── kart_graphs/            # Kart stats graphs, rendered in kart_stats.html
│   │   ├── videos/                 # Videos for website background, rendered in index.html
│   ├── index.html                  # Home page
│   ├── player_stats.html           # Player stats page
│   ├── kart_stats.html             # Kart stats page
│   ├── post_analysis.json          # Shared data for rendering index.html
│   ├── elo_post_analysis.json      # Shared data for rendering player_stats.html
├── output/
│   ├── results.csv                 # Race results from gui_logger.py here
│   ├── post_analysis.json          # Main analysis output
│   ├── elo_post_analysis.json      # Elo analysis ouput
│   ├── elo_tracker.csv             # Elo tracker race by race
│   ├── player_graphs/              # Player-rating graphs
│   ├── kart_graphs/                # Kart-statistics graphs
│   ├── dummy_results.csv           # For testing
├── src/
│   ├── gui_logger.py               # RUN THIS FIRST. GUI for race logging
│   ├── analyze_all.py              # RUN THIS SECOND. Runs all calculations and updates json/graphs for website.
│   ├── calculations/
│   │   ├── analysis.py             # Generates post_analysis.json
│   │   ├── elo_calculations.py     # ELO and player-by-player calculations, writes elo_post_analysis.json and elo_tracker.csv and generates player_graphs
│   │   ├── kart_rankings.py        # Kart performance rankings generates graphs to kart_graphs
├── .gitignore                      # Git configuration
├── README.md                       # Project documentation
