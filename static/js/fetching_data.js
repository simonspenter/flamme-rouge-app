// Function to log when the Classement tab is clicked
function onClassementTabOpened(event) {
    if (event.target && event.target.id === "classementTabButton") {
        console.log("Event triggered: Classement tab opened.");
        // Call the function to fetch classement data when the tab is opened
        fetchClassementData();
    }
}  

function updateClassementTable(data) {
    console.log("Updating classement table with data:", data);
    
    // Loop through each stage in the data
    for (let stage_id in data) {
        let stageData = data[stage_id];
        for (let team_id in stageData) {
            let teamData = stageData[team_id];
            for (let rider_id in teamData) {
                let placement = teamData[rider_id];

                // Construct the corresponding table cell
                let cellId = `classement-stage-${stage_id}-team-${team_id}-rider-${rider_id}`;
                let cell = document.getElementById(cellId);

                if (cell) {
                    // Set the placement in the correct table cell
                    cell.textContent = placement || '';  // If no placement, leave it empty
                }
            }
        }
    }
}


function fetchClassementData() {
    const raceId = document.getElementById('race-id').value;  // Get the race_id from the hidden input field
    console.log(`Fetching classement data for race_id: ${raceId}`);

    const url = `/api/classement_data?race=${raceId}`;
    console.log("Requesting URL:", url);

    fetch(url)
        .then(response => {
            console.log("Response status:", response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();  // Parse the response body as JSON
        })
        .then(data => {
            console.log("Fetched data:", data);
            // Pass the fetched data to the table update function
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
