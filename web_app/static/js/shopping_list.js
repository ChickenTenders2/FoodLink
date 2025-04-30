// Function to open the 'Add Item' popup
function openAddPopup() {
    document.getElementById('overlay').style.display = 'block';
    document.getElementById('add-popup').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

// Function to close the 'Add Item' popup and clear form fields
function closeAddPopup() {
    document.getElementById('overlay').style.display = 'none';
    document.getElementById('add-popup').style.display = 'none';
    document.getElementById('item_name').value = '';
    document.getElementById('quantity').value = '';
    document.body.style.overflow = '';
}

// Function to open the 'Edit Item' popup
function openEditPopup() {
    document.getElementById('overlay').style.display = 'block';
    document.getElementById('edit-popup').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

// Function to close the 'Edit Item' popup and clear form fields
function closeEditPopup() {
    document.getElementById('overlay').style.display = 'none';
    document.getElementById('edit-popup').style.display = 'none';
    document.getElementById('edit_item_id').value = '';
    document.getElementById('edit_item_name').value = '';
    document.getElementById('edit_quantity').value = '';
    document.body.style.overflow = '';
}

// Function to visually mark an item as bought (strikethrough text)
function markBought(button) {
    button.closest('.shopping-item').style.textDecoration = 'line-through';
}

// Pre-fill the edit popup with item values and open it
function editItem(id, name, quantity){
    document.getElementById('edit_item_id').value = id;
    document.getElementById('edit_item_name').value = name;
    document.getElementById('edit_quantity').value = quantity;
    openEditPopup();
}

// Function to show a temporary toast notification
function showToast(message) {
    const toast = document.getElementById("toast");
    toast.innerText = message;
    toast.className = "toast show";
    setTimeout(() => { toast.className = toast.className.replace("show", ""); }, 3000);
}

// Submit handler for editing an item in the shopping list
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

// Submit handler for adding a new item to the shopping list
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

// Submit handlers for marking items as bought or unbought
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

// Submit handlers for suggesting items to the shopping list
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

// Submit handlers for removing individual items
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

// Submit handler for clearing the entire shopping list
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