// Using local storage so that the index value persists on page refresh.
let index = localStorage.getItem('pageIndex') || 0;

async function remove_item(id) {
    if (!confirm("Are you sure you want to delete this item?")) {
        return;
    }

    // Fetches the flask route for deleting an item from the database.
    const response = await fetch('/admin/item_view/delete', {
        method: 'POST',
        body: id,
    })
    
    //Waits until the result is recieved.
    const result = await response.json();
    
    if (result.success) {
        // Reloads the page.
        location.reload();
    } else {
        alert('There was an error deleting the item.');
    }
}

// Opens the item information popup.
async function open_popup(itemName, barcode, name, brand, quantity, expiry_date, unit, item_id, add=false) {
    // Sets values in popup to those of the item.

    // Add is a boolean check to see if items are updated or added to the database.
    if (add == true) {
        document.getElementById('popup-title').innerText = `Add ${itemName}`;
        document.getElementById('barcode-label').hidden = false;
        document.getElementById('barcode').type = "number";
        //image handling
        document.getElementById("image_preview").src = "/static/images/null.jpg";
        document.getElementById("image_preview").alt = null;

        // Adds the functionality to submit the form and move to the next state.
        document.getElementById('update-form').addEventListener('submit', submit_add);
    } else {
        document.getElementById('popup-title').innerText = `Edit ${itemName}`;
        document.getElementById('barcode-label').hidden = true;
        document.getElementById('barcode').type = "hidden";
        //image handling
        document.getElementById("image_preview").src = await get_image_path(item_id);
        document.getElementById("image_preview").alt = name;

        document.getElementById('update-form').addEventListener('submit', submit_update);

        // moved delete button inside popup
        const deleteBtn = document.getElementById('delete_button');
        deleteBtn.style.display = 'inline-block';
        deleteBtn.onclick = () => remove_item(item_id);
    }
    document.getElementById('name').value = name;
    document.getElementById('barcode').value = barcode;
    document.getElementById('brand').value = brand;
    document.getElementById('quantity').value = quantity;
    document.getElementById('expiry').value = expiry_date;
    document.getElementById('unit').value = unit;
    document.getElementById('item_id').value = item_id;
    document.getElementById('original-expiry').value = expiry_date;
    document.getElementById('original-quantity').value = quantity;
    document.getElementById('original-brand').value = brand;
    document.getElementById('original-name').value = name;
    document.getElementById('original-unit').value = unit;
    document.getElementById('popup').style.display = 'block';

}

// Closes item information popup
function close_popup() {
    document.getElementById('popup').style.display = 'none';
    document.getElementById('delete_button').style.display = "none";
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
    
    // Gets new values
    const item_image = document.getElementById("item_image").value;
    const newQuantity = document.getElementById('quantity').value;
    const newExpiry = document.getElementById('expiry').value;
    const newUnit = document.getElementById('unit').value;
    const newBrand = document.getElementById('brand').value;
    const newName = document.getElementById('name').value;

    // Checks if values have not been edited
    if (newQuantity == originalQuantity && newExpiry == originalExpiry 
        && newUnit == originalUnit && newBrand == originalBrand
        && newName == originalName && !item_image) {
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
    // Prevents the form from submitting normally.
    event.preventDefault(); 

    // Recreates the form.
    const form = event.target;
    const formData = new FormData(form);
 
    // Fetches the flask route for adding an item to the database.
    const response = await fetch('/admin/item_view/add_item', {
         method: 'POST',
         body: formData,
     });
 
    // Waits until the result is recieved.
    const result = await response.json();
 
    if (result.success) {
         // Updates the page.
         location.reload();
    } else {
         alert('There was an error updating the item.');
    }
}

// fetches inventory after search term is applied
document.getElementById('filter-form').addEventListener('submit', function (e) {
    e.preventDefault();
    search()
});

async function search() {
    // Uses defaults value if undefined or null.
    if (document.getElementById('search-input').value != ''){
        const searchParam = document.getElementById('search-input').value;
        index = 0
        localStorage.setItem('pageIndex', index)
        history.pushState(null, null, "/admin/item_view/get/" + searchParam);
        fetch("/admin/item_view/get/" + searchParam);
        location.reload();
    }
    else {
        index = 0
        localStorage.setItem('pageIndex', index)
        history.pushState(null, null, "/admin/item_view");
        //fetch("/admin/item_view/");
        location.reload();
    }
}


async function next(event, max) {
    event.preventDefault()
    if (index < max) {
        index++;
        localStorage.setItem('pageIndex', index);
        history.pushState(null, null, "/admin/item_view/get/" + index);
        fetch("/admin/item_view/get/" + index);
        location.reload();
    }
    else {
        document.getElementById('button-next').style.cursor = "not-allowed";
        document.getElementById('button-next').style.color = "grey";
    }
}

async function previous(event) {
    event.preventDefault()
    if (index > 0) {
        index--;
        localStorage.setItem('pageIndex', index);
        history.pushState(null, null, "/admin/item_view/get/" + index);
        fetch("/admin/item_view/get/" + index);
        location.reload();
    }
    else {
        document.getElementById('button-prev').style.cursor = "not-allowed";
        document.getElementById('button-prev').style.color = "grey";
    }
}
