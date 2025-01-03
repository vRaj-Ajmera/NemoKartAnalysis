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

function createAndRenderTableFromStats(containerName, columnNames, stats, columnValues, columnSort, defaultSort = 0, useProfilePictures = true) {
    let sortedStats = stats;

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


document.addEventListener("DOMContentLoaded", () => {
    const postAnalysisUrl = "elo_post_analysis.json"; // Path to elo_post_analysis.json
    const playerGraphsBasePath = "assets/player_graphs/"; // Path to player graphs

    // Fetch JSON data
    fetch(postAnalysisUrl)
        .then(response => response.json())
        .then(data => {
            populateRatingsTable(data["Player Ratings"]);
            populatePlayerDropdown(data["Player Ratings"]);
            populateKartDropdown(data["Player Ratings"]);

            addProfilePictures(); // Add profile pictures after the ratings table renders
        })
        .catch(err => console.error("Error fetching player stats data:", err));


    // Populate Ratings Table
    function populateRatingsTable(playerRatings) {
        createAndRenderTableFromStats(
            "ratings-table-container",
            ["Player", "Current Rating", "Peak Rating"],
            Object.entries(playerRatings),
            [(stat) => stat[0], (stat) => stat[1]["Current Rating"], (stat) => stat[1]["Peak Rating"]],
            [
                {
                    "default": (stats) => stats.sort(([p1,], [p2,]) => p1.localeCompare(p2)),
                    "reverse": (stats) => stats.sort(([p2,], [p1,]) => p1.localeCompare(p2))
                },
                {
                    "default": (stats) => stats.sort(([, a], [, b]) => b["Current Rating"] - a["Current Rating"]),
                    "reverse": (stats) => stats.sort(([, b], [, a]) => b["Current Rating"] - a["Current Rating"])
                },
                {
                    "default": (stats) => stats.sort(([, a], [, b]) => b["Peak Rating"] - a["Peak Rating"]),
                    "reverse": (stats) => stats.sort(([, b], [, a]) => b["Peak Rating"] - a["Peak Rating"])
                }
            ],
            1,
            true
        );
    }

    // Populate Player Dropdown for Elo Graph
    function populatePlayerDropdown(playerRatings) {
        const dropdown = document.getElementById("player-dropdown");
        Object.keys(playerRatings).forEach(player => {
            const option = document.createElement("option");
            option.value = player;
            option.textContent = player;
            dropdown.appendChild(option);
        });

        // Handle dropdown change
        dropdown.addEventListener("change", (e) => {
            const selectedPlayer = e.target.value;
            renderPlayerGraph(selectedPlayer);
        });
    }


    // Render Player Graph
    function renderPlayerGraph(player) {
        const graphContainer = document.getElementById("player-graph");
        graphContainer.innerHTML = ""; // Clear previous graph
        if (player) {
            const graphImage = document.createElement("img");
            graphImage.src = `${playerGraphsBasePath}${player}_elo_progression.png`;
            graphImage.alt = `Elo Progression Graph for ${player}`;
            graphImage.style.maxWidth = "100%";
            graphImage.style.height = "auto";
            graphContainer.appendChild(graphImage);
        }
    }


    // Populate Player Dropdown for Kart Usage
    function populateKartDropdown(playerRatings) {
        const dropdown = document.getElementById("player-kart-dropdown");
        Object.keys(playerRatings).forEach(player => {
            const option = document.createElement("option");
            option.value = player;
            option.textContent = player;
            dropdown.appendChild(option);
        });

        // Handle dropdown change
        dropdown.addEventListener("change", (e) => {
            const selectedPlayer = e.target.value;
            renderKartUsage(selectedPlayer, playerRatings);
        });
    }


    // Render Kart Usage Tables
    function renderKartUsage(player, playerRatings) {
        const container = document.getElementById("kart-usage-container");
        container.innerHTML = ""; // Clear previous content

        if (player && playerRatings[player]?.["Kart Usage"]) {
            const kartUsage = playerRatings[player]["Kart Usage"];

            Object.entries(kartUsage).forEach(([map, stats]) => {
                const mapTitle = document.createElement("h3");
                mapTitle.textContent = `${player}'s most used karts on ${map}`;
                container.appendChild(mapTitle);

                const table = document.createElement("table");
                table.classList.add("kart-usage-table");

                const thead = document.createElement("thead");
                thead.innerHTML = `
                    <tr>
                        <th>Kart</th>
                        <th>Races</th>
                        <th>Points</th>
                        <th>PPR</th>
                        <th>Avg Position</th>
                    </tr>
                `;
                table.appendChild(thead);

                const tbody = document.createElement("tbody");
                stats.forEach(kartStat => {
                    const row = document.createElement("tr");
                    row.innerHTML = `
                        <td>${kartStat["Kart"]}</td>
                        <td>${kartStat["Races"]}</td>
                        <td>${kartStat["Points"]}</td>
                        <td>${kartStat["PPR"]}</td>
                        <td>${kartStat["Avg Position"]}</td>
                    `;
                    tbody.appendChild(row);
                });
                table.appendChild(tbody);

                container.appendChild(table);
            });
        } else {
            const noDataMessage = document.createElement("p");
            noDataMessage.textContent = "No kart usage data available for the selected player.";
            container.appendChild(noDataMessage);
        }
    }
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