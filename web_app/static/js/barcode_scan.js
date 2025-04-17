// Releases camera module on page close
window.onbeforeunload = function(){
    fetch("/scanner/close");
}   

// Starts check when window is opened
window.onload = function(){
    start_check();
}

// Stops checking for barcode
function stop_check() {
    clearInterval(window.interval_id);
    window.interval_id = null;
}

// Checks if a barcode has been found every second
function start_check() {
    fetch("/unpause_scanner")
    // Stops multiple checkers from running
    if (window.interval_id == null) {
        window.interval_id = setInterval(get_object, 1000);
    }
}

function toggle_scan_mode() {
    //gets if checkbox is ticked or not
    checked = document.getElementById("scan_mode").checked;
    fetch("/scanner/toggle_mode/" + checked);
}

// Checks if an object (barcode or AI identified item name) has been found
async function get_object() {
    try {
        let response = await fetch("/scanner/get_object");
        let data = await response.json();
        if (data.success) {
            // Redirects to correct function for each page
            process_barcode(data.object);
        }
    } catch (e) {
        alert(e);
    }
}