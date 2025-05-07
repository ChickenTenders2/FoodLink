let video = document.getElementById('camera');
let canvas = document.getElementById('snapshot');
let context = canvas.getContext('2d');


/**
 * Starts the webcam video stream and sets it as the source for the video element.
 */
navigator.mediaDevices.getUserMedia({ video: true })
.then((stream) => {
    video.srcObject = stream;
})
.catch((err) => {
    console.error("Webcam access error:", err);
});


/**
 * Captures a frame from the webcam stream, sends it to the server,
 * and processes the response if an object (barcode or item) is detected.
 */
function captureAndSendFrame() {
    if (!video.videoWidth) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    // Each frame is drawn on thr invisible canvas.
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(async (blob) => {
        // Blob holds the content of the canvas (the frame to be analysed).
        let formData = new FormData();
        formData.append('frame', blob, 'frame.jpg');

        const response = await fetch('/scanner/analyse_frame', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        if (data.success) {
            process_barcode(data.object);
        }
    }, 'image/jpeg');
}


/**
 * Automatically starts scanning when the page is fully loaded.
 */
window.onload = function() {
    start_check();
};

/**
 * Starts the interval-based scanner loop which captures frames every second.
 * Prevents multiple intervals by checking `window.interval_id`.
 */
function start_check() {
    if (!window.interval_id) {
        window.interval_id = setInterval(captureAndSendFrame, 1000); // every second
    }
}

/**
 * Stops the interval-based scanner loop and clears the timer.
 */
function stop_check() {
    clearInterval(window.interval_id);
    window.interval_id = null;
}


/**
 * Toggles the scan mode (barcode vs object recognition) by notifying the backend.
 */
function toggle_scan_mode() {
    const checked = document.getElementById("scan_mode").checked;
    fetch("/scanner/toggle_mode/" + checked);
}