async function remove_item(id, event) {
    
    event.stopPropagation();

    // Sends update command and waits for response
    const response = await fetch('/admin/recipe_view/delete', {
        method: 'POST',
        body: id,
    })
    
    //Waits until result is recieved
    const result = await response.json();
    
    if (result.success) {
        // Updates page
        location.reload();
    } else {
        alert('There was an error deleting the item.');
    }
}

// Opens item information popup
function open_popup(recipeName, name, instructions, recipe_id, add=false) {
    // Sets values in popup to those of the item
    if (add == true) {
        document.getElementById('popup-title').innerText = `Add ${recipeName}`;
        document.getElementById('update-form').addEventListener('submit', submit_add);
    } else{
        document.getElementById('popup-title').innerText = `Edit ${recipeName}`;
        document.getElementById('update-form').addEventListener('submit', submit_update);
    }
    document.getElementById('name').value = name;
    document.getElementById('instructions').value = instructions;
    document.getElementById('original-instructions').value = instructions;
    document.getElementById('original-name').value = name;
    document.getElementById('recipe-id').value = recipe_id;
    document.getElementById('popup').style.display = 'block';
}

// Closes item information popup
function close_popup() {
    document.getElementById('popup').style.display = 'none';
}

// Updates item in inventory
async function submit_update(event) {
    // Prevent the form from submitting normally
    event.preventDefault(); 

    // Gets original values
    const originalInstructions = document.getElementById('original-instructions').value;
    const originalName = document.getElementById('original-name').value;
    const originalID = document.getElementById('original-user-id').value;
    
    // Gets new values
    const newInstructions = document.getElementById('instructions').value;
    const newName = document.getElementById('name').value;
    const newID = document.getElementById('user-id').value;
    
    // Checks if values have not been edited
    if (newName == originalName && newInstructions == originalInstructions) {
        // Prevent sending the update request
        close_popup();
        return;  
    }

    // Recreates form
    const form = event.target;
    const formData = new FormData(form);

    // Sends update command and waits for response
    const response = await fetch('/admin/item_view/update_recipe', {
        method: 'POST',
        body: formData,
    });

    //Waits until result is recieved
    const result = await response.json();

    if (result.success) {
        // Updates page
        location.reload();
    } else {
        alert('There was an error updating the item.');
    }
}

async function submit_add(event) {
    // Prevent the form from submitting normally
    event.preventDefault(); 

    // Recreates form
    const form = event.target;
    const formData = new FormData(form);
 
    // Sends update command and waits for response
    const response = await fetch('/admin/recipe_view/add_item', {
         method: 'POST',
         body: formData,
     });
 
    //Waits until result is recieved
    const result = await response.json();
 
    if (result.success) {
         // Updates page
         location.reload();
    } else {
         alert('There was an error updating the item.');
    }
}
