/**
 * Opens the item popup with pre-filled item details.
 * If the popup is triggered by a scanner, it stops the scanner.
 * 
 * @param {Array} item - Array containing item details.
 * @param {string} estimated_expiry - Estimated expiry date in YYYY-MM-DD.
 * @param {boolean} from_scanner - Whether the popup was triggered by a scanner.
 */
async function open_item_popup(item, estimated_expiry, from_scanner) {
    // If the popup was opened from the scanner
    if (from_scanner) {
        document.getElementById("close-popup").onclick = () => close_item_popup(true);
        stop_check();
    }
    // gets variables from item
    const [id, barcode, name, brand, expiry_time, default_quantity, unit, is_personal] = item;

    document.getElementById("item_id").value = id;
    document.getElementById("expiry_time").value = expiry_time;
    document.getElementById("item_image").src = await get_image_path(id);
    document.getElementById("item_image").alt = name;
    document.getElementById("barcode").value = barcode;
    document.getElementById("name").value = name;
    document.getElementById("brand").value = brand;
    document.getElementById("expiry_date").value = estimated_expiry;
    document.getElementById("quantity").value = default_quantity;
    // if item is singular, multiple should be allowed to stored together so no max quantity
    if (default_quantity > 1) {
        document.getElementById("quantity").max = default_quantity;
    }
    document.getElementById("unit").value = unit;
    document.getElementById('popup').style.display = 'block';

    if (is_personal) {
        const modify_action_button = document.getElementById("modify_action_button");
        modify_action_button.innerHTML = "Edit Item";
        modify_action_button.onclick = () => open_add_popup("edit");
    }
}

/**
 * Closes the item popup and resets relevant values.
 * Restarts scanner if triggered by scanner input.
 * 
 * @param {boolean} to_scanner - Whether to restart scanner on close.
 */
function close_item_popup(to_scanner) {
    // If the scanner will be in focus after closing
    if (to_scanner) {
        document.getElementById("close-popup").onclick = () => close_item_popup(false);
        start_check();
    }
    // only attribute that has the ability to not get overriden on next open
    document.getElementById("quantity").removeAttribute("max");
    const modify_action_button = document.getElementById("modify_action_button");
    modify_action_button.innerHTML = "Clone Item";
    modify_action_button.onclick = () => open_add_popup("clone");
    document.getElementById('popup').style.display = 'none';
}

/**
 * Opens the search popup for finding public or personal items.
 * Stops scanner before displaying the popup.
 */
function open_search_popup() {
    close_not_found_popup();
    stop_check();
    document.getElementById('search_popup').style.display = 'block';
}

/**
 * Closes the search popup and clears its contents.
 * Restarts the scanner afterward.
 */
function close_search_popup() {
    start_check();
    document.getElementById("search_term").value = "";
    document.getElementById("search_results").innerHTML = "";
    document.getElementById('search_popup').style.display = 'none';
}

/**
 * Opens the personal item search view inside the popup.
 * Temporarily hides the search form and loads personal items.
 */
async function open_personal_popup() {
    document.getElementById("search-popup-title").innerHTML = "Personal Items";
    document.getElementById("search-form").style.display = "none";
    document.getElementById("close_search_popup").onclick = () => close_personal();
    await display_personal();
    open_search_popup();
}

/**
 * Closes the personal items popup and restores public item search UI.
 */
function close_personal() {
    document.getElementById("close_search_popup").onclick = () => close_search_popup();
    document.getElementById("search-popup-title").innerHTML = "Search for item";
    document.getElementById("search-form").style.display = "block";
    close_search_popup();
}

/**
 * Called when an item is selected from search results.
 * Estimates expiry date and opens the item popup.
 * 
 * @param {Array} item - The selected item.
 * @param {boolean} from_scanner - Whether it was selected via barcode/object scan.
 */
function select_item(item, from_scanner) {
    expiry_time = item[4];
    const [days, months, years] = get_expiry_values(expiry_time);
    const estimated_expiry = estimate_expiry_date(days, months, years);
    open_item_popup(item, estimated_expiry, from_scanner)
}

/**
 * Opens the "Add Item" popup in various modes: clone, barcode, AI, search, or edit.
 * Populates specific fields depending on the mode.
 * 
 * @param {string} where_from - Mode of popup ('clone', 'barcode', 'ai', 'search', 'edit').
 * @param {string|null} object - Optional: barcode or item name.
 */
function open_add_popup(where_from, object = null) {
    if (where_from == "clone") {
        add_clone_info();
    } 
    else if (where_from == "barcode") {
        stop_check();
        document.getElementById('barcode_edit').value = object;
        // Barcode scanning should only start if the popup leads back to the main window
        document.getElementById("close-add-popup").onclick = () => close_add_popup(true);
    }
    else if (where_from == "ai") {
        stop_check();
        document.getElementById('name_edit').value = object;
        // Barcode scanning should only start if the popup leads back to the main window
        document.getElementById("close-add-popup").onclick = () => close_add_popup(true);
    }
    else if (where_from == "search") {
        const search_term = document.getElementById("search_term").value;
        document.getElementById("name_edit").value = search_term;
    }
    else if (where_from == "edit") {
        add_clone_info();
        document.getElementById("add-popup-title").innerHTML = "Edit Personal Item";
        document.getElementById("add-popup-submit").innerHTML = "Update Item";
        document.getElementById("add-form").onsubmit = (event) => add_update_item(event);
        document.getElementById("close-add-popup").onclick = () => close_add_popup(false, true);
        document.getElementById("delete_item").style.display = "block";
    }
    // Displays popup
    document.getElementById('add-popup').style.display = 'block';
}

/**
 * Populates the "Add Item" form with details cloned from the selected item.
 * Used when cloning or editing existing item.
 */
async function add_clone_info() {
    // Gets information from the item to clone
    const original_id = document.getElementById("item_id").value;
    const expiry_time = document.getElementById("expiry_time").value;
    const [days, months, years] = get_expiry_values(expiry_time);
    const name = document.getElementById("name").value;
    const barcode = document.getElementById("barcode").value;
    const brand = document.getElementById("brand").value;
    let default_quantity = document.getElementById("quantity").max;
    // incase of an item with no max quantity (i.e. loose item: banana, apple, etc)
    if (!default_quantity) {
        default_quantity = 1;
    }
    const unit = document.getElementById("unit").value;
    // Fills in input boxes with information
    document.getElementById("expiry_day").value = days;
    document.getElementById("expiry_month").value = months;
    document.getElementById("expiry_year").value = years;
    document.getElementById("image_preview").src = await get_image_path(original_id);
    document.getElementById("image_preview").alt = name;
    document.getElementById("original_item_id").value = original_id;
    document.getElementById("name_edit").value = name;
    document.getElementById("barcode_edit").value = barcode;
    document.getElementById("brand_edit").value = brand;
    document.getElementById("default_quantity").value = default_quantity;
    document.getElementById("unit_edit").value = unit;
}

/**
 * Closes the "Add Item" popup and resets all form fields.
 * Optionally restarts scanner and resets form based on edit mode.
 * 
 * @param {boolean} to_scanner - Whether to restart barcode scanning.
 * @param {boolean} edit_mode - Whether the form should be reset for add mode.
 */
async function close_add_popup(to_scanner, edit_mode = false) {
    if (to_scanner) {
        start_check();
        document.getElementById("close-add-popup").onclick = () => close_add_popup(false);
    }
    if (edit_mode) {
        document.getElementById("add-popup-title").innerHTML = "Add To Personal Items";
        document.getElementById("add-popup-submit").innerHTML = "Add Item";
        document.getElementById("add-form").onsubmit = (event) => add_new_item(event);
        document.getElementById("close-add-popup").onclick = () => close_add_popup(false);
        document.getElementById("delete_item").style.display = "none";
        // closes item popup so there are no discrepancies
        document.getElementById("close-popup").click();
        // if normal search popup open, refresh items
        if (document.getElementById("search-form").style.display != "none") {
            text_search_item();
        }
        // if personal items search popup is open, refresh items
        else if (document.getElementById("search_popup").style.display != "none") {
            display_personal();
        }
    }
    document.getElementById("expiry_day").value = null;
    document.getElementById("expiry_month").value = null;
    document.getElementById("expiry_year").value = null;
    document.getElementById("image_preview").src = "/static/images/null.jpg";
    document.getElementById("image_preview").alt = null;
    document.getElementById("original_item_id").value = null;
    document.getElementById("name_edit").value = null;
    document.getElementById("barcode_edit").value = null;
    document.getElementById("brand_edit").value = null;
    document.getElementById("default_quantity").value = null;
    document.getElementById("default_quantity").max = null;
    document.getElementById("unit_edit").value = null;
    document.getElementById("quantity2").max = null;
    document.getElementById("quantity2").value = null;
    document.getElementById("expiry_date2").value = null;
    document.getElementById("item_image_edit").value = null;
    document.getElementById("add_to_inventory").checked = false;
    toggle_inventory_fields();

    document.getElementById("add-popup").style.display = "none";
}

/**
 * Opens the "Item Not Found" popup and assigns an action to the confirm button.
 * 
 * @param {boolean} scan_mode - Whether the trigger was object recognition or barcode.
 * @param {string} object - The name or barcode value that was not found.
 */
function open_not_found_popup(scan_mode, object) {
    stop_check();
    document.getElementById("not_found_popup").style.display = "block";
    const button = document.getElementById("open_not_found_button")
    // runs functions when button is pressed
    button.onclick = () => {
        close_not_found_popup();
        // if object identified not in db replace name with name of identified item
        if (scan_mode) {
            open_add_popup("ai", object);
        // if barcode missing from db replace barcode
        } else {
            open_add_popup("barcode", object);
        }
    }
}

/**
 * Closes the "Item Not Found" popup and resets its confirm button behavior.
 */
function close_not_found_popup() {
    start_check();
    document.getElementById("not_found_popup").style.display = "none";
    document.getElementById("open_not_found_button").onclick = null;
}

/**
 * Opens the "Report Item" popup for users to request correction or public addition.
 * 
 * @param {string} original_item_id - The personal item being reported.
 * @param {string} item_id - The corrected public item to map to.
 */
function open_report_popup(original_item_id, item_id) { 
    if (original_item_id) {
        document.getElementById("report_message").innerHTML = "Send request to fix item error?";
    }
    document.getElementById("report_popup").style.display = "block";
    const button = document.getElementById("report_button");
    // runs functions when button is pressed
    button.onclick = () => {
        send_report(original_item_id, item_id);
        button.innerHTML = "Done";
        button.onclick = () => {
            close_report_popup(); 
        }
    }
}

/**
 * Closes the "Report Item" popup and resets its text and buttons.
 */
function close_report_popup() {
    document.getElementById("report_message").innerHTML = "Send request for missing item to be available for all?";
    document.getElementById("report_message_2").innerHTML = "If successful, your personal item will be replaced.";
    document.getElementById("report_button").innerHTML = "Send Report";
    document.getElementById("report_popup").style.display = "none";
    document.getElementById("report_button").onclick = null;
}

/**
 * Toggles inventory-specific form fields when the "Add to Inventory" checkbox is toggled.
 * Sets required fields and estimated expiry/quantity based on user input.
 */
function toggle_inventory_fields() {
    const checkbox = document.getElementById("add_to_inventory").checked;
    const expiry_input = document.getElementById("expiry_date2");
    const quantity_input = document.getElementById("quantity2");
    const inputs_container = document.getElementById("inventory_fields");

    // If the checkbox is unticked
    if (!checkbox) {
        expiry_input.required = false;
        quantity_input.required = false;
        inputs_container.style.display = "none";
        return;
    }

    // Makes sure values are entered
    expiry_input.required = true;
    quantity_input.required = true;

    // Calculates estimated expiry from new expiry time 
    const days = parseInt(document.getElementById("expiry_day").value) || 0;
    const months = parseInt(document.getElementById("expiry_month").value) || 0;
    const years = parseInt(document.getElementById("expiry_year").value) || 0;
    const estimated_expiry = estimate_expiry_date(days, months, years);
    
    expiry_input.value = estimated_expiry;
    
    // Automatically sets quantity to default and doesnt allow any bigger
    const default_quantity = parseInt(document.getElementById("default_quantity").value);
    quantity_input.value = default_quantity;
    // if item is singular, multiple should be allowed to stored together so no max quantity
    if (default_quantity > 1) {
        quantity_input.max = default_quantity;
    }
    
    // Displays extra inputs
    inputs_container.style.display = "block";
}

/**
 * Performs a text-based item search and displays matching results.
 * 
 * @param {Event} event - The form submission event (optional).
 */
async function text_search_item(event) {
    // Prevent the form from submitting normally
    if (event) {
        event.preventDefault(); 
    }

    const search_term = document.getElementById("search_term").value;

    // fetches and waits for result
    const response = await fetch('/items/text_search/' + search_term);

    //Waits until result is recieved
    const result = await response.json();
    if (result.success) {
        display_search_results(result.items)
    } else {
        alert('There was an error searching. Error: ' + result.error);
    }
}

/**
 * Fetches and displays the user's personal items.
 * Calls backend `/items/get_personal` and passes results to `display_search_results()`.
 */
async function display_personal() {

    const response = await fetch('/items/get_personal');

    //Waits until result is recieved
    const result = await response.json();
    if (result.success) {
        display_search_results(result.items)
    } else {
        alert('There was an error searching. Error: ' + result.error);
    }
}

/**
 * Renders a list of personal items in the UI.
 * Each item is clickable and triggers `select_item()`.

 * @param {Array} items - List of item arrays from the backend.
 */
async function display_search_results(items) {
    // gets div to put results in
    const container = document.getElementById("search_results");
    // Resets text incase no items were found previously
    container.innerHTML = "";
    // creates a container for each item
    for (let item of items) {
        const div = document.createElement("div");
        // gets variables from item
        const [id, , name, brand, , default_quantity, unit] = item;
        // adds the item information and image
        const image_path = await get_image_path(id);
        let brand_text = "";
        if (brand) {
            brand_text = `(${brand})`;
        }
        div.innerHTML = `
        <img src="${image_path}" alt="${name}" class="item_img">
        <div class="item_info">
            ${name} ${brand_text} - ${default_quantity} ${unit}
        </div>`;
        div.className = "search_result_item";
        // estimates expiry for the item and opens popup when item container is clicked on
        div.onclick = () => select_item(item);
        // adds container to search results container
        container.appendChild(div);
    }
}

/**
 * Routes scanned object/barcode to the correct function based on mode.
 * 
 * @param {string} object - Item name or barcode number.
 */
// Redirects to correct function once barcode is found
function process_barcode(object) {
    // Gets mode
    const checkbox = document.getElementById("scan_mode").checked;
    // If in AI object recognition mode
    if (checkbox) {
        single_search_item(object)
    } else {
        barcode_search_item(object);
    }
}

/**
 * Searches for an item using its name (used in object recognition mode).
 * If found, selects it; otherwise opens "not found" popup.
 * 
 * @param {string} item_name - Name of the item to search.
 */
async function single_search_item(item_name) {
    // Searches for an item by name and awaits result
    const response = await fetch('/items/single_text_search/'+item_name)               
    let result = await response.json();

    if (result.success) {
        if (result.item) {
            select_item(result.item, true);
        } else {
            open_not_found_popup(true, item_name);
        }
    } else {
        alert(result.error);
    }
}

/**
 * Searches for an item using its barcode number.
 * If found, selects it; otherwise opens "not found" popup.
 * 
 * @param {string} barcode_number - Barcode to search.
 */
// Checks if barcode is in item table
async function barcode_search_item(barcode_number) {
    // Searches for item by barcode and awaits result
    const result = await fetch('/items/barcode_search/'+barcode_number)               
    let response = await result.json();

    // If an item is found
    if (response.success) {
        if (response.item) {
            select_item(response.item, true);
        } else {
            open_not_found_popup(false, barcode_number);
        }
    } else {
        alert(response.error);
    }
}

/**
 * Submits the add item form to add an item to the user's inventory.
 * Uses AJAX and closes popup on success.
 * 
 * @param {Event} event - The form submission event.
 */
// Adds item to inventory
async function add_item(event) {
    // Prevent the form from submitting normally
    event.preventDefault(); 

    // Recreates form
    const form = event.target;
    const formData = new FormData(form);

    // Sends update command and waits for response
    const response = await fetch('/inventory/add_item/add', {
        method: 'POST',
        body: formData,
    });

    //Waits until result is recieved
    const result = await response.json();

    if (result.success) {
        alert("Item added succesfully.");
        // makes sure popup closes properly (restarts scanning if opened from scanner)
        document.getElementById("close-popup").click();
    } else {
        alert('There was an error adding the item. Error: ' + result.error);
    }
}

/**
 * Submits an update for an existing personal item and possibly updates inventory.
 * 
 * @param {Event} event - The form submission event.
 */
// Updates personal item and potentially adds to inventory
async function add_update_item(event) {
    // Prevent the form from submitting normally
    event.preventDefault(); 

    // Recreates form
    const form = event.target;
    const formData = new FormData(form);

    // Sends update command and waits for response
    const response = await fetch("/inventory/add_item/update", {
        method: 'POST',
        body: formData,
    });

    //Waits until result is recieved
    const result = await response.json();

    if (result.success) {
        alert(result.message);
        close_add_popup(false, true);
    } else {
        alert('There was an error updating the item. Error: ' + result.error);
    }
}

/**
 * Submits a new personal item and potentially adds it to the user's inventory.
 * Also opens the reporting popup to report a missing or incorrect item.
 * 
 * @param {Event} event - The form submission event.
 */
// Adds new personal item and potentially to inventory
async function add_new_item(event) {
    // Prevent the form from submitting normally
    event.preventDefault(); 

    // Recreates form
    const form = event.target;
    const formData = new FormData(form);

    // Sends update command and waits for response
    const response = await fetch('/inventory/add_item/new', {
        method: 'POST',
        body: formData,
    });

    //Waits until result is recieved
    const result = await response.json();

    if (result.success) {
        alert(result.message);
        const original_item_id = document.getElementById("original_item_id").value;
        
        open_report_popup(original_item_id, result.item_id);
        close_add_popup(false);

    } else {
        alert('There was an error adding the item. Error: ' + result.error);
    }
}

/**
 * Deletes a personal item from the database and the user's inventory after confirmation.
 */
// deletes item from table and inventory
async function delete_item() {
    if (!confirm("Are you sure you want to delete this item? It will also be removed from your inventory.")) {
        return;
    }
    const item_id = document.getElementById("original_item_id").value;

    const response = await fetch('/inventory/delete_item/'+item_id)               
    let result = await response.json();

    if (result.success) {
        alert(result.message);
        close_add_popup(false, true);
    } else {
        alert(result.error);
    }
}

/**
 * Sends a report to the backend that a personal item should be replaced or reviewed.
 * 
 * @param {string} original_item_id - The ID of the item being reported.
 * @param {string} item_id - The new item ID the user is reporting as a replacement or correction.
 */
async function send_report(original_item_id, item_id) {

    const formData = new FormData();
    formData.append("new_item_id", item_id);
    formData.append("item_id", original_item_id);

    // Sends update command and waits for response
    const response = await fetch('/items/reports/new', {
        method: 'POST',
        body: formData,
    });

    //Waits until result is recieved
    const result = await response.json();
    
    document.getElementById("report_message").innerHTML = result.success ? "Item successfully reported." : 
                            "Error reporting item: " + result.error + ". Please try again later.";
    document.getElementById("report_message_2").innerHTML = "";
}

/**
 * Estimates an expiry date by adding the specified days, months, and years to today's date.
 * 
 * @param {number} days - Days to add.
 * @param {number} months - Months to add.
 * @param {number} years - Years to add.
 * 
 * @returns {string} - Estimated expiry date in 'YYYY-MM-DD' format.
 */
// Calculate an estimate of the expiry date
function estimate_expiry_date(days, months, years) {
    // Todays date
    const today = new Date();
    // Calucates the expiry from todays date
    const estimated_expiry = new Date(
        today.getFullYear() + years,
        today.getMonth() + months,
        today.getDate() + days
    );
    // Formats to YYYY-MM-DD
    return estimated_expiry.toISOString().split('T')[0];
}

