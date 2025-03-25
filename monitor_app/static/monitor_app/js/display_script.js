// Function to update data and refresh page
function updateAndRefresh() {
    // Make AJAX call to aggregates_data endpoint
    fetch('/aggregates_data/', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => {
        if (response.ok) {
            // Refresh the page after successful update
            window.location.reload();
        } else {
            console.error('Failed to update data');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Run immediately on page load
updateAndRefresh();

// Set interval to run every 30 seconds (30000 milliseconds)
setInterval(updateAndRefresh, 30000);