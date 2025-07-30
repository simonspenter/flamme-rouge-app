// Function to log when the Classement tab is clicked
function onClassementTabOpened(event) {
    if (event.target && event.target.id === "classementTabButton") {
        console.log("Event triggered: Classement tab opened.");
        // Call the function to fetch classement data when the tab is opened
        fetchClassementData();
    }
}  // <-- Closing brace added here

// Function to fetch classement data and just log the message with correct race_id
function fetchClassementData() {
    // Fetch the race_id dynamically from the hidden input field
    const raceId = document.getElementById('race-id').value;  // Get the race_id from the hidden input field
    console.log(`Fetching classement data for race_id: ${raceId}`);

    // Perform the fetch request here for the correct race_id
    fetch(`/scoreboard?race=${raceId}`)
        .then(response => response.json())
        .then(data => {
            // For now, we just log the fetched data to check
            console.log("Fetched data:", data);
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
