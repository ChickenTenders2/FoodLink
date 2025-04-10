function open_popup(barcode_number) {
    stop_check();
    document.getElementById('barcode').value = barcode_number;
    document.getElementById('popup').style.display = 'block';
}

function close_popup() {
    document.getElementById('popup').style.display = 'none';
    document.getElementById("name").value = null;
    document.getElementById("brand").value = null;
    document.getElementById("expiry_day").value = null;
    document.getElementById("expiry_month").value = null;
    document.getElementById("expiry_year").value = null;
    document.getElementById("default_quantity").value = null;
    document.getElementById("unit").value = null;
    document.getElementById("item_image").value = null;

    fetch("/clear_barcode");
    start_check();
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
            console.log(data.barcode);
            open_popup(data.barcode);
        }
    } catch (e) {
        console.log(e);
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
    if (!valid_expiry()) {
        alert("Expiry time must be at least one day.")
        return;
    }

    // Recreates form
    const form = event.target;
    const formData = new FormData(form);

    // Sends update command and waits for response
    const response = await fetch('/add_item/add', {
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

function valid_expiry() {
    const day = parseInt(document.getElementById("expiry_day").value);
    const month = parseInt(document.getElementById("expiry_month").value);
    const year = parseInt(document.getElementById("expiry_year").value);
    return !(day == 0 && month == 0 && year == 0);

}