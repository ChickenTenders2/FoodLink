/**
 * Displays the delete confirmation modal by setting its display style to 'flex'.
 */
function showDeleteModal() {
    document.getElementById('deleteModal').style.display = 'flex';
}

/**
 * Hides the delete confirmation modal by setting its display style to 'none'.
 */
function hideDeleteModal() {
    document.getElementById('deleteModal').style.display = 'none';
}

/**
 * Closes the modal if the user clicks outside of the modal content area.
 * This ensures a user-friendly way to dismiss the modal.
 */
window.onclick = function(event) {
    if (event.target.id === 'deleteModal') {
        hideDeleteModal();
    }
}