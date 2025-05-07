/**
 * Opens the item edit popup with pre-filled values.
 * 
 * @param {string} itemName - Name of the item.
 * @param {number} quantity - Current quantity in inventory.
 * @param {number} default_quantity - Max allowable quantity.
 * @param {string} expiry_date - Expiry date in YYYY-MM-DD format.
 * @param {number} inventory_id - ID of the inventory record.
 */
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


/**
 * Closes the item popup without making changes.
 */
function close_popup() {
    document.getElementById('popup').style.display = 'none';
}


/**
 * Submits updated quantity or expiry for an inventory item.
 * Only submits if actual changes were made.
 * 
 * @param {Event} event - Form submission event.
 */
async function submit_update(event) {
    // Prevent the form from submitting normally
    event.preventDefault(); 

    // Gets original values
    const originalQuantity = document.getElementById('original-quantity').value;
    const originalExpiry = document.getElementById('original-expiry').value;

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
        // refetches items incase expiry was changed altering sort order
        fetchInventory();
        close_popup();
        showToast('Item updated successfully');

    } else {
        alert('There was an error updating the item.');
    }    
}

/**
 * Loads inventory when the page is first loaded.
 */
window.addEventListener('DOMContentLoaded', () => {
  fetchInventory();
});

/**
 * Reloads inventory if the page was restored from cache.
 */
window.addEventListener('pageshow', (event) => {
  // if page was loaded from cache instead of properly reloaded
  if (event.persisted) {
    // refresh inventory
    fetchInventory();
  }
});

/**
 * Re-fetches inventory when the filter form is submitted.
 */
document.getElementById('filter-form').addEventListener('submit', function (e) {
  e.preventDefault();
  fetchInventory();
});

/**
 * Fetches inventory items from the server and displays them as tiles.
 */
async function fetchInventory() {
    // Use empty string or default value if undefined or null
    const searchParam = document.getElementById('search-input').value || '';
    const sortParam = document.getElementById('sort-select').value || 'relevance';
  
    const response = await fetch("/inventory/get/"+searchParam);
    const result = await response.json();
    if (result.success) {
      const container = document.querySelector('.inventory-container');
      container.innerHTML = ''; // Clear current tiles
      let items = result.items;
      sort_items(items, sortParam); // Sort items client-side

      // Render each item as a tile
      for (let item of items) {
        let tile = document.createElement('div');
        await fill_tile(tile, item);
        container.appendChild(tile);
      }
    } else {
      alert(result.error);
    }
  }

/**
 * Builds an inventory tile element from item data.
 * 
 * @param {HTMLElement} tile - The tile DOM element to populate.
 * @param {Array} item - Array of item data.
 */
async function fill_tile(tile, item) {
  // extracts item attributes
  const [inv_id, item_id, name, , quantity, , expiry_date, default_quantity, ] = item;
  tile.className = 'inventory-tile';
  // sets attribute so query selector can find item to deleted upon removal
  tile.setAttribute('data-id', inv_id);
  days_left = calculate_days_Left(expiry_date);

  // links to css styling to highlight soon to be expired items
  if (days_left < 0) tile.classList.add('expired');
  else if (days_left === 0) tile.classList.add('expires-today');
  else if (days_left === 1) tile.classList.add('expires-1-day');
  else if (days_left === 2) tile.classList.add('expires-2-days');

  image_path = await get_image_path(item_id);

  tile.innerHTML = `
    <img src="${image_path}">
    <span class="item-name">${name}</span>
  `;

  tile.onclick = () => {
    open_popup(name, quantity, default_quantity, expiry_date, inv_id);
  };

  return tile;
}

/**
 * Calculates the number of days remaining until expiry.
 * 
 * @param {string} expiry_date - Expiry date in YYYY-MM-DD format.
 * @returns {number} - Days left (can be negative).
 */
function calculate_days_Left(expiry_date) {
  const today = new Date();
  const expiry = new Date(expiry_date);

  // remove time to match the expiry date
  today.setHours(0, 0, 0, 0);

  //the milliseconds in a day
  const day_ms = 86400000; // 1000 * 60 * 60 * 24
  //calculates the difference in dates in ms and then converts to days
  return Math.round((expiry - today) / day_ms);
}

/**
 * Sorts inventory items client-side based on selected method.
 * 
 * @param {Array} items - Array of item arrays.
 * @param {string} sort - Sort criteria ('name' or 'expiry').
 */
function sort_items(items, sort) {
  // sort by name a>z
  if (sort == "name") {
    items.sort((a,b) => {
      item_name = (item) => item[2];
      // compares string item_name
      return item_name(a).localeCompare(item_name(b));
    });
  // sort by expiry soonest to least soon to expire
  } else if (sort == "expiry") {
    items.sort((a,b) => {
      // converts string expiry_date to date
      expiry_date = (item) => new Date(item[6]);
      // compares lowest to highest
      return expiry_date(a) - expiry_date(b);
    })
  }
}

/**
 * Sends a request to delete an item from the inventory.
 * Removes the tile from the DOM on success.
 */
async function removeItem() {
    const inventoryId = document.getElementById('inventory-id').value;
    const formData = new FormData();
    formData.append('inventory_id', inventoryId);

    const response = await fetch('/inventory/remove_item', {
        method: 'POST',
        body: formData
    });

    const result = await response.json();
    if (result.success){
      // only needs to delete tile as sort arrangement will not change
      const tile = document.querySelector(`.inventory-tile[data-id="${inventoryId}"]`);
      if (tile) tile.remove(); 
      close_popup(); 
      showToast('Item deleted successfully');
    } else { 
      alert('Delete failed: ' + data.error);
    }
}

/**
 * Displays a short toast message for feedback.
 * 
 * @param {string} message - The message to display.
 */
function showToast(message) {
    const toast = document.getElementById("toast");
    toast.innerText = message;
    toast.className = "toast show";
    setTimeout(() => { toast.className = toast.className.replace("show", ""); }, 3000);
}
