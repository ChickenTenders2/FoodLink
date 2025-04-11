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
        // Updates page
        location.reload();
    } else {
        alert('There was an error updating the item.');
    }
}