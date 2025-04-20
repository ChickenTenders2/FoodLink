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
function open_popup(recipeName, name, servings, prep, cook, instructions, recipe_id, add=false) {
    // Sets values in popup to those of the item
    if (add == true) {
        document.getElementById('popup-title').innerText = `Add ${recipeName}`;
        document.getElementById('update-form').addEventListener('submit', function(event) {
            const recipe_id = 1;
            submit_next(recipe_id);});
    } else {
        document.getElementById('popup-title').innerText = `Edit ${recipeName}`;
        document.getElementById('update-form').addEventListener('submit', submit_update);
    }
    document.getElementById('name').value = name;
    document.getElementById('servings').value = servings;
    document.getElementById('prep').value = prep;
    document.getElementById('cook').value = cook;
    document.getElementById('instructions').value = instructions;
    document.getElementById('original-instructions').value = instructions;
    document.getElementById('original-name').value = name;
    document.getElementById('original-servings').value = servings;
    document.getElementById('original-prep').value = prep;
    document.getElementById('original-cook').value = cook;
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
    const originalServings = document.getElementById('original-servings').value;
    const originalCook = document.getElementById('original-cook').value;
    const originalPrep = document.getElementById('original-prep').value;

    // Gets new values
    const newInstructions = document.getElementById('instructions').value;
    const newName = document.getElementById('name').value;
    const newServings = document.getElementById('servings').value;
    const newCook = document.getElementById('cook').value;
    const newPrep = document.getElementById('prep').value;
    
    // Checks if values have not been edited
    if (newName == originalName && newInstructions == originalInstructions
        && originalCook == newCook && originalServings == newServings 
        && originalPrep == newPrep)
    {
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

async function submit_next(event, recipe_id) {
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
        get_ingredients(recipe_id)
    } else {
         alert('There was an error updating the item.');
    }
}

async function get_ingredients(recipe_id) {
    try {
        const response = await fetch('/admin/recipe_view/add_item/' + recipe_id, {
            method: 'GET', // No body needed for GET request
        });
        
        // Check if the request was successful (status 200)
        if (!response.ok) {
            // If response is not OK, throw an error with the response status
            throw new Error(`Failed to fetch ingredients. Status: ${response.status}`);
        }

        // Parse the JSON response
        const ingredients = await response.json();
        
        // Use the ingredients list in your app
        console.log(ingredients);
    } catch (error) {
        // Log any errors to the console (e.g., 404 or JSON parsing errors)
        console.error('Error fetching ingredients:', error);
    }
}


