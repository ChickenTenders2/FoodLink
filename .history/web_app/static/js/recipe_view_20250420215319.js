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
        document.getElementById('update-form').addEventListener('submit', submit_add);
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

async function submit_next(event) {
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
         open_edit_ingredients_popup(ingredients)
    } else {
         alert('There was an error updating the item.');
    }
}

function open_edit_ingredients_popup(ingredients) {
    const container = document.getElementById("ingredients_list_container");
    container.innerHTML = "";
    // for each ingredient from list
    for (let ingredient of ingredients) {
        // add row
        add_ingredient_row(ingredient[0], ingredient[1], ingredient[2]);
    }
    document.getElementById("edit_ingredients_popup").style.display = "block";
}

function close_edit_ingredients_popup() {
    document.getElementById("edit_ingredients_popup").style.display = "none";
}

function add_ingredient_row(name = "", quantity = "", unit = "") {
    const row = document.createElement("div");
    row.className = "ingredient-row";

    // displays information and creates button which removes ingredient on click
    row.innerHTML = `
        <input type="text" name="name" placeholder="Name" required value="${name}">
        <input type="number" name="quantity" min="1" placeholder="Quantity" required value="${quantity}">
        <input type="text" name="unit" placeholder="Unit" required value="${unit}">
        <button type="button" onclick="this.parentElement.remove()">X</button>
    `;

    document.getElementById("ingredients_list_container").appendChild(row);
}

function update_ingredients() {
    const container = document.getElementById("ingredients_list_container");
    const rows = container.querySelectorAll(".ingredient-row");

    const new_ingredients = [];

    // loops through each row in the edit ingredients popup and gets the ingredient information
    for (let row of rows) {
        const name = row.querySelector('input[name="name"]').value.trim();
        const quantity = row.querySelector('input[name="quantity"]').value;
        const unit = row.querySelector('input[name="unit"]').value.trim();
        // makes sure no null values
        if (name && quantity && unit) {
            new_ingredients.push([name, quantity, unit]);
        }
    }
    display_ingredients(new_ingredients);
    close_edit_ingredients_popup();
}