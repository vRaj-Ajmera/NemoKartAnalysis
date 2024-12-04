# **NemoKartAnalysis**

View Project: https://vraj-ajmera.github.io/NemoKartAnalysis/

---

NemoKartAnalysis is a project designed to log and analyze races in the game "Nemokart."

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
│   ├── index.html                  # Home page
│   ├── player_stats.html           # Player stats page
│   ├── kart_stats.html             # Kart stats page
│   ├── post_analysis.json          # Shared data for rendering index.html
│   ├── elo_post_analysis.json      # Shared data for rendering player_stats.html
├── output/
│   ├── dummy_post_analysis.json    # For testing
│   ├── dummy_results.csv           # For testing
│   ├── post_analysis.json          # Main analysis output
│   ├── elo_post_analysis.json      # Elo analysis ouput
│   ├── results.csv                 # Main race results
│   ├── elo_tracker.csv             # Elo tracker race by race
│   ├── player_graphs/              # Player-rating graphs
├── src/
│   ├── gui_logger.py           # GUI for race logging
│   ├── gui_analyzer.py         # GUI for data analysis
│   ├── calculations/
│   │   ├── analysis.py             # Generates post_analysis.json
│   │   ├── elo_calculations.py     # ELO calculations
│   │   ├── kart_rankings.py        # Kart performance rankings
├── .gitignore                      # Git configuration
├── README.md                       # Project documentation

```

## **Run Instructions**
1. **gui_logger.py**: Run **gui_logger.py** and enter relevant information. In position enter 0 if the player did not race. Otherwise enter 1-8 which is their race position. Select a car if the player raced. Enter a race time (ex. 1:23.45) if the player raced. Results are logged to **results.csv**.
2. **analysis.py**: Run **analysis.py** to analyze results.csv data into **post_analysis.json**.
3. **elo_analysis.py**: Run **elo_analysis.py** to analyze results.csv data into **elo_tracker.csv**, **elo_post_analysis.json**, and generate player graphs.
4. Copy player graphs from output to docs->assets->player_graphs. Copy **post_analysis.json** and **elo_post_analysis.json** from output to docs.
