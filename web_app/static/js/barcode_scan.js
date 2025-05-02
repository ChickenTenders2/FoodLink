let video = document.getElementById('camera');
let canvas = document.getElementById('snapshot');
let context = canvas.getContext('2d');

// Start webcam stream
navigator.mediaDevices.getUserMedia({ video: true })
.then((stream) => {
    video.srcObject = stream;
})
.catch((err) => {
    console.error("Webcam access error:", err);
});

// Repeatedly capture frame and send to server
function captureAndSendFrame() {
    if (!video.videoWidth) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(async (blob) => {
        let formData = new FormData();
        formData.append('frame', blob, 'frame.jpg');

        const response = await fetch('/scanner/analyze_frame', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        if (data.success) {
            process_barcode(data.object);
        }
    }, 'image/jpeg');
}

// Start scanning on page load
window.onload = function() {
    start_check();
};

function start_check() {
    if (!window.interval_id) {
        window.interval_id = setInterval(captureAndSendFrame, 1000); // every second
    }
}

function stop_check() {
    clearInterval(window.interval_id);
    window.interval_id = null;
}

function toggle_scan_mode() {
    const checked = document.getElementById("scan_mode").checked;
    fetch("/scanner/toggle_mode/" + checked);
}