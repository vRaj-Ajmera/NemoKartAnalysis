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
    ],
    "race4.png": [
        {'placement': 1, 'player_name': 'Azhan', 'race_time': '1:54.38'},
        {'placement': 3, 'player_name': 'Sameer', 'race_time': '1:56.94'}
    ],
    "race5.png": [
        {'placement': 2, 'player_name': 'Azhan', 'race_time': '2:43.20'},
        {'placement': 3, 'player_name': 'Sameer', 'race_time': '2:44.08'},
        {'placement': 5, 'player_name': 'Zetaa', 'race_time': '2:53.48'}
    ],
    "race6.png": [
        {'placement': 2, 'player_name': 'Azhan', 'race_time': '2:03.26'},
        {'placement': 4, 'player_name': 'Sameer', 'race_time': '2:06.20'},
        {'placement': 5, 'player_name': 'Zetaa', 'race_time': '2:06.68'}
    ],
    "race7.png": [
        {'placement': 1, 'player_name': 'Sameer', 'race_time': '1:56.20'},
        {'placement': 2, 'player_name': 'Zetaa', 'race_time': '1:56.36'},
        {'placement': 3, 'player_name': 'Azhan', 'race_time': '1:56.58'}
    ],
    "race8.png": [
        {'placement': 1, 'player_name': 'Azhan', 'race_time': '2:46.24'},
        {'placement': 2, 'player_name': 'Sameer', 'race_time': '2:48.60'},
        {'placement': 3, 'player_name': 'Zetaa', 'race_time': '2:48.70'}
    ],
    "race9.png": [
        {'placement': 1, 'player_name': 'Azhan', 'race_time': '2:37.16'},
        {'placement': 2, 'player_name': 'Sameer', 'race_time': '2:37.64'},
        {'placement': 3, 'player_name': 'Zetaa', 'race_time': '2:38.98'}
    ],
    "race10.png": [
        {'placement': 2, 'player_name': 'Azhan', 'race_time': '2:41.62'},
        {'placement': 3, 'player_name': 'Sameer', 'race_time': '2:42.24'},
        {'placement': 4, 'player_name': 'Raj', 'race_time': '2:43.20'}
    ],
    "race11.png": [
        {'placement': 1, 'player_name': 'Azhan', 'race_time': '1:46.34'},
        {'placement': 3, 'player_name': 'Sameer', 'race_time': '1:47.50'},
        {'placement': 5, 'player_name': 'Raj', 'race_time': '1:50.24'}
    ],
    "race12.png": [
        {'placement': 2, 'player_name': 'Azhan', 'race_time': '2:48.60'},
        {'placement': 4, 'player_name': 'Sameer', 'race_time': '2:50.16'}
    ]
    # Add more test cases as needed
}
