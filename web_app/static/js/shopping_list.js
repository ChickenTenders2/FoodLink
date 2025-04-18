function openAddPopup() {
    document.getElementById('overlay').style.display = 'block';
    document.getElementById('add-popup').style.display = 'block';
    document.body.style.overflow = 'hidden';
}
function closeAddPopup() {
    document.getElementById('overlay').style.display = 'none';
    document.getElementById('add-popup').style.display = 'none';
    document.getElementById('item_name').value = '';
    document.getElementById('quantity').value = '';
    document.body.style.overflow = '';
}
function openEditPopup() {
    document.getElementById('overlay').style.display = 'block';
    document.getElementById('edit-popup').style.display = 'block';
    document.body.style.overflow = 'hidden';
}
function closeEditPopup() {
    document.getElementById('overlay').style.display = 'none';
    document.getElementById('edit-popup').style.display = 'none';
    document.getElementById('edit_item_id').value = '';
    document.getElementById('edit_item_name').value = '';
    document.getElementById('edit_quantity').value = '';
    document.body.style.overflow = '';
}
function markBought(button) {
    button.closest('.shopping-item').style.textDecoration = 'line-through';
}
function editItem(id, name, quantity){
    document.getElementById('edit_item_id').value = id;
    document.getElementById('edit_item_name').value = name;
    document.getElementById('edit_quantity').value = quantity;
    openEditPopup();
}
function showToast(message) {
    const toast = document.getElementById("toast");
    toast.innerText = message;
    toast.className = "toast show";
    setTimeout(() => { toast.className = toast.className.replace("show", ""); }, 3000);
}
  
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