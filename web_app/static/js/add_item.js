/**
 * Opens the popup form and fills in the barcode number.
 * Also stops any background checks (e.g., scanner polling).
 * 
 * @param {string} barcode_number - The barcode to populate into the form.
 */
function open_popup(barcode_number) {
    stop_check();
    document.getElementById('barcode').value = barcode_number;
    document.getElementById('popup').style.display = 'block';
}

/**
 * Closes the popup form and clears all form fields.
 * Also restarts any background checks (e.g., scanner polling).
 */
function close_popup() {
    start_check();
    document.getElementById('popup').style.display = 'none';
    document.getElementById("name").value = null;
    document.getElementById("brand").value = null;
    document.getElementById("expiry_day").value = null;
    document.getElementById("expiry_month").value = null;
    document.getElementById("expiry_year").value = null;
    document.getElementById("default_quantity").value = null;
    document.getElementById("unit").value = null;
    document.getElementById("item_image").value = null;
}

/**
 * Triggers the popup form when a barcode is successfully scanned.
 * 
 * @param {string} barcode - The scanned barcode value.
 */
// Opens popup to add item information once barcode is scanned succesfully
function process_barcode(barcode) {
    open_popup(barcode);
}

/**
 * Submits the add item form using Fetch API (AJAX).
 * Validates expiry date before sending.
 * Displays alert messages based on the result.
 * 
 * @param {Event} event - The form submit event.
 */
// Adds item to item table
async function add_item(event) {
    // Prevent the form from submitting normally
    event.preventDefault(); 

    // Makes sure item expiry is more than one day
    if (!valid_expiry()) {
        alert("Expiry time must be at least one day.")
        return;
    }

    // Recreates form
    const form = event.target;
    const formData = new FormData(form);

    // Sends add command and waits for response
    const response = await fetch('/items/add_item/add', {
        method: 'POST',
        body: formData,
    });

    //Waits until result is recieved
    const result = await response.json();

    if (result.success) {
        alert("Item added succesfully.");
        close_popup();
    } else {
        alert('There was an error adding the item. Error: ' + result.error);
    }
}


/**
 * Validates that the entered expiry date is not all zeros (00/00/0000).
 * 
 * @returns {boolean} - True if expiry date is valid (not all zero), false otherwise.
 */
// Returns if expiry time is more than a day
function valid_expiry() {
    const day = parseInt(document.getElementById("expiry_day").value);
    const month = parseInt(document.getElementById("expiry_month").value);
    const year = parseInt(document.getElementById("expiry_year").value);
    return !(day == 0 && month == 0 && year == 0);
}