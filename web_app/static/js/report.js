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

async function get_item(id, original = false) {
    try {
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
    } catch (e) {
        alert(e);
    }
}

function set_missing_report() {
    document.getElementById("original_item").style.display = "none";
    document.getElementById("new_item_heading").innerHTML = "Missing Item Information";
    document.getElementById("modify_type").value = "add";
}

window.onload = async function() {
    const new_item_id = document.getElementById("new_item_id").value;
    await get_item(new_item_id);
    const original_item_id = document.getElementById("original_item_id").value;
    if (original_item_id != "null") {
        await get_item(original_item_id, true);
    } else {
        set_missing_report();
    }
}

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

