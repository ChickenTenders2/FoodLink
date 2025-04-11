function open_popup(barcode_number) {
    stop_check();
    document.getElementById('barcode').value = barcode_number;
    document.getElementById('popup').style.display = 'block';
}

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

// Opens popup to add item information once barcode is scanned succesfully
async function get_barcode() {
    try {
        let response = await fetch("/get_barcode");
        let data = await response.json();
        
        if (data.success) {
            // resets barcode number
            fetch("/clear_barcode");
            open_popup(data.barcode);
        }
    } catch (e) {
        console.log(e);
    }
}

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

// Returns if expiry time is more than a day
function valid_expiry() {
    const day = parseInt(document.getElementById("expiry_day").value);
    const month = parseInt(document.getElementById("expiry_month").value);
    const year = parseInt(document.getElementById("expiry_year").value);
    return !(day == 0 && month == 0 && year == 0);

}