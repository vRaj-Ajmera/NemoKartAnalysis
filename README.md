# **NemoKartAnalysis**

NemoKartAnalysis is a project designed to log and analyze races in the game "Nemokart." It consists of two main tools:
1. **Race Logger**: A GUI-based tool to log race data, including player placements and kart selections.
2. **Race Analyzer**: A GUI-based tool to analyze logged data, showing player stats, daily race insights, and performance trends.

---

## **File Structure**

```plaintext
NemoKartAnalysis/
├── data/
│   ├── karts.csv         # List of kart names
│   ├── maps.csv          # List of map names
├── output/
│   └── results.csv       # Logged race data
├── src/
│   ├── gui_logger.py     # GUI for logging races
│   ├── gui_analyzer.py   # GUI for analyzing races
├── .gitignore            # Git ignore file
├── README.md             # Project documentation
```

## **Run Instructions**
1. **gui_logger.py**: Run **gui_logger.py** and enter relevant information. In position enter 0 if the player did not race. Otherwise enter 1-8 which is their race position. Select a car if the player raced. Enter a race time (ex. 1:23.45) if the player raced. Results are logged to **results.csv** and **maps_best_times.csv**.
2. **gui_analyzer.py**: Run **gui_analyzer.py** to analyze data for specific days or view overall stats. PPR is points per race, calculated using the F1 scoring system.