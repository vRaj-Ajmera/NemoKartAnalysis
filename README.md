# **NemoKartAnalysis**

View Project: https://vraj-ajmera.github.io/NemoKartAnalysis/
\\NemoKartAnalysis is a project designed to log and analyze races in the game "Nemokart."

---

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
│   ├── index.html                  # Home page
│   ├── player_stats.html           # Player stats page
│   ├── kart_stats.html             # Kart stats page
│   ├── post_analysis.json          # Shared data for rendering pages
├── output/
│   ├── dummy_post_analysis.json    # For testing
│   ├── dummy_results.csv           # For testing
│   ├── post_analysis.json          # Main analysis output
│   ├── results.csv                 # Main race results
│   ├── player_graphs/              # Player-specific graphs
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
1. **gui_logger.py**: Run **gui_logger.py** and enter relevant information. In position enter 0 if the player did not race. Otherwise enter 1-8 which is their race position. Select a car if the player raced. Enter a race time (ex. 1:23.45) if the player raced. Results are logged to **results.csv** and **maps_best_times.csv**.
2. **gui_analyzer.py**: Run **gui_analyzer.py** to analyze data for specific days or view overall stats. PPR is points per race, calculated using the F1 scoring system.