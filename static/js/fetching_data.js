// Function to log when the Classement tab is clicked
function onClassementTabOpened(event) {
    if (event.target && event.target.id === "classementTabButton") {
        console.log("Event triggered: Classement tab opened.");
        // Call the function to fetch classement data when the tab is opened
        fetchClassementData();
    }
}  

function updateClassementTable(classementData) {
    console.log("UpdateClassementTable func received data:", classementData);

    // Loop through each stage
    Object.keys(classementData).forEach(stage_id => {
        let stage = classementData[stage_id];
        Object.keys(stage).forEach(team_id => {
            let team = stage[team_id];
            Object.keys(team).forEach(rider_id => {
                // Get the table cell by ID (combining stage_id, team_id, rider_id)
                let cell = document.getElementById(`classement-stage-${stage_id}-team-${team_id}-rider-${rider_id}`);
                if (cell) {
                    // Update the cell with the placement data
                    cell.innerHTML = team[rider_id];
                }
            });
        });
    });
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





// Ensure the DOM is loaded before attaching event listeners
document.addEventListener("DOMContentLoaded", function () {
    // Attach the event listener to the "Classement" tab button
    attachClassementTabListener();
});
