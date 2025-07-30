// Function to log when the Classement tab is clicked
function onClassementTabOpened(event) {
    console.log("Tab clicked:", event.target); // Check which element was clicked
    if (event.target && event.target.id === "classementTabButton") {
        console.log("Event triggered: Classement tab opened.");
        // Call the function to fetch classement data when the tab is opened
        fetchClassementData();
    }
}

// Function to fetch classement data for the specific race
function fetchClassementData() {
    const raceId = "{{ race_id }}";  // Ensure race_id is passed from the template

    console.log(`Fetching classement data for race_id: ${raceId}`);

    // Fetch the data from the server (use the raceId dynamically in the URL)
    fetch(`/scoreboard?race=${raceId}`)
        .then(response => response.json())  // Parse the JSON response
        .then(data => {
            console.log("Fetched data:", data);  // Log the entire data for debugging

            // Process and display the fetched data (classement_data)
            const classementData = data.classement_data;
            console.log("Classement Data to be displayed:", classementData);

            // Example of iterating through the fetched classement data and logging it
            for (let stageId in classementData) {
                console.log(`Stage ${stageId}:`);
                for (let teamId in classementData[stageId]) {
                    for (let riderId in classementData[stageId][teamId]) {
                        const placement = classementData[stageId][teamId][riderId];
                        console.log(`Team ${teamId}, Rider ${riderId} - Placement: ${placement}`);
                    }
                }
            }
        })
        .catch(error => {
            console.error("Error fetching data:", error);  // Handle errors if the fetch fails
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
