document.addEventListener("DOMContentLoaded", () => {
    const postAnalysisUrl = "post_analysis.json";

    // Fetch JSON data
    fetch(postAnalysisUrl)
        .then(response => response.json())
        .then(data => {
            renderSummaryTable(data["All Time Stats"]);
            populateDailyStatsDropdown(data["Daily Stats"]);
            renderRacesTogetherTable(data["Races Together"]);
            populateLeaderboardsDropdown(data["Best Race Times"]);
        })
        .catch(err => console.error("Error fetching analysis data:", err));

    // Render Summary Table
    function renderSummaryTable(stats) {
        const table = document.createElement("table");
        table.innerHTML = `
            <thead>
                <tr>
                    <th>Player</th>
                    <th>Races</th>
                    <th>Points</th>
                    <th>PPR</th>
                    <th>Avg Position</th>
                </tr>
            </thead>
            <tbody>
                ${Object.entries(stats).map(([player, stat]) => {
                    const imagePath = `assets/icons/${player}.png`; // Path to profile images
                    return `
                        <tr>
                            <td>
                                <img src="${imagePath}" alt="${player}" class="profile-pic" />
                                ${player}
                            </td>
                            <td>${stat.Races}</td>
                            <td>${stat.Points}</td>
                            <td>${stat.PPR.toFixed(2)}</td>
                            <td>${stat["Avg Race Position"]?.toFixed(2) ?? "N/A"}</td>
                        </tr>
                    `;
                }).join("")}
            </tbody>
        `;
        document.getElementById("summary-table").appendChild(table);
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
        const table = document.createElement("table");
        table.innerHTML = `
            <thead>
                <tr>
                    <th>Player</th>
                    <th>Races</th>
                    <th>Points</th>
                    <th>PPR</th>
                    <th>Avg Position</th>
                </tr>
            </thead>
            <tbody>
                ${Object.entries(stats).map(([player, stat]) => `
                    <tr>
                        <td>${player}</td>
                        <td>${stat.Races}</td>
                        <td>${stat.Points}</td>
                        <td>${stat.PPR.toFixed(2)}</td>
                        <td>${stat["Avg Race Position"]?.toFixed(2) ?? "N/A"}</td>
                    </tr>
                `).join("")}
            </tbody>
        `;
        const container = document.getElementById("daily-stats-table");
        container.innerHTML = ""; // Clear previous table
        container.appendChild(table);
    }

    // Render Races Together Table
    function renderRacesTogetherTable(stats) {
        const table = document.createElement("table");
        table.innerHTML = `
            <thead>
                <tr>
                    <th>Player</th>
                    <th>Races</th>
                    <th>Points</th>
                    <th>PPR</th>
                    <th>Avg Position</th>
                </tr>
            </thead>
            <tbody>
                ${Object.entries(stats).map(([player, stat]) => `
                    <tr>
                        <td>${player}</td>
                        <td>${stat.Races}</td>
                        <td>${stat.Points}</td>
                        <td>${stat.PPR.toFixed(2)}</td>
                        <td>${stat["Avg Race Position"]?.toFixed(2) ?? "N/A"}</td>
                    </tr>
                `).join("")}
            </tbody>
        `;
        const container = document.getElementById("races-together-table");
        container.innerHTML = ""; // Clear previous table
        container.appendChild(table);
    }

    // Populate and handle Leaderboards Dropdown
    function populateLeaderboardsDropdown(leaderboards) {
        const dropdown = document.getElementById("map-dropdown");
        Object.keys(leaderboards).forEach(map => {
            const option = document.createElement("option");
            option.value = map;
            option.textContent = map;
            dropdown.appendChild(option);
        });

        dropdown.addEventListener("change", (e) => {
            if (e.target.value !== "-- Select --") {
                renderLeaderboardsTable(leaderboards[e.target.value]);
                e.target.querySelector("option[value='-- Select --']").remove(); // Remove "-- Select --"
            }
        });
    }

    // Render Leaderboards Table
    function renderLeaderboardsTable(leaderboard) {
        const table = document.createElement("table");
        table.innerHTML = `
            <thead>
                <tr>
                    <th>#</th>
                    <th>Details</th>
                </tr>
            </thead>
            <tbody>
                ${leaderboard.map((entry, index) => `
                    <tr>
                        <td>${index + 1}</td>
                        <td>${entry}</td>
                    </tr>
                `).join("")}
            </tbody>
        `;
        const container = document.getElementById("leaderboards-table");
        container.innerHTML = ""; // Clear previous table
        container.appendChild(table);
    }
});
