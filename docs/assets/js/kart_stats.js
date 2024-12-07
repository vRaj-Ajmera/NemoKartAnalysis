document.addEventListener("DOMContentLoaded", () => {
    const mapDropdown = document.getElementById("mapDropdown");
    const graphsContainer = document.getElementById("graphsContainer");

    // Define the available maps and corresponding graph paths
    const mapGraphs = {
        "Shanghai": ["docs/assets/kart_graphs/Shanghai_kart_racetimes.png", "docs/assets/kart_graphs/Shanghai_kart_placements.png"],
        "Shanghai by Night": ["docs/assets/kart_graphs/Shanghai by Night_kart_racetimes.png", "docs/assets/kart_graphs/Shanghai by Night_kart_placements.png"],
        "Snowville": ["docs/assets/kart_graphs/Snowville_kart_racetimes.png", "docs/assets/kart_graphs/Snowville_kart_placements.png"]
    };

    // Add the default "-- Select --" option
    const defaultOption = document.createElement("option");
    defaultOption.value = "";
    defaultOption.textContent = "-- Select --";
    defaultOption.disabled = true;
    defaultOption.selected = true;
    mapDropdown.appendChild(defaultOption);

    // Populate the dropdown with map options
    for (const mapName in mapGraphs) {
        const option = document.createElement("option");
        option.value = mapName;
        option.textContent = mapName;
        mapDropdown.appendChild(option);
    }

    // Update graphs when a map is selected
    mapDropdown.addEventListener("change", () => {
        const selectedMap = mapDropdown.value;
        graphsContainer.innerHTML = ""; // Clear existing graphs

        if (selectedMap && mapGraphs[selectedMap]) {
            mapGraphs[selectedMap].forEach(graphPath => {
                const img = document.createElement("img");
                img.src = graphPath;
                img.alt = `Graph for ${selectedMap}`;
                img.style.maxWidth = "100%"; // Make images responsive
                img.style.marginBottom = "20px"; // Add some spacing
                graphsContainer.appendChild(img);
            });
        }
    });
});
