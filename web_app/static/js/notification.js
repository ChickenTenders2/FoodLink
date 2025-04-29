// function fetchNotifications() {
//     fetch('/get_notifications')
//         .then(response => response.json())
//         .then(data => {
//             const list = document.getElementById('notification-list');
//             const badge = document.getElementById('notification-badge');

//             // displyes notifcation in notifcation popup
//             list.innerHTML = '';
//             data.notifications.forEach(n => {
//                 const li = document.createElement('li');
//                 li.className = n.read ? 'read' : 'unread';
//                 li.setAttribute('data-id', n.id);
//                 li.setAttribute('data-severity', n.severity);
//                 li.onclick = function () { markRead(this); };

//                 li.innerHTML = `<strong>${n.severity.charAt(0).toUpperCase() + n.severity.slice(1)}</strong> : ${n.message}
//                                 <small>${n.timestamp}</small>`;
//                 list.appendChild(li);
//             });

//             // updates the notification badge with the correct number of unread alerts
//             if (data.unread_count > 0) {
//                 if (!badge) {
//                     const newBadge = document.createElement('span');
//                     newBadge.id = 'notification-badge';
//                     newBadge.className = 'notification-badge';
//                     newBadge.textContent = data.unread_count;
//                     document.querySelector('.nav-right').appendChild(newBadge);
//                 } else {
//                     badge.textContent = data.unread_count;
//                     badge.style.display = 'inline';
//                 }
//             } else {
//                 if (badge) badge.style.display = 'none';
//             }
//         });
// }

function fetchNotifications() {
    const list = document.getElementById('notification-list');
    const badge = document.getElementById('notification-badge');

    list.innerHTML = '<li class="loading">Loading notifications...</li>';

    fetch('/get_notifications')
        .then(response => {
            if (!response.ok) throw new Error("Network response was not ok");
            return response.json();
        })
        .then(data => {
            list.innerHTML = '';
            data.notifications.forEach(n => {
                const li = document.createElement('li');
                li.className = 'unread';
                li.setAttribute('data-id', n.id);
                li.setAttribute('data-severity', n.severity);
                li.onclick = function () { markRead(this); };

                li.innerHTML = `<strong>${n.severity.charAt(0).toUpperCase() + n.severity.slice(1)}</strong> : ${n.message}
                                <small>${n.timestamp}</small>`;
                list.appendChild(li);
            });

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
    setInterval(fetchNotifications, 30000);
});


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