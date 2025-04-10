
function open_popup(id, barcode_number, name, brand, estimated_expiry, default_quantity, unit) {
    stop_check();
    document.getElementById("item_id").value = id;
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

function close_popup() {
    document.getElementById('popup').style.display = 'none';
    start_check();
}

function open_search_popup() {
    stop_check();
    document.getElementById('search_popup').style.display = 'block';
}

function close_search_popup() {
    document.getElementById('search_popup').style.display = 'none';
    start_check();
}

async function search_item(event) {
    // Prevent the form from submitting normally
    event.preventDefault(); 

    // Recreates form
    const form = event.target;
    const formData = new FormData(form);

    // Sends update command and waits for response
    const response = await fetch('/inventory/add_item/search', {
        method: 'POST',
        body: formData,
    });

    //Waits until result is recieved
    const result = await response.json();
    if (result.success) {
        display_search(result.items)
    } else {
        alert('There was an error searching. Error: ' + result.error);
    }
}

function display_search(items) {
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
        // opens popup when item is clicked on
        div.onclick = () => open_popup(id, barcode, name, brand, expiry_time, default_quantity, unit);
        // adds container to search results container
        container.appendChild(div);
    }
}

window.onbeforeunload = function(){
    fetch("/close_capture");
}   

window.onload = function(){
    start_check();
}

async function check_barcode() {
    try {
        let response = await fetch("/check_barcode");
        let data = await response.json();

        if (data.barcode) {
            // resets barcode number
            fetch("/clear_barcode")
            // searches for item by barcode
            get_item(data.barcode);
        }
    } catch (e) {
        alert(e);
    }
}

function start_check() {
    window.interval_id = setInterval(check_barcode, 1000);
}

function stop_check() {
    clearInterval(window.interval_id);
}

async function submit_item(event) {
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
        close_popup();
    } else {
        alert('There was an error adding the item. Error: ' + result.error);
    }
}

async function get_item(barcode_number) {
    try {
        // Creates form with barcode number
        const formData = new FormData();
        formData.append("barcode", barcode_number)
        
        // Searches for item by barcode and awaits result
        const response = await fetch('/barcode_search', {
            method: 'POST',
            body: formData
        });                 
        let data = await response.json();

        // If an item is found
        if (data.success) {
            open_popup(data.item[0], barcode_number, data.item[1], data.item[2], data.item[3], data.item[4], data.item[5]);
        } else {
            alert(data.error)
        }
    } catch (e) {
        alert(e);
    }
}