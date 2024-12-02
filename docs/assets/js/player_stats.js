document.addEventListener("DOMContentLoaded", () => {
    const postAnalysisUrl = "elo_post_analysis.json"; // Path to elo_post_analysis.json
    const playerGraphsBasePath = "assets/player_graphs/"; // Path to player graphs

    // Fetch JSON data
    fetch(postAnalysisUrl)
        .then(response => response.json())
        .then(data => {
            populateRatingsTable(data["Player Ratings"]);
            populatePlayerDropdown(data["Player Ratings"]);
        })
        .catch(err => console.error("Error fetching player stats data:", err));

    // Populate Ratings Table
    function populateRatingsTable(playerRatings) {
        const tableBody = document.querySelector("#ratings-table tbody");
        Object.entries(playerRatings).forEach(([player, stats]) => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${player}</td>
                <td>${stats["Current Rating"]}</td>
                <td>${stats["Peak Rating"]}</td>
            `;
            tableBody.appendChild(row);
        });
    }

    // Populate Player Dropdown
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
});
