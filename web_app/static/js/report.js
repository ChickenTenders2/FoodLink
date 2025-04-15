async function fill_item(id, barcode, name, brand, days, months, years, default_quantity, unit) {
    document.getElementById("expiry_day").value = days;
    document.getElementById("expiry_month").value = months;
    document.getElementById("expiry_year").value = years;
    document.getElementById("image_preview").src = await get_image_path(id);
    document.getElementById("image_preview").alt = name;
    document.getElementById("name").value = name;
    document.getElementById("barcode").value = barcode;
    document.getElementById("brand").value = brand;
    document.getElementById("default_quantity").value = default_quantity;
    document.getElementById("unit").value = unit;
}

async function get_item(id) {
    try {
        // Searches for item by barcode and awaits result
        const response = await fetch('/items/get_item/'+ id);               
        let result = await response.json();

        // If an item is found
        if (result.success) {
            const [id, barcode, name, brand, expiry_time, default_quantity, unit] = result.item;
            const [days, months, years] = get_expiry_values(expiry_time);
            fill_item(id, barcode, name, brand, days, months, years, default_quantity, unit);
        } else {
            alert(result.error)
        }
    } catch (e) {
        alert(e);
    }
}

window.onload = function() {
    const new_item_id = document.getElementById("new_item_id").value;
    get_item(new_item_id);
}