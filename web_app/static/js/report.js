/**
 * Fills form fields with item data (used for new or original item).
 * Supports both the new and original item form layouts by prefixing field IDs.
 * 
 * @param {number|string} id - Item ID.
 * @param {string} barcode - Barcode of the item.
 * @param {string} name - Item name.
 * @param {string} brand - Item brand.
 * @param {number} days - Expiry day.
 * @param {number} months - Expiry month.
 * @param {number} years - Expiry year.
 * @param {number} default_quantity - Default quantity for item.
 * @param {string} unit - Unit of measurement (e.g., grams, pieces).
 * @param {boolean} original - Whether this is the original item being filled (adds ID prefix).
 */
async function fill_item(id, barcode, name, brand, days, months, years, default_quantity, unit, original=false) {
    let id_text = "";
    if (original) {
        id_text = "original_";
    }
    document.getElementById(id_text + "expiry_day").value = days;
    document.getElementById(id_text + "expiry_month").value = months;
    document.getElementById(id_text + "expiry_year").value = years;
    document.getElementById(id_text + "image_preview").src = await get_image_path(id);
    document.getElementById(id_text + "image_preview").alt = name;
    document.getElementById(id_text + "name").value = name;
    document.getElementById(id_text + "barcode").value = barcode;
    document.getElementById(id_text + "brand").value = brand;
    document.getElementById(id_text + "default_quantity").value = default_quantity;
    document.getElementById(id_text + "unit").value = unit;
}

/**
 * Fetches item data by ID from the server and fills the form using `fill_item`.
 * 
 * @param {string|number} id - The item ID.
 * @param {boolean} original - Whether this is the original item (used for comparison).
 */
async function get_item(id, original = false) {
    // Searches for item by barcode and awaits result
    const response = await fetch('/items/get_item/'+ id);               
    let result = await response.json();

    // If an item is found
    if (result.success) {
        const [id, barcode, name, brand, expiry_time, default_quantity, unit] = result.item;
        const [days, months, years] = get_expiry_values(expiry_time);
        fill_item(id, barcode, name, brand, days, months, years, default_quantity, unit, original);
    } else {
        alert(result.error)
    }
}

/**
 * Updates the UI for missing item reports by hiding the original item section
 * and updating the heading for the new item.
 */
function set_missing_report() {
    document.getElementById("original_item").style.display = "none";
    document.getElementById("new_item_heading").innerHTML = "Missing Item Information";
}

/**
 * Sets the selected admin action (approve/deny) into a hidden input field.
 * 
 * @param {string} action - The selected action value (e.g., "approve", "deny").
 */
function set_action(action) {
    document.getElementById("report_action").value = action;
}

/**
 * Page load event handler to fetch and display both new and original item data.
 * Detects if the report is for a missing item or correction.
 */
window.onload = async function() {
    // Get the new item ID from the form/input
    const new_item_id = document.getElementById("new_item_id").value;
    // Fetch and display the new item data
    await get_item(new_item_id);
    // Get the original item ID if it exists (for comparison)
    const original_item_id = document.getElementById("original_item_id").value;
    if (original_item_id) {
        // If there's an original item, fetch and display it as well (true = isOriginal)
        await get_item(original_item_id, true);
    } else {
        // If not, configure the page to show it's a missing item report
        set_missing_report();
    }
}

/**
 * Submits the resolution of a report (approve or deny) to the server.
 * 
 * @param {Event} event - The form submission event.
 */
async function resolve_report(event) {
    // Prevent the form from submitting normally
    event.preventDefault(); 

    // Recreates form
    const form = event.target;
    const formData = new FormData(form);

    // Sends update command and waits for response
    const response = await fetch('/items/reports/resolve', {
        method: 'POST',
        body: formData,
    });

    //Waits until result is recieved
    const result = await response.json();
    if (result.success) {
        alert("report resolved.")
        window.location.href = "/items/reports"
    } else {
        alert('There was an error resolving the report. Error: ' + result.error);
    }
}

