/**
 * Opens the "Add Item" popup and disables page scrolling.
 */
function openAddPopup() {
    document.getElementById('overlay').style.display = 'block';
    document.getElementById('add-popup').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

/**
 * Closes the "Add Item" popup, clears input fields, and restores page scroll.
 */
function closeAddPopup() {
    document.getElementById('overlay').style.display = 'none';
    document.getElementById('add-popup').style.display = 'none';
    document.getElementById('item_name').value = '';
    document.getElementById('quantity').value = '';
    document.body.style.overflow = '';
}

/**
 * Opens the "Edit Item" popup and disables page scrolling.
 */
function openEditPopup() {
    document.getElementById('overlay').style.display = 'block';
    document.getElementById('edit-popup').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

/**
 * Closes the "Edit Item" popup, clears input fields, and restores page scroll.
 */
function closeEditPopup() {
    document.getElementById('overlay').style.display = 'none';
    document.getElementById('edit-popup').style.display = 'none';
    document.getElementById('edit_item_id').value = '';
    document.getElementById('edit_item_name').value = '';
    document.getElementById('edit_quantity').value = '';
    document.body.style.overflow = '';
}

/**
 * Applies a strikethrough effect to mark an item as bought in the UI.
 * 
 * @param {HTMLElement} button - The button inside the shopping item row.
 */
function markBought(button) {
    button.closest('.shopping-item').style.textDecoration = 'line-through';
}

/**
 * Pre-fills the edit form fields with existing values and opens the edit popup.
 * 
 * @param {string|number} id - Item ID.
 * @param {string} name - Item name.
 * @param {string|number} quantity - Item quantity.
 */
function editItem(id, name, quantity){
    document.getElementById('edit_item_id').value = id;
    document.getElementById('edit_item_name').value = name;
    document.getElementById('edit_quantity').value = quantity;
    openEditPopup();
}

/**
 * Displays a temporary toast message with color based on success/failure.
 * 
 * @param {string} message - The message to display.
 * @param {boolean} isSuccess - Optional, if true shows green toast, else red (default is success).
 */
function showToast(message) {
    const toast = document.getElementById("toast");
    toast.innerText = message;
    toast.className = "toast show";
    setTimeout(() => { toast.className = toast.className.replace("show", ""); }, 3000);
}

/**
 * Handles submission of the edit form and updates the item via AJAX.
 */
document.getElementById('editForm').addEventListener('submit', function (e) {
    e.preventDefault();
    e.stopPropagation();
    const form = e.target;
    const formData = new FormData(form);
    fetch('/shopping_list/update', {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        showToast(`Updated "${data.item}" to shopping list.`);
        setTimeout(() => location.reload(), 1000);
      } else {
        alert('Failed to update item: ' + data.error);
      }
    });
});

/**
 * Handles submission of the add form and adds a new item to the list.
 */
document.getElementById('addForm').addEventListener('submit', function (e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    fetch('/shopping_list/add', {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        showToast(`Added "${data.item}" to shopping list.`);
        setTimeout(() => location.reload(), 1000);
      } else {
        alert('Failed to add item: ' + data.error);
      }
    });
});

/**
 * Handles submission of bought/unbought toggle forms for each item.
 */
document.querySelectorAll('.boughtForm').forEach(form => {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const formData = new FormData(form);
      const boughtValue = formData.get('bought');
      fetch('/shopping_list', {
        method: 'POST',
        body: formData
      })
      .then(response => response.json())
      .then(data => {
        if (data.success && data.action === 'mark_bought') {
          const message = boughtValue === '1'
            ? 'Item marked as bought'
            : 'Item moved back to list'
          showToast(message);
          setTimeout(() => location.reload(), 1000);
        }
      });
    });
});

/**
 * Handles submission of suggest forms to add recommended items to the list.
 */
document.querySelectorAll('.suggestForm').forEach(form => {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const formData = new FormData(form);
      fetch(form.action, {
        method: 'POST',
        body: formData
      })
      .then(response => response.json())
      .then(data => {
        if (data.success && data.action === 'add') {
          showToast(`Added "${data.item}" to shopping list.`);
          setTimeout(() => location.reload(), 1000);
        }
      });
    });
});

/**
 * Handles submission of remove buttons to delete individual items from the list.
 */
document.querySelectorAll('.removeForm').forEach(form => {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const formData = new FormData(form);
      fetch('/shopping_list', {
        method: 'POST',
        body: formData
      })
      .then(response => response.json())
      .then(data => {
        if (data.success && data.action === 'remove') {
          showToast(`Removed item.`);
          setTimeout(() => location.reload(), 1000);
        }
      });
    });
});

/**
 * Handles submission of the clear form to remove all items from the list.
 */
document.getElementById('clearForm').addEventListener('submit', function (e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    fetch('/shopping_list', {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      if (data.success && data.action === 'clear') {
        showToast('Shopping list cleared.');
        setTimeout(() => location.reload(), 1000);
      }
    });
});