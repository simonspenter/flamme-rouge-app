// /static/js/fetching_data.js

// Function to log when the Classement tab is clicked
function onClassementTabOpened(event) {
    console.log("Tab clicked:", event.target); // Check which element was clicked
    if (event.target && event.target.id === "classementTabButton") {
        console.log("Event triggered: Classement tab opened.");
        // You can also trigger your data-fetching function here
        fetchClassementData();
    }
}

// Function to fetch classement data (example placeholder function)
function fetchClassementData() {
    const raceId = '{{ race_id }}';  // Make sure race_id is passed in the template

    console.log(`Fetching classement data for race_id: ${raceId}`);

    fetch(`/scoreboard?race=${raceId}`)
        .then(response => response.json())
        .then(data => {
            console.log("Fetched data:", data);
            // Process the fetched data here
        })
        .catch(error => console.error("Error fetching data:", error));
}

// Function to add event listener to the classement tab button
function attachClassementTabListener() {
    const classementTabButton = document.getElementById("classementTabButton");
    if (classementTabButton) {
        classementTabButton.addEventListener("click", onClassementTabOpened);
    }
}

// Ensure the DOM is loaded before attaching event listeners
document.addEventListener("DOMContentLoaded", function () {
    attachClassementTabListener();
});
