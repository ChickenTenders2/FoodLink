function fetchNotifications() {
    fetch('/get_notifications')
        .then(response => response.json())
        .then(data => {
            const list = document.getElementById('notification-list');
            const badge = document.getElementById('notification-badge');

            list.innerHTML = '';
            data.notifications.forEach(n => {
                const li = document.createElement('li');
                li.className = n.read ? 'read' : 'unread';
                li.setAttribute('data-id', n.id);
                li.setAttribute('data-severity', n.severity);
                li.onclick = function () { markRead(this); };

                li.innerHTML = `<strong>${n.severity.charAt(0).toUpperCase() + n.severity.slice(1)}</strong> : ${n.message}
                                <small>${n.timestamp}</small>`;
                list.appendChild(li);
            });

            if (data.unread_count > 0) {
                if (!badge) {
                    const newBadge = document.createElement('span');
                    newBadge.id = 'notification-badge';
                    newBadge.className = 'notification-badge';
                    newBadge.textContent = data.unread_count;
                    document.querySelector('.nav-right').appendChild(newBadge);
                } else {
                    badge.textContent = data.unread_count;
                    badge.style.display = 'inline';
                }
            } else {
                if (badge) badge.style.display = 'none';
            }
        });
}

// document.addEventListener("DOMContentLoaded", function () {
//     const popup = document.getElementById('notification-popup');
//     const icon = document.getElementById('notification-icon');

//     // Toggle popup on icon click
//     icon.addEventListener('click', function (e) {
//         console.log("Clicked notification icon");
//         e.stopPropagation(); // Prevent window click from firing
//         // Toggle visibility
//         if (popup.style.display === 'block') {
//             popup.style.display = 'none';
//         } else {
//             popup.style.display = 'block';
//         }
//     });

//     // Prevent click inside the popup from closing it
//     popup.addEventListener('click', function (e) {
//         e.stopPropagation();
//     });

//     // Click anywhere else closes the popup
//     window.addEventListener('click', function () {
//         popup.style.display = 'none';
//     });

//     const tbFooter = document.querySelector('.tb-powered-by-footer');
//     if (tbFooter) tbFooter.style.display = 'none';

//     setInterval(fetchNotifications, 300000); // auto-refresh every 5 minutes
//     fetchNotifications(); // run once on page load
// });

document.addEventListener("DOMContentLoaded", function () { 
    const popup = document.getElementById('notification-popup'); 
    const icon = document.getElementById('notification-icon');

    if (!popup || !icon) {
        console.error('Notification popup or icon not found');
        return;
    }
    
    icon.addEventListener('click', function (e) {
        e.stopPropagation(); // Prevent body click from hiding it immediately
        popup.style.display = (popup.style.display === 'block') ? 'none' : 'block';
    });
    
    // Hide popup when clicking outside
    window.addEventListener('click', function () {
        popup.style.display = 'none';
    });
    
    popup.addEventListener('click', function (e) {
        e.stopPropagation();
    });

    const tbFooter = document.querySelector('.tb-powered-by-footer');
    if (tbFooter) tbFooter.style.display = 'none';
    
    fetchNotifications();
    setInterval(fetchNotifications, 300000);
});

// const tbFooter = document.querySelector('.tb-powered-by-footer');
// if (tbFooter) tbFooter.style.display = 'none';

// setInterval(fetchNotifications, 300000); // auto-refresh every 5 minutes
// fetchNotifications(); // run once on page load


function markRead(elem) {
    const notifId = elem.getAttribute('data-id');
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
            elem.classList.remove('unread');
            elem.classList.add('read');
            const badge = document.getElementById('notification-badge');
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