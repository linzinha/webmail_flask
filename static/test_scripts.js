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


// Function to update sender and subject lists
function updateSenderAndSubjectLists() {
    // Update the header to indicate that the update is in progress
    var dataContainer = $("#data-container");
    dataContainer.find("h2").text("Top 10 Senders: (Update in progress)");

    // Fetch updated data from the server using AJAX
    $.get("/refresh-data", function(updatedData) {
        // Append the updated data to the existing content
        var newContent = $(updatedData);

        // Find the existing list of senders and subjects
        var senderList = dataContainer.find("#sender-list");
        var subjectList = dataContainer.find("#subject-list");

        // Replace the content of sender and subject lists with the new data
        senderList.html(newContent.find("#sender-list").html());
        subjectList.html(newContent.find("#subject-list").html());
    });
}

// function loadSenderAndSubjectLists() {
//     $.get("/load-data", function(staleData) {

//     }
// }

$(document).ready(function() {
    // Function to handle button click
    $("#show-data").click(function() {
        // Call the function to update sender and subject lists
        loadSenderAndSubjectLists();
    });
    $("#refresh-data").click(function() {
        // Call the function to update sender and subject lists
        updateSenderAndSubjectLists();
    });
});


    
    
    
    
    