function loadEmailContent(emailId) {
    fetch(`/read_email/${emailId}`)
        .then(response => response.text())
        .then(content => {
            const emailContentWrapper = document.getElementById("email-content-wrapper");
            emailContentWrapper.style.display = "block"; // Show the content wrapper
            const topTen = document.getElementById("top-senders");
            topTen.style.display = "none";
            document.getElementById("email-content").innerHTML = content;
        });
}

function closeEmailContent() {
    const emailContentWrapper = document.getElementById("email-content-wrapper");
    emailContentWrapper.style.display = "none"; // Hide the content wrapper
    const topTen = document.getElementById("top-senders");
    topTen.style.display = "block";
}


$(document).ready(function() {
    var initialData;

    // Fetch initial JSON data
    $.getJSON("/static/emails.json", function(data) {
        initialData = data;

        // Call a function to populate the page with the initial data
        populatePage(initialData);
    });

    // Function to populate the page with data
    function populatePage(data) {
        // Extract sender and subject data
        var senderData = data.sender;
        var subjectData = data.subject;
        // Sort sender data by value in descending order
        var sortedSenderData = Object.entries(senderData).sort((a, b) => b[1] - a[1]);

        // Sort subject data by value in descending order
        var sortedSubjectData = Object.entries(subjectData).sort((a, b) => b[1] - a[1]);

        // Take the top 10 entries for sender and subject
        var top10Sender = sortedSenderData.slice(0, 10);
        var top10Subject = sortedSubjectData.slice(0, 10);

        // Display the top 10 sender and subject data on the screen
        var dataContainer = $("#data-container");
        dataContainer.empty(); // Clear previous data
        var dataHtml = "<h2>Top 10 Senders:</h2>";
        dataHtml += "<ul>";
        top10Sender.forEach(function(entry) {
            dataHtml += "<li>Sender: " + entry[0] + ", Count: " + entry[1] + "</li>";
        });
        dataHtml += "</ul>";

        dataHtml += "<h2>Top 10 Subjects:</h2>";
        dataHtml += "<ul>";
        top10Subject.forEach(function(entry) {
            dataHtml += "<li>Subject: " + entry[0] + ", Count: " + entry[1] + "</li>";
        });
        dataHtml += "</ul>";

        dataContainer.append(dataHtml);
    }
    // Function to handle button click
    $("#show-data").click(function() {
        var dataContainer = $("#data-container");
        // Update the header to indicate that the update is in progress
        dataContainer.find("h2").html("Top 10 Senders: (Update in progress)");

        // Fetch new data
        $.get("/top-ten", function(data) {
            // Handle the response if needed
            // Fetch data from the JSON file
            $.getJSON("/static/emails.json", function(data) {
                // Use the new data to populate the page
                populatePage(data);
            });
        });
    });
});

    
    
    
    
    