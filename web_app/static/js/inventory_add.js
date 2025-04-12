function open_item_popup(id, barcode_number, name, brand, expiry_time, estimated_expiry, default_quantity, unit) {
    stop_check();
    document.getElementById("item_id").value = id;
    document.getElementById("expiry_time").value = expiry_time;
    document.getElementById("item_image").src = "/static/images/" + id + ".jpg";
    document.getElementById("item_image").alt = name;
    document.getElementById("barcode").value = barcode_number;
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

function close_item_popup() {
    start_check();
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
        const [id, barcode, name, brand, expiry_time, default_quantity, unit] = item;
        // adds the item information and image
        div.innerHTML = `
        <img src="/static/images/${id}.jpg" alt="${name}" class="item_img" onerror="this.src='/static/images/null.jpg'">
        <div class="item_info">
            ${name} (${brand}) - ${default_quantity} ${unit}
        </div>`;
        div.className = "search_result_item";
        // estimates expiry for the item and opens popup when item container is clicked on
        div.onclick = () => open_item_popup(id, barcode, name, brand, expiry_time, estimate_expiry_date(expiry_time), default_quantity, unit);
        // adds container to search results container
        container.appendChild(div);
    }
}

// Checks if a barcode has been found
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
            const estimated_expiry = estimate_expiry_date(expiry_time);
            open_item_popup(id, barcode_number, name, brand, expiry_time, estimated_expiry, default_quantity, unit);
        } else {
            alert(data.error);
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

// Calculate an estimate of the expiry date
function estimate_expiry_date(expiry_time) {
    // Gets each part of the expiry string and maps it to a number
    const [days, months, years] = get_expiry_values(expiry_time);
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
    return expiry_time.split('/').map(Number);
}

function open_add_popup() {
    // document.getElementById("barcode").removeAttribute("readonly");
    // document.getElementById("name").removeAttribute("readonly");
    // document.getElementById("brand").removeAttribute("readonly");
    // document.getElementById("name").setAttribute("required", true);
    // document.getElementById("brand").setAttribute("required", true);


    // for (let div of document.querySelectorAll(".item_fields")) {
    //     div.style.display = "block";
    // }

    // for (let div of document.querySelectorAll(".inventory_fields")) {
    //     div.style.display = "none";
    // }

    document.getElementById("add-popup").style.display = "block";
}

function close_add_popup() {
    document.getElementById("add-popup").style.display = "none";
}

function toggle_inventory_fields() {
    const checkbox = document.getElementById("add_to_inventory").checked;
    if (checkbox) {
        document.getElementById("inventory_fields").style.display = "block";
    } else {
        document.getElementById("inventory_fields").style.display = "none";
    }
    const default_quantity = document.getElementById("default_quantity").value;
    if (default_quantity > 1) {
        document.getElementById("quantity").max = default_quantity;
    }
}

function hide_inventory_fields() {
    document.getElementById("inventory_fields").style.display = "none";
}
