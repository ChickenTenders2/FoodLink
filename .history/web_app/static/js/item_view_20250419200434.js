async function remove_item(id, event) {
    
    event.stopPropagation();

    // Sends update command and waits for response
    const response = await fetch('/admin/item_view/delete', {
        method: 'POST',
        body: id,
    })
    
    //Waits until result is recieved
    const result = await response.json();
    
    if (result.success) {
        // Updates page
        location.reload();
    } else {
        alert('There was an error deleting the item.');
    }
}

// Opens item information popup
function open_popup(itemName, barcode, name, brand, quantity, expiry_date, unit, inventory_id, user_id, add=false) {
    // Sets values in popup to those of the item
    if (add == true) {
        document.getElementById('popup-title').innerText = `Add a New Item`;
        document.getElementById('barcode-label').hidden = false;
        document.getElementById('barcode').type = "text";
        document.getElementById('update-form').addEventListener('submit', submit_add);
    } else{
        document.getElementById('popup-title').innerText = `Edit ${itemName}`;
        document.getElementById('barcode-label').hidden = true;
        document.getElementById('barcode').type = "hidden";
        document.getElementById('update-form').addEventListener('submit', submit_update);
    }
    document.getElementById('name').value = name;
    document.getElementById('barcode').value = barcode;
    document.getElementById('brand').value = brand;
    document.getElementById('quantity').value = quantity;
    document.getElementById('expiry').value = expiry_date;
    document.getElementById('unit').value = unit;
    document.getElementById('user-id').value = user_id;
    document.getElementById('inventory-id').value = inventory_id;
    document.getElementById('original-expiry').value = expiry_date;
    document.getElementById('original-quantity').value = quantity;
    document.getElementById('original-brand').value = brand;
    document.getElementById('original-name').value = name;
    document.getElementById('original-unit').value = unit;
    document.getElementById('original-user-id').value = user_id;
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
    const originalUnit = document.getElementById('original-unit').value;
    const originalBrand = document.getElementById('original-brand').value;
    const originalName = document.getElementById('original-name').value;
    const originalID = document.getElementById('original-user-id').value;
    
    // Gets new values
    const newQuantity = document.getElementById('quantity').value;
    const newExpiry = document.getElementById('expiry').value;
    const newUnit = document.getElementById('unit').value;
    const newBrand = document.getElementById('brand').value;
    const newName = document.getElementById('name').value;
    const newID = document.getElementById('user-id').value;

    // Checks if values have not been edited
    if (newQuantity == originalQuantity && newExpiry == originalExpiry 
        && newUnit == originalUnit && newBrand == originalBrand
        && newName == originalName && originalID == newID) {
        // Prevent sending the update request
        close_popup();
        return;  
    }

    // Recreates form
    const form = event.target;
    const formData = new FormData(form);

    // Sends update command and waits for response
    const response = await fetch('/admin/item_view/update_item', {
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

async function submit_add(event) {
    // Prevent the form from submitting normally
    event.preventDefault(); 

    // Recreates form
    const form = event.target;
    const formData = new FormData(form);
 
    // Sends update command and waits for response
    const response = await fetch('/admin/item_view/add_item', {
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
