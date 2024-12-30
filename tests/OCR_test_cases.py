# tests/OCR_test_cases.py

# A dictionary of expected OCR outputs for given image filenames
test_cases = {
    "race1.png": [
        {'placement': 1, 'player_name': 'Azhan', 'race_time': '2:35.04'},
        {'placement': 3, 'player_name': 'Raj', 'race_time': '2:35.70'},
        {'placement': 4, 'player_name': 'Sameer', 'race_time': '2:35.90'}
    ],
    "race2.png": [
        {'placement': 1, 'player_name': 'Raj', 'race_time': '1:57.66'},
        {'placement': 3, 'player_name': 'Sameer', 'race_time': '2:00.50'},
        {'placement': 4, 'player_name': 'Azhan', 'race_time': '2:00.52'}
    ],
    "race3.png": [
        {'placement': 1, 'player_name': 'Raj', 'race_time': '2:28.02'},
        {'placement': 6, 'player_name': 'Viraj', 'race_time': '2:38.36'}
    ]
    # Add more test cases as needed
}
