// Opens item information popup
function open_popup(itemName, quantity, default_quantity, expiry_date, inventory_id) {
    // Sets values in popup to those of the item
    document.getElementById('popup-title').innerText = `Edit ${itemName}`;
    document.getElementById('quantity').value = quantity;
    document.getElementById('original-quantity').value = quantity;
    // if item is singular, multiple should be allowed to stored together so no max quantity
    if (default_quantity > 1) {
        document.getElementById("quantity").max = default_quantity;
    }
    document.getElementById('expiry').value = expiry_date;
    document.getElementById('original-expiry').value = expiry_date;
    document.getElementById('inventory-id').value = inventory_id;
    document.getElementById('popup').style.display = 'block';
}

// Closes item information popup
function close_popup() {
    document.getElementById('popup').style.display = 'none';
}

// Updates item in inventory
async function submit_update(event) {
    // Prevent the form from submitting normally
    event.preventDefault(); 

    // Gets original values
    const originalQuantity = document.getElementById('original-quantity').value;
    const originalExpiry = document.getElementById('original-expiry').value;
    const inventoryId = document.getElementById('inventory-id').value;

    // Gets new values
    const newQuantity = document.getElementById('quantity').value;
    const newExpiry = document.getElementById('expiry').value;

    // Checks if values have not been edited
    if (newQuantity == originalQuantity && newExpiry == originalExpiry) {
        // Prevent sending the update request
        close_popup();
        return;  
    }

    // Recreates form
    const form = event.target;
    const formData = new FormData(form);

    // Sends update command and waits for response
    const response = await fetch('/inventory/update_item', {
        method: 'POST',
        body: formData,
    });

    //Waits until result is recieved
    const result = await response.json();

    if (result.success) {
        const item = result.item;
        const tile = document.querySelector(`.inventory-tile[data-id="${item[0]}"]`);
        tile.querySelector('.item-name').textContent = item[2];
        tile.querySelector('img').src = `/static/images/${item[1]}.jpg`;
        close_popup();
        showToast('Item updated successfully');

    } else {
        alert('There was an error updating the item.');
    }    
}

window.addEventListener('DOMContentLoaded', () => {
    const tiles = document.querySelectorAll('.inventory-tile');

    tiles.forEach(tile => {
      const daysLeft = parseInt(tile.getAttribute('data-days-left'));
      tile.classList.remove('expires-2-days', 'expires-1-day', 'expires-today', 'expired');

      if (daysLeft < 0) tile.classList.add('expired');
      else if (daysLeft === 0) tile.classList.add('expires-today');
      else if (daysLeft === 1) tile.classList.add('expires-1-day');
      else if (daysLeft === 2) tile.classList.add('expires-2-days');
    });
  });

  document.getElementById('filter-form').addEventListener('submit', function (e) {
    e.preventDefault();
    const search = document.getElementById('search-input').value;
    const sort = document.getElementById('sort-select').value;
    fetchInventory(search, sort);
  });
  
  function fetchInventory(search, sort) {
    // Use empty string or default value if undefined or null
    const searchParam = search || '';
    const sortParam = sort || 'relevance';
  
    const url = `/api/inventory?search=${encodeURIComponent(searchParam)}&sort_by=${encodeURIComponent(sortParam)}`;
    
    fetch(url)
      .then(res => res.json())
      .then(data => {
        const container = document.querySelector('.inventory-container');
        container.innerHTML = '';
  
        data.items.forEach(item => {
          const tile = document.createElement('div');
          tile.className = 'inventory-tile';
          tile.setAttribute('data-id', item[0]);
          tile.setAttribute('data-days-left', item[8]);
  
          if (item[8] < 0) tile.classList.add('expired');
          else if (item[8] === 0) tile.classList.add('expires-today');
          else if (item[8] === 1) tile.classList.add('expires-1-day');
          else if (item[8] === 2) tile.classList.add('expires-2-days');
  
          tile.innerHTML = `
            <img src="/static/images/${item[1]}.jpg" alt="${item[2]}" onerror="this.onerror=null; this.src='/static/images/null.jpg';">
            <span class="item-name">${item[2]}</span>
          `;

  
          tile.onclick = () => {
            open_popup(item[2], item[4], item[7], item[6], item[0]);
          };
  
          container.appendChild(tile);
        });
      });
  }
  
  

// function refreshInventory() {
//     fetch('/api/inventory')
//       .then(response => response.json())
//       .then(data => {
//         data.items.forEach(item => {
//           const tile = document.querySelector(`.inventory-tile[data-id="${item[0]}"]`);
//           if (tile) {
//             // Update image and name
//             tile.querySelector('.item-name').textContent = item[2];
//             tile.querySelector('img').src = `/static/images/${item[1]}.jpg`;
  
//             // Update expiration class
//             const daysLeft = item[8];
  
//             tile.classList.remove('expired', 'expires-today', 'expires-1-day', 'expires-2-days');
  
//             if (daysLeft < 0) {
//               tile.classList.add('expired');
//             } else if (daysLeft === 0) {
//               tile.classList.add('expires-today');
//             } else if (daysLeft === 1) {
//               tile.classList.add('expires-1-day');
//             } else if (daysLeft === 2) {
//               tile.classList.add('expires-2-days');
//             } 
//           }
//         });
//       });
//   }
  
  // Refresh every 30 seconds
  setInterval(fetchInventory, 30000); // or adjust to your desired interval

async function removeItem() {
    const inventoryId = document.getElementById('inventory-id').value;
    const formData = new FormData();
    formData.append('inventory_id', inventoryId);

    const response = await fetch('/remove_item', {
        method: 'POST',
        body: formData
    });

    const result = await response.json();
    if (result.success){
        const tile = document.querySelector(`.inventory-tile[data-id="${inventoryId}"]`);
    if (tile) tile.remove(); 
    close_popup(); 
    showToast('Item deleted successfully');
    } else { 
        alert('Delete failed: ' + data.error);
    }
}


function showToast(message) {
    const toast = document.getElementById("toast");
    toast.innerText = message;
    toast.className = "toast show";
    setTimeout(() => { toast.className = toast.className.replace("show", ""); }, 3000);
  }
