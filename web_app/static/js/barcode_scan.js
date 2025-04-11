// Releases camera module on page close
window.onbeforeunload = function(){
    fetch("/close_scanner");
}   

// Starts check when window is opened
window.onload = function(){
    start_check();
}

// Stops checking for barcode
function stop_check() {
    clearInterval(window.interval_id);
}

// Checks if a barcode has been found every second
function start_check() {
    window.interval_id = setInterval(get_barcode, 1000);
}

// Checks if a barcode has been found
async function get_barcode() {
    try {
        let response = await fetch("/get_barcode");
        let data = await response.json();
        if (data.success) {
            // Redirects to correct function for each page
            process_barcode(data.barcode);
        }
    } catch (e) {
        alert(e);
    }
}
