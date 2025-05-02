let video = document.getElementById('webcam');
let canvas = document.getElementById('canvas');
let context = canvas.getContext('2d');
let scanMode = 'barcode'; // or 'ai'
let scanInterval = null;

// Request webcam access and start scanning
async function startScanner() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
        scanInterval = setInterval(captureAndScan, 1000);
    } catch (err) {
        console.error("Camera access failed:", err);
    }
}

// Capture a frame and send it to the backend
async function captureAndScan() {
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg'));
    
    const response = await fetch(`/scanner/analyze?mode=${scanMode}`, {
        method: "POST",
        body: blob
    });

    const data = await response.json();
    if (data.success) {
        process_barcode(data.object); // your existing handler
        stopScanner(); // optional: stop scanning once found
    }
}

function toggle_scan_mode() {
    scanMode = document.getElementById("scan_mode").checked ? "ai" : "barcode";
}

function stopScanner() {
    if (scanInterval) clearInterval(scanInterval);
    const stream = video.srcObject;
    if (stream) stream.getTracks().forEach(track => track.stop());
    video.srcObject = null;
}
