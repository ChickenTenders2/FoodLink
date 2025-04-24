// returns the image path for an item or the placeholder image if it doesnt have one
async function get_image_path(id) {
    let image_name = "null";
    try {
        const response = await fetch("/find_image/" + id);
        const result = await response.json();
        if (result.success) {
            image_name = id;
        }
    } catch (e) {
        console.log(e);
    }
    return "/static/images/" + image_name + ".jpg";
}

function update_image_preview(event) {
    if (event.target.files && event.target.files[0]) {
        image = document.getElementById("image_preview");
        image.src = URL.createObjectURL(event.target.files[0]);
        image.onload = function() {
            URL.revokeObjectURL(image.src); //Frees up memory after image is changed
        }
    }
}

function get_expiry_values(expiry_time) {
    // Gets each part of the expiry string and maps it to a number
    return expiry_time.split('/').map(Number);
}

