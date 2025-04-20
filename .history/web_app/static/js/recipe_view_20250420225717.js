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
            submit_next(event, recipe_id);});
    } else {
        document.getElementById('popup-title').innerText = `Edit ${recipeName}`;
        document.getElementById('update-form').addEventListener('submit', function(event) {
            submit_next(event, recipe_id);});
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
    const response = await fetch('/admin/item_view/update_recipe', {
         method: 'POST',
         body: formData,
     });
 
    //Waits until result is recieved
    const result = await response.json();
 
    if (result.success) {
        close_popup()
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
        let ingredients = await response.json();
        
            // for each ingredient from list
    for (let ingredient of ingredients) {
        // add row
        add_ingredient_row(ingredient[0], ingredient[1], ingredient[2], recipe_id);
    }
    document.getElementById("edit_ingredients_popup").style.display = "block";
    } catch (error) {
        // Log any errors to the console (e.g., 404 or JSON parsing errors)
        console.error('Error fetching ingredients:', error);
    }
}

function add_ingredient_row(name = "", quantity = "", unit = "", recipe_id) {
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
    document.getElementById('edit_ingredients_popup').addEventListener('submit', function(event) {
        update_ingredients(event, recipe_id);});
}

function close_edit_ingredients_popup() {
    document.getElementById("edit_ingredients_popup").style.display = "none";
}

function update_ingredients(recipe_id) {
    close_edit_ingredients_popup();
    console.log(recipe_id);
    get_tools(recipe_id);
}

async function get_tools(recipe_id) {
    try {
        const response = await fetch('/admin/recipe_view/add_tools/' + recipe_id, {
            method: 'GET', // No body needed for GET request
        });
        
        // Check if the request was successful (status 200)
        if (!response.ok) {
            // If response is not OK, throw an error with the response status
            throw new Error(`Failed to fetch ingredients. Status: ${response.status}`);
        }

        // Parse the JSON response
        let ingredients = await response.json();
        
            // for each ingredient from list
    for (let ingredient of ingredients) {
        // add row
        add_ingredient_row(ingredient[0], ingredient[1], ingredient[2]);
    }
    document.getElementById("edit_ingredients_popup").style.display = "block";
    } catch (error) {
        // Log any errors to the console (e.g., 404 or JSON parsing errors)
        console.error('Error fetching ingredients:', error);
    }
}

function open_edit_tools_popup(tool_ids) {
    const container = document.getElementById("tools_list_container");
    container.innerHTML = "";

    const addContainer = document.getElementById("tool_add_controls");
    addContainer.innerHTML = "";

    // creates the selection dropdown
    const dropdown = document.createElement("select");
    dropdown.id = "tool_selector";

    // adds options that are not in tool_ids (tool_ids are unique and shouldnt be added twice)
    for (let [tool_id, tool_name] of Object.entries(window.tools)) {
        if (!tool_ids.includes(parseInt(tool_id))) {
            const option = document.createElement("option");
            option.value = tool_id;
            option.innerText = tool_name;
            dropdown.appendChild(option);
        }
    }

    // adds button to add selected from dropdown 
    const addButton = document.createElement("button");
    addButton.innerText = "+ Add Tool";
    addButton.onclick = () => {
        const selected_id = parseInt(dropdown.value);
        add_tool_display_row(selected_id, dropdown);
    };

    addContainer.appendChild(dropdown);
    addContainer.appendChild(addButton);

    // displays initial tools for recipe
    for (let id of tool_ids) {
        add_tool_display_row(id, dropdown);
    }

    document.getElementById("edit_tools_popup").style.display = "block";
}

function add_tool_display_row(tool_id, dropdown) {
    const container = document.getElementById("tools_list_container");
    const row = document.createElement("div");
    row.className = "tool-row";

    // adds tool name to row
    const tool_name = window.tools[tool_id];
    const label = document.createElement("span");
    label.innerText = tool_name;
    label.value = tool_id;
    row.appendChild(label);

    // adds remove button to row
    const remove_button = document.createElement("button");
    remove_button.innerText = "X";
    remove_button.onclick = () => {
        // removes row on click and
        row.remove();
        // adds option back to dropdown
        const option = document.createElement("option");
        option.value = tool_id;
        option.innerText = tool_name;
        dropdown.appendChild(option);
    };

    row.appendChild(remove_button);
    container.appendChild(row);

    // removes selected option from dropdown (if not already removed)
    const optionToRemove = dropdown.querySelector(`option[value="${tool_id}"]`);
    if (optionToRemove) {
        optionToRemove.remove();
    }
}
