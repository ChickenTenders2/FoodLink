// Function to fetch notifications from the server and update the UI
function fetchNotifications() {
    const list = document.getElementById('notification-list');
    const badge = document.getElementById('notification-badge');
    
    // Show a loading message while fetching
    list.innerHTML = '<li class="loading">Loading notifications...</li>';

    // Fetch notifications from the server
    fetch('/get_notifications')
        .then(response => {
            if (!response.ok) throw new Error("Network response was not ok");
            return response.json();
        })
        .then(data => {
            // Clear previous notifications
            list.innerHTML = '';
            // Clear previous notifications
            data.notifications.forEach(n => {
                const li = document.createElement('li');
                li.className = n.read ? 'read' : 'unread';
                li.setAttribute('data-id', n.id);
                li.setAttribute('data-severity', n.severity);
                li.onclick = function () { markRead(this); };
                
                // Set inner content of the list item
                li.innerHTML = `<strong>${n.severity.charAt(0).toUpperCase() + n.severity.slice(1)}</strong> : ${n.message}
                                <small>${n.timestamp}</small>`;

                //Hide read notification
                if (n.read) li.style.display = 'none';

                list.appendChild(li);
            });

            // Update the notification badge with unread count
            if (data.unread_count > 0) {
                badge.textContent = data.unread_count;
                badge.style.display = 'inline';
            } else {
                badge.style.display = 'none';
            }
        })
        .catch(error => {
            console.error("Failed to fetch notifications:", error);
            list.innerHTML = '<li class="error">Failed to load notifications</li>';
        });
}


// Event listener when the DOM is fully loaded
document.addEventListener("DOMContentLoaded", function () { 
    const popup = document.getElementById('notification-popup'); 
    const icon = document.getElementById('notification-icon');

    // Check that popup and icon exist
    if (!popup || !icon) {
        console.error('Notification popup or icon not found');
        return;
    }
    // Toggle the popup visibility when the icon is clicked
    icon.addEventListener('click', function (e) {
        e.stopPropagation();  // Prevent the click from propagating to the window
        popup.style.display = (popup.style.display === 'block') ? 'none' : 'block';
    });
    
    // Hide popup when clicking outside
    window.addEventListener('click', function () {
        popup.style.display = 'none';
    });
    
    // Prevent hiding the popup when clicking inside it
    popup.addEventListener('click', function (e) {
        e.stopPropagation();
    });

    // Hide ThingsBoard branding footer if present
    const tbFooter = document.querySelector('.tb-powered-by-footer');
    if (tbFooter) tbFooter.style.display = 'none';
    
    // Load notifications immediately
    fetchNotifications();
    // Refresh notifications every 30 seconds
    setInterval(fetchNotifications, 30000);
});

// Function to mark a notification as read
function markRead(elem) {
    const notifId = elem.getAttribute('data-id');
    // Send request to mark the notification as read
    fetch('/notification/mark_read', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ notif_id: notifId })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            // change style based on unread/read notifications
            elem.classList.remove('unread');
            elem.classList.add('read');
            const badge = document.getElementById('notification-badge');
            // update badge count
            if (badge) {
                let count = parseInt(badge.textContent);
                if (count > 1) {
                    badge.textContent = count - 1;
                } else {
                    badge.style.display = 'none';
                }
            }
        } else {
            alert(data.error);
        }
    });
}