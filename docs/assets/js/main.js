function addProfilePictures() {
    const players = ["Raj", "Azhan", "Sameer", "Zetaa", "Adi", "Dylan", "Parum", "EnderRobot", "Lynden", "Rusheel", "SultanSpeppy", "Viraj"];
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

function createAndRenderTableFromStats(containerName, columnNames, stats, columnValues, columnSort, defaultSort = 0, useProfilePictures = true) {
    let sortedStats = stats;

    function sortTable(columnNo) {
        sortedStats = columnSort[columnNo](stats);
    }

    function createInnerHTML() {
        return `
            <thead>
                <tr>
                    ${columnNames.map((columnName, index) => `<th id="${index}">${columnName}</th>`).join("")}
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

    sortTable(defaultSort);
    createAndRenderTable(createInnerHTML());
}

function createAndRenderSummaryTable(containerName, stats) {
    createAndRenderTableFromStats(
        containerName,
        [
            "Player",
            "Races",
            "Points",
            "PPR",
            "Avg Position"
        ],
        stats,
        [
            ([a,]) => a,
            ([, b]) => b.Races,
            ([, b]) => b.Points,
            ([, b]) => b.PPR.toFixed(2),
            ([, b]) => b["Avg Race Position"]?.toFixed(2) ?? "N/A"
        ],
        [
            (stats,) => Object.entries(stats).sort(([a,], [b,]) => a.localeCompare(b)), // Player
            (stats,) => Object.entries(stats).sort(([, a], [, b]) => b.Races - a.Races), // Races
            (stats,) => Object.entries(stats).sort(([, a], [, b]) => b.Points - a.Points), // Points
            (stats,) => Object.entries(stats).sort(([, a], [, b]) => b.PPR - a.PPR), // PPR
            (stats,) => Object.entries(stats).sort(([, a], [, b]) => (a["Avg Race Position"] - b["Avg Race Position"])), // Avg Position
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
        populateRacesTogetherDropdowns(postAnalysisData["All Time Stats"], postAnalysisData["Daily Stats"]); // Add this
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


    function populateRacesTogetherDropdowns(allTimeStats, dailyStats) {
        const players = Object.keys(allTimeStats);
        const dropdownIds = ["player1-dropdown", "player2-dropdown", "player3-dropdown", "player4-dropdown"];
    
        dropdownIds.forEach((id) => {
            const dropdown = document.getElementById(id);
            dropdown.innerHTML = '<option value="">-- Select --</option>'; // Clear previous options
            players.forEach((player) => {
                const option = document.createElement("option");
                option.value = player;
                option.textContent = player;
                dropdown.appendChild(option);
            });
        });
        document.getElementById("fetch-races-together").addEventListener("click", () => {
            const players = [
                document.getElementById("player1-dropdown").value,
                document.getElementById("player2-dropdown").value,
                document.getElementById("player3-dropdown").value,
                document.getElementById("player4-dropdown").value,
            ];
        
            const racesTogether = findRacesTogether(players, dailyStats);
            renderRacesTogetherTable(racesTogether);
        });
    }
    
    function findRacesTogether(players, dailyStats) {
        const selectedPlayers = players.filter((player) => player);
        if (selectedPlayers.length < 2) {
            document.getElementById("races-together-message").textContent = "Select at least 2 players.";
            return [];
        }
    
        document.getElementById("races-together-message").textContent = "";
    
        const racesTogether = [];
        Object.entries(dailyStats).forEach(([date, stats]) => {
            console.log(`Processing date: ${date}, stats type: ${typeof stats}`, stats); // Debugging log
    
            // Ensure stats is an object
            if (typeof stats !== "object" || Array.isArray(stats)) {
                console.warn(`Stats for ${date} is not a valid object. Skipping.`);
                return;
            }
    
            const allInRace = selectedPlayers.every((player) => player in stats);
            if (allInRace) {
                racesTogether.push({
                    date,
                    ...selectedPlayers.reduce((race, player) => {
                        race[player] = { Points: stats[player]?.Points || 0 };
                        return race;
                    }, {}),
                });
            }
        });
    
        if (racesTogether.length === 0) {
            document.getElementById("races-together-message").textContent = "Selected players have not raced together.";
        }
    
        return racesTogether;
    }
    
    
    function renderRacesTogetherTable(racesTogether, selectedPlayers) {
        console.log("Rendering races together table..."); // Debugging log
        console.log("Selected Players:", selectedPlayers); // Debugging log
        console.log("Races Together Data:", racesTogether); // Debugging log
    
        if (racesTogether.length === 0) {
            document.getElementById("races-together-table").innerHTML = "<p>No races found.</p>";
            console.warn("No races found for the selected players."); // Debugging log
            return;
        }
    
        const playerStats = selectedPlayers.reduce((stats, player) => {
            stats[player] = { Races: 0, Points: 0, PPR: 0, "Avg Position": 0, TotalPlacement: 0 };
            return stats;
        }, {});
    
        const pointsAllocation = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1];
    
        racesTogether.forEach((race) => {
            selectedPlayers.forEach((player) => {
                if (race[player]) {
                    playerStats[player].Races += 1;
                    const placement = parseInt(race[player].Placement, 10) || 0;
                    playerStats[player].Points += pointsAllocation[placement - 1] || 0;
                    playerStats[player].TotalPlacement += placement;
                }
            });
        });
    
        Object.values(playerStats).forEach((stats) => {
            if (stats.Races > 0) {
                stats.PPR = (stats.Points / stats.Races).toFixed(2);
                stats["Avg Position"] = (stats.TotalPlacement / stats.Races).toFixed(2);
            } else {
                stats.PPR = "N/A";
                stats["Avg Position"] = "N/A";
            }
        });
    
        const columnNames = ["Player", "Races", "Points", "PPR", "Avg Position"];
        const table = document.createElement("table");
        table.innerHTML = `
            <thead>
                <tr>${columnNames.map((col) => `<th>${col}</th>`).join("")}</tr>
            </thead>
            <tbody>
                ${Object.entries(playerStats)
                    .map(
                        ([player, stats]) => `
                        <tr>
                            <td>${player}</td>
                            <td>${stats.Races}</td>
                            <td>${stats.Points}</td>
                            <td>${stats.PPR}</td>
                            <td>${stats["Avg Position"]}</td>
                        </tr>
                    `
                    )
                    .join("")}
            </tbody>
        `;
        const container = document.getElementById("races-together-table");
        if (!container) {
            console.error("Container for races-together-table not found."); // Debugging log
            return;
        }
        container.innerHTML = ""; // Clear previous table
        container.appendChild(table);
    }    
    

    function populateLeaderboardsDropdown(leaderboards, individualBestTimes) {
        const dropdown = document.getElementById("map-dropdown");
        const toggleButton = document.getElementById("toggle-leaderboard");
    
        let isIndividual = false; // Track toggle state
    
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
    
        dropdown.addEventListener("change", (e) => {
            const selectedMap = dropdown.value;
    
            // Ensure the "Select" option remains greyed out but selectable maps can still be chosen
            if (selectedMap && selectedMap !== "-- Select --") {
                renderLeaderboardsTable(
                    selectedMap,
                    leaderboards[selectedMap],
                    individualBestTimes,
                    isIndividual
                );
            }
        });
    
        toggleButton.addEventListener("click", () => {
            isIndividual = !isIndividual;
            toggleButton.textContent = isIndividual
                ? "Switch to Best Race Times"
                : "Switch to Individual Best Times";
    
            const selectedMap = dropdown.value;
            if (selectedMap && selectedMap !== "-- Select --") {
                renderLeaderboardsTable(
                    selectedMap,
                    leaderboards[selectedMap],
                    individualBestTimes,
                    isIndividual
                );
            }
        });
    }
    
    function renderLeaderboardsTable(map, leaderboard, individualBestTimes, isIndividual = false) {
        const table = document.createElement("table");
        table.innerHTML = `
            <thead>
                <tr>
                    <th>#</th>
                    <th>${isIndividual ? "Player Best Time" : "Details"}</th>
                </tr>
            </thead>
            <tbody>
                ${isIndividual
                    ? individualBestTimes[map]
                        .map((entry, index) => `
                            <tr>
                                <td>${index + 1}</td>
                                <td>${entry}</td>
                            </tr>
                        `)
                        .join("")
                    : leaderboard
                        .map((entry, index) => `
                            <tr>
                                <td>${index + 1}</td>
                                <td>${entry}</td>
                            </tr>
                        `)
                        .join("")
                }
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
    
        // Initial sort by ELO descending
        combinedStats.sort((a, b) => b.ELO - a.ELO);
    
        const container = document.getElementById("summary-table");
    
        function renderTable(stats) {
            const table = document.createElement("table");
            table.innerHTML = `
                <thead>
                    <tr>
                        <th id="Player">Player</th>
                        <th id="Races">Races</th>
                        <th id="Points">
                            Points 
                            <div class="info-icon" data-tooltip="Points are awarded based on the F1 system: 
                            1st: 25, 2nd: 18, 3rd: 15, 4th: 12, 5th: 10, 6th: 8, 7th: 6, 8th: 4">i</div>
                        </th>
                        <th id="PPR">
                            PPR 
                            <div class="info-icon" data-tooltip="PPR: Points per race, calculated as total points divided by the number of races.">i</div>
                        </th>
                        <th id="ELO">
                            ELO 
                            <div class="info-icon" data-tooltip="ELO: A rating system that tracks player performance. The base rating starts at 1000 and increases or decreases based on race results compared to other players' ratings. Higher ELO indicates stronger performance relative to opponents.">i</div>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    ${stats.map(stat => `
                        <tr>
                            <td>${stat.Player}</td>
                            <td>${stat.Races}</td>
                            <td>${stat.Points}</td>
                            <td>${stat.PPR.toFixed(2)}</td>
                            <td>${stat.ELO}</td>
                        </tr>
                    `).join("")}
                </tbody>
            `;
            container.innerHTML = ""; // Clear previous table
            container.appendChild(table);
    
            // Add click event listeners to headers for sorting
            const headers = table.querySelectorAll("th");
            headers.forEach(header => {
                header.addEventListener("click", () => {
                    const sortKey = header.id;
                    const isAscending = header.classList.contains("asc");
    
                    // Remove existing sort classes
                    headers.forEach(h => h.classList.remove("asc", "desc"));
    
                    // Sort the table
                    combinedStats.sort((a, b) => {
                        if (sortKey === "Player") return !isAscending ? a.Player.localeCompare(b.Player) : b.Player.localeCompare(a.Player);
                        return isAscending ? a[sortKey] - b[sortKey] : b[sortKey] - a[sortKey];
                    });
    
                    // Toggle sort direction
                    header.classList.toggle("asc", !isAscending);
                    header.classList.toggle("desc", isAscending);
    
                    // Re-render the table
                    renderTable(combinedStats);
                    addProfilePictures();
                });
            });
        }
        // Initial render
        renderTable(combinedStats);
    }
});
