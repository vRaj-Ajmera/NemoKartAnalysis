const players = [
    "Raj",
    "Azhan",
    "Sameer",
    "Zetaa",
    "Adi",
    "Dylan",
    "Parum",
    "EnderRobot",
    "Lynden",
    "Rusheel",
    "SultanSpeppy",
    "Viraj",
    "Tejas"
];

function addProfilePictures() {
    const defaultImagePath = "assets/icons/default.png";

    // Loop through all <td> elements in the document
    document.querySelectorAll("td").forEach(td => {
        const playerName = td.textContent.trim();

        if (players.includes(playerName)) {
            const imagePath = `assets/icons/${playerName}.png`;

            // Create image element
            const img = document.createElement("img");
            img.src = imagePath;
            img.alt = playerName;
            img.className = "profile-pic";
            img.onerror = () => (img.src = defaultImagePath); // Fallback to default image

            // Clear existing text and re-add image + name
            td.innerHTML = ""; // Clear text content
            td.appendChild(img);
            td.appendChild(document.createTextNode(` ${playerName}`)); // Add name after the image
        }
    });
}

function createAndRenderTableFromStats(containerName, columnNamesAndInfos, stats, columnValues, columnSort, defaultSort = 0, useProfilePictures = true) {
    let sortedStats = stats;
    let columnNames = Object.entries(columnNamesAndInfos).map(([cName,]) => cName);

    let recentlySortedColumn = defaultSort;
    let recentlySortedDefault = true;

    function sortTable(columnNo, useDefaultSort = false) {
        if (useDefaultSort) {
            recentlySortedDefault = true;
        } else {
            if (recentlySortedColumn === columnNo) {
                recentlySortedDefault = !recentlySortedDefault;
            } else {
                recentlySortedColumn = columnNo;
                recentlySortedDefault = true;
            }
        }
        sortedStats = columnSort[columnNo][recentlySortedDefault ? "default" : "reverse"](stats);
    }

    function createInnerHTML() {
        return `
            <thead>
                <tr> ${Object.entries(columnNamesAndInfos).map(([cName, info], index) => info === "" ? `<th id="${index}">${cName}</th>` : `<th id="${index}">${cName}<div class="info-icon" data-tooltip="${info}">i</div></th>`).join("")}
                </tr>
            </thead>
            <tbody>
            ${sortedStats.map((stat, ind) => `
                <tr>
                    ${columnNames.map((_, index) => `<td>${columnValues[index](stat, ind)}</td>`).join("")}
                `).join("")}
            </tbody>
        `;
    }

    function createAndRenderTable(innerHTML) {
        const table = document.createElement("table");
        table.innerHTML = innerHTML;
        table.querySelectorAll('th') // get all the table header elements
            .forEach((element) => { // add a click handler for each 
                element.addEventListener('click', event => {
                    sortTable(parseInt(element.id) ?? 0);
                    createAndRenderTable(createInnerHTML()); //call a function which sorts the table by a given column number
                })
            });

        const container = document.getElementById(containerName);
        container.innerHTML = ""; // Clear previous table
        container.appendChild(table);
        if (useProfilePictures) {
            addProfilePictures(); // Add profile pictures after table renders
        }
    }

    sortTable(defaultSort, true);
    createAndRenderTable(createInnerHTML());
}

function createAndRenderSummaryTable(containerName, stats) {
    createAndRenderTableFromStats(
        containerName,
        {
            "Player": "",
            "Races": "",
            "Points": "Points are awarded based on placement- 1st: 25, 2nd: 18, 3rd: 15, 4th: 12, 5th: 10, 6th: 8, 7th: 6, 8th:",
            "PPR": "PPR: Points per race, calculated as total points divided by the number of races.",
            "Avg Position": ""
        },

        stats,
        [
            ([a,]) => a,
            ([, b]) => b.Races,
            ([, b]) => b.Points,
            ([, b]) => b.PPR.toFixed(2),
            ([, b]) => b["Avg Race Position"]?.toFixed(2) ?? "N/A"
        ],
        [
            {
                "default": (stats,) => Object.entries(stats).sort(([a,], [b,]) => a.localeCompare(b)),
                "reverse": (stats,) => Object.entries(stats).sort(([b,], [a,]) => a.localeCompare(b))
            }, // Player
            {
                "default": (stats,) => Object.entries(stats).sort(([, a], [, b]) => b.Races - a.Races),
                "reverse": (stats,) => Object.entries(stats).sort(([, b], [, a]) => b.Races - a.Races)
            }, // Races
            {
                "default": (stats,) => Object.entries(stats).sort(([, a], [, b]) => b.Points - a.Points),
                "reverse": (stats,) => Object.entries(stats).sort(([, b], [, a]) => b.Points - a.Points)
            }, // Points
            {
                "default": (stats,) => Object.entries(stats).sort(([, a], [, b]) => b.PPR - a.PPR),
                "reverse": (stats,) => Object.entries(stats).sort(([, b], [, a]) => b.PPR - a.PPR)
            }, // PPR
            {
                "default": (stats,) => Object.entries(stats).sort(([, a], [, b]) => (a["Avg Race Position"] - b["Avg Race Position"])),
                "reverse": (stats,) => Object.entries(stats).sort(([, b], [, a]) => (a["Avg Race Position"] - b["Avg Race Position"]))
            }, // Avg Position
        ],
        3,
        true
    );
}

document.addEventListener("DOMContentLoaded", () => {
    const postAnalysisUrl = "post_analysis.json";
    const eloAnalysisUrl = "elo_post_analysis.json"; // Add this line

    Promise.all([
        fetch(postAnalysisUrl).then((response) => response.json()),
        fetch(eloAnalysisUrl).then((response) => response.json()),
    ])
        .then(([postAnalysisData, eloAnalysisData]) => {
            renderSummaryTable(postAnalysisData["All Time Stats"], eloAnalysisData["Player Ratings"]);
            populateDailyStatsDropdown(postAnalysisData["Daily Stats"]);
            populateLeaderboardsDropdown(
                postAnalysisData["Best Race Times"],
                postAnalysisData["Individual Player Best Times"]
            );
        })
        .catch((err) => console.error("Error fetching data:", err));

    // Populate and handle Daily Stats Dropdown
    function populateDailyStatsDropdown(dailyStats) {
        const dropdown = document.getElementById("daily-stats-dropdown");

        // Sort dates in descending order
        const sortedDates = Object.keys(dailyStats).sort((a, b) => new Date(b) - new Date(a));

        // Populate the dropdown with sorted dates
        sortedDates.forEach(date => {
            const option = document.createElement("option");
            option.value = date;
            option.textContent = date;
            dropdown.appendChild(option);
        });

        dropdown.addEventListener("change", (e) => {
            if (e.target.value !== "-- Select --") {
                renderDailyStatsTable(dailyStats[e.target.value]);
                e.target.querySelector("option[value='-- Select --']").remove(); // Remove "-- Select --"
            }
        });
    }

    // Render Daily Stats Table
    function renderDailyStatsTable(stats) {
        createAndRenderSummaryTable("daily-stats-table", stats);
    }

    function populateLeaderboardsDropdown(leaderboards, individualBestTimes) {
        const dropdown = document.getElementById("map-dropdown");
        const playerTimesButton = document.getElementById("player-times-button");
        const recordedTimesButton = document.getElementById("recorded-times-button");

        let isIndividual = true; // Start with no rendering

        // Initially hide the buttons
        playerTimesButton.classList.add("hidden");
        recordedTimesButton.classList.add("hidden");

        // Add the default "-- Select --" option
        const defaultOption = document.createElement("option");
        defaultOption.value = "-- Select --";
        defaultOption.textContent = "-- Select --";
        defaultOption.disabled = true; // Keep it disabled
        defaultOption.selected = true; // Make it the default selected
        dropdown.appendChild(defaultOption);

        // Populate dropdown options
        Object.keys(leaderboards).forEach(map => {
            const option = document.createElement("option");
            option.value = map;
            option.textContent = map;
            dropdown.appendChild(option);
        });

        // Function to render the leaderboard based on the selected map and type
        function renderCurrentLeaderboard(selectedMap) {
            if (selectedMap && selectedMap !== "-- Select --") {
                const data = isIndividual
                    ? individualBestTimes[selectedMap].slice(0, 10) // Limit to 10
                    : leaderboards[selectedMap].slice(0, 10); // Limit to 10

                renderLeaderboardsTable(selectedMap, data, isIndividual);
            }
        }

        // Dropdown change event
        dropdown.addEventListener("change", () => {
            const selectedMap = dropdown.value;

            // Only render leaderboard if a valid map is selected
            if (selectedMap && selectedMap !== "-- Select --") {
                playerTimesButton.classList.remove("hidden");
                recordedTimesButton.classList.remove("hidden");
                renderCurrentLeaderboard(selectedMap);
            } else {
                playerTimesButton.classList.add("hidden");
                recordedTimesButton.classList.add("hidden");
                const container = document.getElementById("leaderboards-table");
                container.innerHTML = ""; // Clear the leaderboard table
            }
        });

        // Button to show "Best Player Times"
        playerTimesButton.addEventListener("click", () => {
            isIndividual = true;
            playerTimesButton.disabled = true; // Disable the button to avoid redundant clicks
            recordedTimesButton.disabled = false; // Enable the other button
            playerTimesButton.classList.add("selected");
            recordedTimesButton.classList.remove("selected");
            const selectedMap = dropdown.value;
            renderCurrentLeaderboard(selectedMap);
        });

        // Button to show "Best Recorded Times"
        recordedTimesButton.addEventListener("click", () => {
            isIndividual = false;
            recordedTimesButton.disabled = true; // Disable the button to avoid redundant clicks
            playerTimesButton.disabled = false; // Enable the other button
            recordedTimesButton.classList.add("selected");
            playerTimesButton.classList.remove("selected");
            const selectedMap = dropdown.value;
            renderCurrentLeaderboard(selectedMap);
        });
    }

    function renderLeaderboardsTable(map, data, isIndividual = false) {
        const table = document.createElement("table");
        table.innerHTML = `
            <thead>
                <tr>
                    <th>#</th>
                    <th>${isIndividual ? "Best Player Times" : "Best Recorded Times"}</th>
                </tr>
            </thead>
            <tbody>
                ${data
                .map((entry, index) => `
                        <tr>
                            <td>${index + 1}</td>
                            <td>${entry}</td>
                        </tr>
                    `)
                .join("")}
            </tbody>
        `;
        const container = document.getElementById("leaderboards-table");
        container.innerHTML = ""; // Clear previous table
        container.appendChild(table);
    }

    function renderSummaryTable(allTimeStats, eloRatings) {
        let combinedStats = Object.entries(allTimeStats).map(([player, stats]) => ({
            Player: player,
            Races: stats.Races,
            Points: stats.Points,
            PPR: parseFloat(stats.PPR.toFixed(2)),
            ELO: parseFloat(eloRatings[player]?.["Current Rating"] || 0) // Default to 0 for missing ELO
        }));

        createAndRenderTableFromStats(
            "summary-table",
            {
                "Player": "",
                "Races": "",
                "Points": "Points are awarded based on placement- 1st: 25, 2nd: 18, 3rd: 15, 4th: 12, 5th: 10, 6th: 8, 7th: 6, 8th: 4",
                "PPR": "PPR: Points per race, calculated as total points divided by the number of races.",
                "ELO": "ELO: A rating system that tracks player performance based on race placements. Higher ELO indicates stronger performance relative to opponents."
            },
            combinedStats,
            [
                (stat) => stat.Player,
                (stat) => stat.Races,
                (stat) => stat.Points,
                (stat) => stat.PPR,
                (stat) => stat.ELO
            ],
            [
                {
                    "default": (stats) => stats.sort((a, b) => a.Player.localeCompare(b.Player)),
                    "reverse": (stats) => stats.sort((b, a) => a.Player.localeCompare(b.Player))
                }, // Player
                {
                    "default": (stats) => stats.sort((a, b) => b.Races - a.Races),
                    "reverse": (stats) => stats.sort((b, a) => b.Races - a.Races)
                }, // Races
                {
                    "default": (stats) => stats.sort((a, b) => b.Points - a.Points),
                    "reverse": (stats) => stats.sort((b, a) => b.Points - a.Points)
                }, // Points
                {
                    "default": (stats) => stats.sort((a, b) => b.PPR - a.PPR),
                    "reverse": (stats) => stats.sort((b, a) => b.PPR - a.PPR)
                }, // PPR
                {
                    "default": (stats) => stats.sort((a, b) => b.ELO - a.ELO),
                    "reverse": (stats) => stats.sort((b, a) => b.ELO - a.ELO)
                } // ELO
            ],
            4,
            true
        );
    }
});

document.addEventListener("DOMContentLoaded", () => {
    const resultsUrl = "results.json";

    // Fetch results data
    let resultsData = [];
    fetch(resultsUrl)
        .then((response) => response.json())
        .then((data) => {
            resultsData = data;
        })
        .catch((err) => console.error("Error fetching results data:", err));

    // Utility function to display messages
    function displayMessage(message, isError = false) {
        const messageContainer = document.getElementById("races-together-message");
        messageContainer.textContent = message;
        messageContainer.style.color = isError ? "red" : "white"; // Dynamic coloring
    }

    // Handle Fetch Races Together
    document.getElementById("fetch-races-together").addEventListener("click", () => {
        const input = document.getElementById("races-together-input").value.trim();
        if (!input) {
            displayMessage("Input cannot be empty.", true);
            return;
        }

        // Validate input: Split by commas, trim whitespace, and filter out empty strings
        let inputPlayers = input.split(",").map((player) => player.trim().toLowerCase()).filter(Boolean);
        inputPlayers = [...new Set(inputPlayers)]; // Remove duplicate player names

        if (inputPlayers.length < 2) {
            displayMessage("Invalid input format. Must enter at least 2 unique players.", true);
            return;
        }
        if (inputPlayers.length > 8) {
            displayMessage("Maximum of 8 players allowed.", true);
            return;
        }

        // Map input players to the correct case-sensitive player names in the global players list
        const validPlayers = inputPlayers.map((inputPlayer) =>
            players.find((player) => player.toLowerCase() === inputPlayer)
        ).filter(Boolean); // Filter out unmatched players

        if (validPlayers.length !== inputPlayers.length) {
            const invalidPlayers = inputPlayers.filter(
                (inputPlayer) => !players.some((player) => player.toLowerCase() === inputPlayer)
            );
            displayMessage(`Invalid player(s): ${invalidPlayers.join(", ")}`, true);
            return;
        }

        // Find races where all valid players participated
        const racesTogether = resultsData.filter((race) =>
            validPlayers.every((player) => race[`${player} Placement`] && race[`${player} Placement`] !== "DNR")
        );

        if (racesTogether.length === 0) {
            displayMessage(`Players (${validPlayers.join(", ")}) have not raced together.`, true);
            return;
        }

        displayMessage(`Found ${racesTogether.length} races together for (${validPlayers.join(", ")})`, false);

        // Calculate player stats
        const playerStats = validPlayers.reduce((stats, player) => {
            stats[player] = { Points: 0, Races: 0, TotalPlacement: 0 };
            return stats;
        }, {});

        const pointsAllocation = [25, 18, 15, 12, 10, 8, 6, 4];
        racesTogether.forEach((race) => {
            validPlayers.forEach((player) => {
                const placement = parseInt(race[`${player} Placement`], 10);
                playerStats[player].Races += 1;
                playerStats[player].Points += pointsAllocation[placement - 1] || 0;
                playerStats[player].TotalPlacement += placement;
            });
        });

        // Add PPR (Points Per Race) and Avg Position to stats
        Object.values(playerStats).forEach((stats) => {
            stats.PPR = (stats.Points / stats.Races).toFixed(2);
            stats.AvgPosition = (stats.TotalPlacement / stats.Races).toFixed(2);
        });

        // Render table
        renderRacesTogetherTable(playerStats);
        addProfilePictures();
    });

    function renderRacesTogetherTable(playerStats) {
        createAndRenderTableFromStats(
            "races-together-table",
            {
                "Player": "",
                "Races": "",
                "Points": "Points are awarded based on placement- 1st: 25, 2nd: 18, 3rd: 15, 4th: 12, 5th: 10, 6th: 8, 7th: 6, 8th: 4",
                "PPR": "PPR: Points per race, calculated as total points divided by the number of races.",
                "Avg Position": ""
            },
            Object.entries(playerStats),
            [
                ([player,]) => player,
                ([, stats]) => stats.Races,
                ([, stats]) => stats.Points,
                ([, stats]) => stats.PPR,
                ([, stats]) => stats.AvgPosition
            ],
            [
                {
                    "default": (stats) => stats.sort(([a,], [b,]) => a.localeCompare(b)),
                    "reverse": (stats) => stats.sort(([b,], [a,]) => a.localeCompare(b))
                }, // Player
                {
                    "default": (stats) => stats.sort(([, a], [, b]) => b.Races - a.Races),
                    "reverse": (stats) => stats.sort(([, b], [, a]) => b.Races - a.Races)
                }, // Races
                {
                    "default": (stats) => stats.sort(([, a], [, b]) => b.Points - a.Points),
                    "reverse": (stats) => stats.sort(([, b], [, a]) => b.Points - a.Points)
                }, // Points
                {
                    "default": (stats) => stats.sort(([, a], [, b]) => b.PPR - a.PPR),
                    "reverse": (stats) => stats.sort(([, b], [, a]) => b.PPR - a.PPR)
                }, // PPR
                {
                    "default": (stats) => stats.sort(([, b], [, a]) => b.AvgPosition - a.AvgPosition),
                    "reverse": (stats) => stats.sort(([, a], [, b]) => b.AvgPosition - a.AvgPosition)
                } // Avg Position
            ],
            3,
            true
        );
    }
});

document.querySelectorAll(".toggle-btn, #fetch-races-together").forEach((button) => {
    button.addEventListener("click", () => {
        // Add the bounce class
        button.classList.add("bounce");

        // Remove the bounce class after the animation ends
        button.addEventListener("animationend", () => {
            button.classList.remove("bounce");
        }, { once: true }); // Ensures the event listener is removed after one execution
    });
});

/*
// Global array to store players dynamically loaded from players.json
let players = [];

// Load players.json data when the DOM content is fully loaded
document.addEventListener("DOMContentLoaded", () => {
    const playersUrl = "../../docs/players.json";
    fetch(playersUrl)
        .then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then((data) => {
            // Assign the JSON array directly to the players variable
            players = data;
            console.log("Players loaded:", players);
        })
        .catch((err) => console.error("Error fetching players data:", err));
});
*/