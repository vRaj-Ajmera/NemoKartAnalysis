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
        const tableBody = document.querySelector("#ratings-table tbody");

        // Sort playerRatings by Current Rating in descending order
        const sortedRatings = Object.entries(playerRatings).sort(([, a], [, b]) => b["Current Rating"] - a["Current Rating"]);

        // Populate the table with sorted data
        sortedRatings.forEach(([player, stats]) => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${player}</td>
                <td>${stats["Current Rating"]}</td>
                <td>${stats["Peak Rating"]}</td>
            `;
            tableBody.appendChild(row);
        });
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