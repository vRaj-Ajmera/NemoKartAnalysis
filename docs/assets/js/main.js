function addProfilePictures() {
    const players = ["Raj", "Azhan", "Sameer", "Zetaa", "Adi", "Dylan", "Parum", "EnderRobot", "Lynden", "Rusheel"];
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

function createAndRenderTableFromStats(containerName, columnNames, stats, columnValues, columnSort, defaultSort = 0, useProfilePictures = false) {
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

    // Fetch JSON data
    fetch(postAnalysisUrl)
        .then(response => response.json())
        .then(data => {
            renderSummaryTable(data["All Time Stats"]);
            populateDailyStatsDropdown(data["Daily Stats"]);
            renderRacesTogetherTable(data["Races Together"]);
            populateLeaderboardsDropdown(data["Best Race Times"], data["Individual Player Best Times"]); // <-- Called here
        })
        .catch(err => console.error("Error fetching analysis data:", err));

    // Render Summary Table
    function renderSummaryTable(stats) {
        createAndRenderSummaryTable("summary-table", stats);
    }


    // Populate and handle Daily Stats Dropdown
    function populateDailyStatsDropdown(dailyStats) {
        const dropdown = document.getElementById("daily-stats-dropdown");
        Object.keys(dailyStats).forEach(date => {
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


    // Render Races Together Table
    function renderRacesTogetherTable(stats) {
        createAndRenderSummaryTable("races-together-table", stats);
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
});
