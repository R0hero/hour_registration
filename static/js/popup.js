// static/js/popup.js

document.addEventListener("DOMContentLoaded", function() {
    var popup = document.getElementById('popup');
    var span = document.getElementsByClassName("close")[0];

    document.querySelectorAll('td a').forEach(function(element) {
        element.addEventListener('click', function(event) {
            event.preventDefault();
            var date = event.target.dataset.date;var dateInput = document.querySelector('input[name="date"]');
            dateInput.value = date; // Set the value of the hidden input

            // Send AJAX request to get timecards for the selected date
            fetch(getTimecardsUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),  // Use the CSRF token
                },
                body: JSON.stringify({ date: date })
            })
            .then(response => response.json())
            .then(data => {
                var selectedDateSpan = document.getElementById('selected-date');
                selectedDateSpan.textContent = date; // Update the date display

                var timecardsContainer = document.getElementById('timecards-container');
                var editUrlBase = timecardsContainer.getAttribute('data-edit-url-base');
                timecardsContainer.innerHTML = ''; // Clear previous timecards
                data.timecards.forEach(timecard => {
                    var p = document.createElement('p');
                    var editUrl = editUrlBase.replace('0', timecard.id);
                    p.innerHTML = '<a class="no-underline-link" href="' + editUrl + '">(' + timecard.project_number + ')</a> ' + timecard.project_name + '<br>' + timecard.start_time + ' to ' + timecard.end_time;
                    timecardsContainer.appendChild(p);
                });

                popup.style.display = "block";
            });
        });
    });

    span.onclick = function() {
        popup.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == popup) {
            popup.style.display = "none";
        }
    }
});

// CSRF token helper function
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
