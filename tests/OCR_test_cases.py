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
    ],
    "race13.png": [
        {'placement': 3, 'player_name': 'Azhan', 'race_time': '2:40.26'},
        {'placement': 4, 'player_name': 'Sameer', 'race_time': '2:41.70'}
    ],
    "race14.png": [
        {'placement': 1, 'player_name': 'Sameer', 'race_time': '2:02.78'}
    ],
    "race15.png": [
        {'placement': 1, 'player_name': 'Raj', 'race_time': '1:51.84'},
        {'placement': 2, 'player_name': 'Sameer', 'race_time': '1:52.72'},
        {'placement': 3, 'player_name': 'Azhan', 'race_time': '1:53.94'}
    ],
    "race16.png": [
        {'placement': 2, 'player_name': 'Sameer', 'race_time': '2:49.56'}
    ],
    "race17.png": [
        {'placement': 1, 'player_name': 'Sameer', 'race_time': '1:52.20'}
    ],
    "race18.png": [
        {'placement': 3, 'player_name': 'Sameer', 'race_time': '1:52.02'},
        {'placement': 4, 'player_name': 'Raj', 'race_time': '1:52.38'},
        {'placement': 5, 'player_name': 'Azhan', 'race_time': '1:55.16'}
    ],
    "race19.png": [
        {'placement': 1, 'player_name': 'Sameer', 'race_time': '2:36.74'},
        {'placement': 3, 'player_name': 'Azhan', 'race_time': '2:39.20'}
    ],
    "race20.png": [
        {'placement': 2, 'player_name': 'Azhan', 'race_time': '2:50.76'},
        {'placement': 3, 'player_name': 'Sameer', 'race_time': '2:53.56'}
    ],
    "race21.png": [
        {'placement': 1, 'player_name': 'Sameer', 'race_time': '2:43.24'},
        {'placement': 2, 'player_name': 'Raj', 'race_time': '2:46.12'}
    ],
    "race22.png": [
        {'placement': 1, 'player_name': 'Azhan', 'race_time': '2:42.66'},
        {'placement': 2, 'player_name': 'Adi', 'race_time': '2:44.16'},
        {'placement': 3, 'player_name': 'Dylan', 'race_time': '2:45.22'},
        {'placement': 4, 'player_name': 'EnderRobot', 'race_time': '2:46.10'}
    ],
    "race23.png": [
        {'placement': 1, 'player_name': 'Adi', 'race_time': '2:14.24'},
        {'placement': 2, 'player_name': 'Dylan', 'race_time': '2:14.84'},
        {'placement': 3, 'player_name': 'Azhan', 'race_time': '2:15.66'},
        {'placement': 5, 'player_name': 'Lynden', 'race_time': '2:17.16'},
        {'placement': 6, 'player_name': 'EnderRobot', 'race_time': '2:19.08'}
    ],
    "race24.png": [
        {'placement': 1, 'player_name': 'Azhan', 'race_time': '2:43.62'},
        {'placement': 4, 'player_name': 'Adi', 'race_time': '2:45.76'},
        {'placement': 5, 'player_name': 'EnderRobot', 'race_time': '2:52.02'}
    ],
    "race25.png": [
        {'placement': 1, 'player_name': 'Azhan', 'race_time': '2:40.16'},
        {'placement': 2, 'player_name': 'Raj', 'race_time': '2:40.44'},
        {'placement': 3, 'player_name': 'Sameer', 'race_time': '2:44.04'},
        {'placement': 4, 'player_name': 'Adi', 'race_time': '2:45.62'},
        {'placement': 6, 'player_name': 'Dylan', 'race_time': '2:47.68'},
        {'placement': 7, 'player_name': 'Parum', 'race_time': '2:50.30'}
    ]
    # Add more test cases as needed
}
