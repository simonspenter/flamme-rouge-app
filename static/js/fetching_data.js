// Function to log when the Classement tab is clicked
function onClassementTabOpened(event) {
    if (event.target && event.target.id === "classementTabButton") {
        console.log("Event triggered: Classement tab opened.");
        // Call the function to fetch classement data when the tab is opened
        fetchClassementData();
    }
}  // <-- Closing brace added here

function fetchClassementData() {
    // Fetch the race_id dynamically from the hidden input field
    const raceId = document.getElementById('race-id').value;  // Get the race_id from the hidden input field
    console.log(`Fetching classement data for race_id: ${raceId}`);

    fetch(`/scoreboard?race=${raceId}`)
        .then(response => {
            // Log the status of the response
            console.log(`Response status: ${response.status}`);
            
            // If the response is not OK, check for HTML content
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            // If the response is HTML (not JSON), log the raw HTML
            if (response.headers.get("Content-Type").includes("text/html")) {
                response.text().then(html => {
                    console.error("Unexpected HTML content received:", html);
                });
                throw new Error("Received HTML content, expected JSON.");
            }

            return response.json();  // Parse the response body as JSON
        })
        .then(data => {
            // For now, we just log the fetched data to check
            console.log("Fetched data:", data);
        })
        .catch(error => {
            // Log the error if there's any issue with the fetch
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
