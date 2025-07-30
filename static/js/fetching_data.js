// Function to log when the Classement tab is clicked
function onClassementTabOpened(event) {
    if (event.target && event.target.id === "classementTabButton") {
        console.log("Event triggered: Classement tab opened.");
        // Call the function to fetch classement data when the tab is opened
        fetchClassementData();
    }
}

function updateClassementTable(data) {
    // Loop through the stages, teams, and riders to populate the table with the correct placement
    for (let stageId in data) {
        for (let teamId in data[stageId]) {
            for (let riderId in data[stageId][teamId]) {
                const placement = data[stageId][teamId][riderId];
                const cellId = `classement-stage-${stageId}-team-${teamId}-rider-${riderId}`;
                const cell = document.getElementById(cellId);
                if (cell) {
                    cell.innerText = placement;  // Update the cell with the placement value
                }
            }
        }
    }
}

// Function to fetch classement data
function fetchClassementData() {
    const raceId = document.getElementById('race-id').value;  // Get the race_id from the hidden input field
    console.log(`Fetching classement data for race_id: ${raceId}`);

    const url = `/api/classement_data?race=${raceId}`;
    console.log("Requesting URL:", url);  // Log the full URL

    fetch(url)
        .then(response => {
            console.log("Response status:", response.status);  // Log response status
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();  // Parse the response body as JSON
        })
        .then(data => {
            console.log("Fetched data:", data);
            // Update the table with the fetched data
            updateClassementTable(data);
        })
        .catch(error => {
            console.error("Error fetching data:", error);
        });
}




// Function to add event listener to the "Classement" tab button
function attachClassementTabListener() {
    const classementTabButton = document.getElementById("classementTabButton");
    if (classementTabButton) {
        classementTabButton.addEventListener("click", onClassementTabOpened);
    }
}

// Ensure the DOM is loaded before attaching event listeners
document.addEventListener("DOMContentLoaded", function () {
    // Attach the event listener to the "Classement" tab button
    attachClassementTabListener();
});
