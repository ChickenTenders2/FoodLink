function open_item_popup(item, estimated_expiry, from_scanner) {
    // If the popup was opened from the scanner
    if (from_scanner) {
        document.getElementById("close-popup").onclick = () => close_item_popup(true);
        stop_check();
    }
    // gets variables from item
    const [id, barcode, name, brand, expiry_time, default_quantity, unit] = item;

    document.getElementById("item_id").value = id;
    document.getElementById("expiry_time").value = expiry_time;
    document.getElementById("item_image").src = "/static/images/" + id + ".jpg";
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
}

function close_item_popup(to_scanner) {
    // If the scanner will be in focus after closing
    if (to_scanner) {
        document.getElementById("close-popup").onclick = () => close_item_popup(false);
        start_check();
    }
    document.getElementById('popup').style.display = 'none';
}

function open_search_popup() {
    stop_check();
    document.getElementById('search_popup').style.display = 'block';
}

function close_search_popup() {
    start_check();
    document.getElementById('search_popup').style.display = 'none';
}

function select_item(item) {
    expiry_time = item[4];
    const [days, months, years] = get_expiry_values(expiry_time);
    const estimated_expiry = estimate_expiry_date(days, months, years);
    open_item_popup(item, estimated_expiry, false)
}

function open_add_popup(from_clone, barcode = null) {
    if (from_clone) {
        add_clone_info();
    } 
    else if (barcode) {
        stop_check();
        document.getElementById('barcode_edit').value = barcode;
        // Barcode scanning should only start if the popup leads back to the main window
        document.getElementById("close-add-popup").onclick = () => close_add_popup(true);
    }
    else {
        const search_term = document.getElementById("search_term").value;
        document.getElementById("name_edit").value = search_term;
    }
    // Displays popup
    document.getElementById('add-popup').style.display = 'block';
}

function add_clone_info() {
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
    document.getElementById("image_preview").src = "/static/images/" + original_id + ".jpg";
    document.getElementById("image_preview").alt = name;
    document.getElementById("original_item_id").value = original_id;
    document.getElementById("name_edit").value = name;
    document.getElementById("barcode_edit").value = barcode;
    document.getElementById("brand_edit").value = brand;
    document.getElementById("default_quantity").value = default_quantity;
    document.getElementById("unit_edit").value = unit;
}

function close_add_popup(to_scanner) {
    if (to_scanner) {
        start_check();
        document.getElementById("close-add-popup").onclick = () => close_add_popup(false);
    }
    document.getElementById("expiry_day").value = null;
    document.getElementById("expiry_month").value = null;
    document.getElementById("expiry_year").value = null;
    document.getElementById("image_preview").src = "";
    document.getElementById("image_preview").alt = null;
    document.getElementById("original_item_id").value = null;
    document.getElementById("name_edit").value = null;
    document.getElementById("barcode_edit").value = null;
    document.getElementById("brand_edit").value = null;
    document.getElementById("default_quantity").value = null;
    document.getElementById("quantity2").max = null;
    document.getElementById("quantity2").value = null;
    document.getElementById("expiry_date2").value = null;
    document.getElementById("item_image_edit").value = null;
    document.getElementById("add_to_inventory").checked = false;
    toggle_inventory_fields();

    document.getElementById("add-popup").style.display = "none";
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

function update_image_preview(event) {
    if (event.target.files && event.target.files[0]) {
        image = document.getElementById("image_preview");
        image.src = URL.createObjectURL(event.target.files[0]);
        image.onload = function() {
            URL.revokeObjectURL(image.src); //Frees up memory after image is changed
        }
    }
}

async function text_search_item(event) {
    // Prevent the form from submitting normally
    event.preventDefault(); 

    // Recreates form
    const form = event.target;
    const formData = new FormData(form);

    // Sends update command and waits for response
    const response = await fetch('/items/text_search', {
        method: 'POST',
        body: formData,
    });

    //Waits until result is recieved
    const result = await response.json();
    if (result.success) {
        display_search_results(result.items)
    } else {
        alert('There was an error searching. Error: ' + result.error);
    }
}

function display_search_results(items) {
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
        div.innerHTML = `
        <img src="/static/images/${id}.jpg" alt="${name}" class="item_img" onerror="this.src='/static/images/null.jpg'">
        <div class="item_info">
            ${name} (${brand}) - ${default_quantity} ${unit}
        </div>`;
        div.className = "search_result_item";
        // estimates expiry for the item and opens popup when item container is clicked on
        div.onclick = () => select_item(item);
        // adds container to search results container
        container.appendChild(div);
    }
}

// Redirects to correct function once barcode is found
function process_barcode(barcode) {
    barcode_search_item(barcode);
}

// Checks if barcode is in item table
async function barcode_search_item(barcode_number) {
    try {
        // Creates form with barcode number
        const formData = new FormData();
        formData.append("barcode", barcode_number);
        
        // Searches for item by barcode and awaits result
        const response = await fetch('/items/barcode_search', {
            method: 'POST',
            body: formData
        });                 
        let data = await response.json();

        // If an item is found
        if (data.success) {
            const [id, name, brand, expiry_time, default_quantity, unit] = data.item;
            // Calculates estimated expiry
            const [days, months, years] = get_expiry_values(expiry_time);
            const estimated_expiry = estimate_expiry_date(days, months, years);
            open_item_popup(item, estimated_expiry, true);
        } else {
            alert(data.error);
            open_add_popup(false, barcode_number);
        }
    } catch (e) {
        alert(e);
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

function estimate_expiry_from_string(expiry_time) {
    const [days, months, years] = get_expiry_values(expiry_time);
    return estimate_expiry_date(days, months, years);
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

function get_expiry_values(expiry_time) {
    // Gets each part of the expiry string and maps it to a number
    return expiry_time.split('/').map(Number);
}