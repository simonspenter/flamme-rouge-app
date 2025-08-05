// CLASSEMENT DATA //

// Function to log when the Classement tab is clicked
function onClassementTabOpened(event) {
    if (event.target && event.target.id === "classementTabButton") {
        // Call the function to fetch classement data when the tab is opened
        fetchClassementData();
    }
}  

function updateClassementTable(classementData) {
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

    const url = `/api/classement_data?race=${raceId}`;

    fetch(url)
        .then(response => {
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


// SEGMENT DATA //

// Function to log when the Sprint tab is clicked
function onSprintTabOpened(event) {
    if (event.target && event.target.id === "sprintTabButton") {
        // Fetch sprint data
        fetchSegmentData('sprint');
    }
}

// Function to log when the Mountain tab is clicked
function onMountainTabOpened(event) {
    if (event.target && event.target.id === "mountainTabButton") {
        // Fetch mountain data
        fetchSegmentData('mountain');
    }
}

// Attach event listeners to the tab buttons
document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("sprintTabButton").addEventListener("click", onSprintTabOpened);
    document.getElementById("mountainTabButton").addEventListener("click", onMountainTabOpened);
});


// Function to fetch segment data for the relevant table
function fetchSegmentData(segmentType) {
    const raceId = document.getElementById('race-id').value;  // Get race_id from the hidden input field

    const url = `/api/segment_data?race=${raceId}&segment_type=${segmentType}`;

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();  // Parse the response body as JSON
        })
        .then(data => {
            console.log(`Fetched ${segmentType} data:`, data);
            // Pass the fetched data to the table update function
            if (segmentType === 'sprint') {
                updateSprintTable(data);
            } else if (segmentType === 'mountain') {
                updateMountainTable(data);
            }
        })
        .catch(error => {
            console.error("Error fetching data:", error);
        });
}

// Function to update the sprint table
function updateSprintTable(sprintData) {
    // Loop through each stage and team
    Object.keys(sprintData).forEach(stage_id => {
        let stage = sprintData[stage_id];
        Object.keys(stage).forEach(team_id => {
            let team = stage[team_id];
            Object.keys(team).forEach(rider_id => {
                // Get the table cell by ID
                let cell = document.getElementById(`sprint-stage-${stage_id}-team-${team_id}-rider-${rider_id}`);
                if (cell) {
                    // Update the cell with the points data
                    cell.innerHTML = team[rider_id];
                }
            });
        });
    });
}

// Function to update the mountain table
function updateMountainTable(mountainData) {
    // Loop through each stage and team
    Object.keys(mountainData).forEach(stage_id => {
        let stage = mountainData[stage_id];
        Object.keys(stage).forEach(team_id => {
            let team = stage[team_id];
            Object.keys(team).forEach(rider_id => {
                // Get the table cell by ID
                let cell = document.getElementById(`mountain-stage-${stage_id}-team-${team_id}-rider-${rider_id}`);
                if (cell) {
                    // Update the cell with the points data
                    cell.innerHTML = team[rider_id];
                }
            });
        });
    });
}
