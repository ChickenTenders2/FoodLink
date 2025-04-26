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

function close_item_popup(to_scanner) {
    // If the scanner will be in focus after closing
    if (to_scanner) {
        document.getElementById("close-popup").onclick = () => close_item_popup(false);
        start_check();
    }
    const modify_action_button = document.getElementById("modify_action_button");
    modify_action_button.innerHTML = "Clone Item";
    modify_action_button.onclick = () => open_add_popup("clone");
    document.getElementById('popup').style.display = 'none';
}

function open_search_popup() {
    close_not_found_popup();
    stop_check();
    document.getElementById('search_popup').style.display = 'block';
}

function close_search_popup() {
    start_check();
    document.getElementById("search_term").value = "";
    document.getElementById("search_results").innerHTML = "";
    document.getElementById('search_popup').style.display = 'none';
}

function open_personal_popup() {
    document.getElementById("search-popup-title").innerHTML = "Personal Items";
    document.getElementById("search-form").style.display = "none";
    document.getElementById("close_search_popup").onclick = () => close_personal();
    display_personal();
    open_search_popup();
}

function close_personal() {
    document.getElementById("close_search_popup").onclick = () => close_search_popup();
    document.getElementById("search-popup-title").innerHTML = "Search for item";
    document.getElementById("search-form").style.display = "block";
    close_search_popup();
}

function select_item(item, from_scanner) {
    expiry_time = item[4];
    const [days, months, years] = get_expiry_values(expiry_time);
    const estimated_expiry = estimate_expiry_date(days, months, years);
    open_item_popup(item, estimated_expiry, from_scanner)
}

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

async function add_clone_info() {
    // Gets information from the item to clone
    const original_id = document.getElementById("item_id").value;
    const expiry_time = document.getElementById("expiry_time").value;
    const [days, months, years] = get_expiry_values(expiry_time);
    const name = document.getElementById("name").value;
    const barcode = document.getElementById("barcode").value;
    const brand = document.getElementById("brand").value;
    const default_quantity = document.getElementById("quantity").max;
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

function close_add_popup(to_scanner, edit_mode = false) {
    console.log("close add popup");
    if (to_scanner) {
        start_check();
        document.getElementById("close-add-popup").onclick = () => close_add_popup(false);
    }
    if (edit_mode) {
        console.log("edit mode close");
        document.getElementById("add-popup-title").innerHTML = "Add To Personal Items";
        document.getElementById("add-popup-submit").innerHTML = "Add Item";
        document.getElementById("add-form").onsubmit = (event) => add_new_item(event);
        document.getElementById("close-add-popup").onclick = () => close_add_popup(false);
        document.getElementById("delete_item").style.display = "none";
        // closes item popup so there are no discrepancies
        document.getElementById("close-popup").click();
        // if search popup open, refresh items
        if (document.getElementById("search_popup").style.display != "none") {
            text_search_item();
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
    document.getElementById("unit_edit").value = null;
    document.getElementById("quantity2").max = null;
    document.getElementById("quantity2").value = null;
    document.getElementById("expiry_date2").value = null;
    document.getElementById("item_image_edit").value = null;
    document.getElementById("add_to_inventory").checked = false;
    toggle_inventory_fields();

    document.getElementById("add-popup").style.display = "none";
}

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

function close_not_found_popup() {
    start_check();
    document.getElementById("not_found_popup").style.display = "none";
    document.getElementById("open_not_found_button").onclick = null;
}

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

function close_report_popup() {
    document.getElementById("report_message").innerHTML = "Send request for missing item to be available for all?";
    document.getElementById("report_message_2").innerHTML = "If successful, your personal item will be replaced.";
    document.getElementById("report_button").innerHTML = "Send Report";
    document.getElementById("report_popup").style.display = "none";
    document.getElementById("report_button").onclick = null;
}

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
        close_item_popup();
    } else {
        alert('There was an error adding the item. Error: ' + result.error);
    }
}

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

