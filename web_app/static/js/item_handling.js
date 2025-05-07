/**
 * Retrieves the image path for a given item ID.
 * If the item has an associated image, returns its image path;
 * otherwise, returns a path to a placeholder image.
 * 
 * @param {string|number} id - The item ID.
 * @returns {Promise<string>} - Path to the item's image file.
 */
async function get_image_path(id) {
    let image_name = "null";
    const response = await fetch("/items/find_image/" + id);
    const result = await response.json();
    if (result.success) {
        image_name = id;
    }
    return "/static/images/" + image_name + ".jpg";
}

/**
 * Updates the preview image shown in the form when a user selects a new image file.
 * 
 * @param {Event} event - The file input change event.
 */
function update_image_preview(event) {
    if (event.target.files && event.target.files[0]) {
        image = document.getElementById("image_preview");
        image.src = URL.createObjectURL(event.target.files[0]);
        image.onload = function() {
            URL.revokeObjectURL(image.src); //Frees up memory after image is changed
        }
    }
}

/**
 * Splits a date string in DD/MM/YYYY format and returns its parts as numbers.
 * 
 * @param {string} expiry_time - The expiry date string (e.g., "14/05/2025").
 * @returns {number[]} - An array [day, month, year].
 */
function get_expiry_values(expiry_time) {
    // Gets each part of the expiry string and maps it to a number
    return expiry_time.split('/').map(Number);
}

