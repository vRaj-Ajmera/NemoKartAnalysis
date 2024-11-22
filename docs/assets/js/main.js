document.addEventListener("DOMContentLoaded", () => {
    const postAnalysisUrl = "post_analysis.json";

    // Fetch JSON data
    fetch(postAnalysisUrl)
        .then(response => response.json())
        .then(data => {
            renderSummaryTable(data.all_time_stats);
            populateDailyStatsDropdown(data.daily_stats);
            populateLeaderboardsDropdown(data.map_leaderboards);
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
                ${Object.entries(stats).map(([player, stat]) => `
                    <tr>
                        <td>${player}</td>
                        <td>${stat.races}</td>
                        <td>${stat.points}</td>
                        <td>${stat.ppr.toFixed(2)}</td>
                        <td>${stat.avg_position.toFixed(2)}</td>
                    </tr>
                `).join("")}
            </tbody>
        `;
        document.getElementById("summary-table").appendChild(table);
    }

    // Populate Daily Stats Dropdown
    function populateDailyStatsDropdown(dailyStats) {
        const dropdown = document.getElementById("daily-stats-dropdown");
        Object.keys(dailyStats).forEach(date => {
            const option = document.createElement("option");
            option.value = date;
            option.textContent = date;
            dropdown.appendChild(option);
        });

        // Render table on change
        dropdown.addEventListener("change", (e) => {
            renderDailyStatsTable(dailyStats[e.target.value]);
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
                        <td>${stat.races}</td>
                        <td>${stat.points}</td>
                        <td>${stat.ppr.toFixed(2)}</td>
                        <td>${stat.avg_position.toFixed(2)}</td>
                    </tr>
                `).join("")}
            </tbody>
        `;
        const container = document.getElementById("daily-stats-table");
        container.innerHTML = ""; // Clear previous table
        container.appendChild(table);
    }

    // Populate Leaderboards Dropdown
    function populateLeaderboardsDropdown(leaderboards) {
        const dropdown = document.getElementById("map-dropdown");
        Object.keys(leaderboards).forEach(map => {
            const option = document.createElement("option");
            option.value = map;
            option.textContent = map;
            dropdown.appendChild(option);
        });

        // Render table on change
        dropdown.addEventListener("change", (e) => {
            renderLeaderboardsTable(leaderboards[e.target.value]);
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
