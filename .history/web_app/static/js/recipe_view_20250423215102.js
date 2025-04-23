async function remove_item(id, event) {
    if (!confirm("Are you sure you want to delete this recipe?")) {
        return;
    }
    
    event.stopPropagation();

    // Sends update command and waits for response
    const response = await fetch('/admin/recipe_view/delete', {
        method: 'POST',
        body: id,
    })
    
    // Waits until the result is recieved.
    const result = await response.json();
    
    if (result.success) {
        // Updates the page.
        location.reload();
    } else {
        alert('There was an error deleting the item.');
    }
}

// Opens the item information popup.
function open_popup(recipeName, name, servings, prep, cook, instructions, recipe_id, add=false) {
    // Sets values in popup to those of the item.

    // Add is a boolean check to see if items are updated or added to the database.
    if (add == true) {
        document.getElementById('popup-title').innerText = `Add ${recipeName}`;
            // Adds the functionality to submit the form and move to the next state.
        document.getElementById('update-form').addEventListener('submit', function(event) {
            submit_next_add(event);});

        document.getElementById('exit').style.display = "block";
    } else {
        // Adds the functionality to submit the form and move to the next state.
        document.getElementById('popup-title').innerText = `Edit ${recipeName}`;

        document.getElementById('update-form').addEventListener('submit', function(event) {
            submit_next_update(event, recipe_id);});
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

// Closes the recipe information popup.
function close_popup() {
    document.getElementById('popup').style.display = 'none';
}

async function submit_next_update(event, recipe_id) {
    // Prevents the form from submitting normally.
    event.preventDefault(); 

    // Recreates the form.
    const form = event.target;
    const formData = new FormData(form);
 
    // Sends update command and waits for response.
    const response = await fetch('/admin/item_view/update_recipe', {
         method: 'POST',
         body: formData,
     });
 
    // Waits until result is recieved.
    const result = await response.json();
 
    if (result.success) {
        close_popup()
        get_ingredients_update(recipe_id)
    } else {
         alert('There was an error updating the item.');
    }
}

async function submit_next_add(event) {
    // Prevents the form from submitting normally.
    event.preventDefault(); 

    // Recreates the form.
    const form = event.target;
    const formData = new FormData(form);
 
    // Sends update command and waits for response.
    const response = await fetch('/admin/item_view/add_recipe', {
         method: 'POST',
         body: formData,
     });
 
    // Waits until result is recieved.
    const result = await response.json();
    
    // Getting the recipe id of the latest recipe to be added (the one added in the previous state).
    if (result.success) {
        const response_recipe = await fetch('/admin/recipe_view/recipe_id/', {
            method: 'GET',
        });

          // Checks if the request was successful.
          if (!response_recipe.ok) {
            throw new Error(`Failed to add recipe. Status: ${response.status}`);
        }

        // Parses the JSON response.
        let recipe_id = await response_recipe.json();

        close_popup()
        create_list_ingredients(recipe_id[0])
    } else {
         alert('There was an error updating the item.');
    }
}

async function get_ingredients_update(recipe_id) {
    try {
        const response = await fetch('/admin/recipe_view/add_item/' + recipe_id, {
            method: 'GET',
        });
        
        // Checks if the request was successful.
        if (!response.ok) {
            throw new Error(`Failed to fetch ingredients. Status: ${response.status}`);
        }

        // Parses the JSON response.
        let ingredients = await response.json();
        
            // for each ingredient from list
        for (let ingredient of ingredients) {
            // Adds a row.
            add_ingredient_row(ingredient[0], ingredient[1], ingredient[2], recipe_id);
        }
        document.getElementById("edit_ingredients_popup").style.display = "block";

        // Adds the functionality to update the ingredients to the submit button.
        document.getElementById("update-form-items").addEventListener('submit', (event) => {
        update_ingredients(event, recipe_id);

        });    
    } catch (error) {
        // Log any errors to the console (e.g., 404 or JSON parsing errors)
        console.error('Error fetching ingredients:', error);
    }
}

async function create_list_ingredients(recipe_id) {
    try {
    // Adding empty rows to be filled by the user.
    add_ingredient_row("", "", "", recipe_id);
    document.getElementById("edit_ingredients_popup").style.display = "block";

    // Adding functionality that submits the ingredients form to the add ingredients button.
    document.getElementById("update-form-items").addEventListener('submit', (event) => {
        add_ingredients(event, recipe_id);
    });    
    } catch (error) {
        // Logs any errors to the console.
        console.error('Error fetching ingredients:', error);
}
}

function add_ingredient_row(name = "", quantity = "", unit = "", recipe_id) {
    const row = document.createElement("div");
    row.className = "ingredient-row";

    // Displays information and creates button which removes ingredient on click.
    row.innerHTML = `
        <input type="text" name="name[]" placeholder="Name" required value="${name}">
        <input type="text" name="unit[]" placeholder="Unit" required value="${unit}">
        <input type="number" name="quantity[]" min="1" placeholder="Quantity" required value="${quantity}">
        <br>
        <input type="hidden" name="recipe-id" placeholder="recipe-id" required value="${recipe_id}">
        <button type="button" onclick="remove_conditional(this)">X</button>
    `;

    document.getElementById("ingredients_list_container").appendChild(row);
}

// Closes the recipe ingredients popup.
function close_edit_ingredients_popup() {
    document.getElementById("edit_ingredients_popup").style.display = "none";
}

async function update_ingredients(event, recipe_id) {
    event.preventDefault();

    // Recreates form
    const form = event.target;
    const formData = new FormData(form);
     
    // Sends update command and waits for response
    const response = await fetch('/admin/item_view/update_recipe_ingredients', {
             method: 'POST',
             body: formData,
         });
     
    //Waits until result is recieved
    const result = await response.json();
     
    if (result.success) {
        close_edit_ingredients_popup();
        get_tools(recipe_id);
    } else {
        alert('There was an error updating the ingredients.');
    }
}

async function add_ingredients(event, recipe_id) {
    event.preventDefault();

    // Recreates the form.
    const form = event.target;
    const formData = new FormData(form);
     
    // Fetches the flask route for adding ingredients to the database.
    const response = await fetch('/admin/item_view/add_recipe_ingredients', {
             method: 'POST',
             body: formData,
         });
     
    //Waits until result is recieved.
    const result = await response.json();
     
    if (result.success) {
        close_edit_ingredients_popup();
        create_list_tools(recipe_id);
    } else {
        alert('There was an error adding the ingredients.');
    }
}

async function update_ingredients(event, recipe_id) {
    event.preventDefault();

    // Recreates the form.
    const form = event.target;
    const formData = new FormData(form);
     
    // Fetches the flask route for updating ingredients in the database.
    const response = await fetch('/admin/item_view/update_recipe_ingredients', {
             method: 'POST',
             body: formData,
         });
     
    //Waits until result is recieved
    const result = await response.json();
     
    if (result.success) {
        close_edit_ingredients_popup();
        get_tools(recipe_id);
    } else {
        alert('There was an error updating the item.');
    }
}

async function get_tools(recipe_id) {
    try {
        // Gets the tools asociated with the recipe that is being edited.
        const response_id = await fetch('/admin/recipe_view/get_tools_ids/' + recipe_id, {
            method: 'GET', 
        });
        
        // Checks if the request was successful.
        if (!response_id.ok) {
            throw new Error(`Failed to fetch tools. Status: ${response.status}`);
        }

        // Parses the JSON response.
        let tools = await response_id.json();

        const response_tool = await fetch('/admin/recipe_view/get_tools/');
        
        // Checks if the request was successful.
        if (!response_tool.ok) {
            throw new Error(`Failed to fetch tool map. Status: ${response.status}`);
        }

        // Window.tools is a map of tool ids to tool names.
        window.tools = await response_tool.json();

        for (let tool of tools) {
        // Adds a row for each tool.
        add_tool_display_row(tool, recipe_id);
        }
        document.getElementById("edit_tools_popup").style.display = "block";
        document.getElementById("update-form-tools").addEventListener('submit', (event) => {
            update_tools(event, recipe_id);
        });    
    } catch (error) {
        // Log any errors to the console.
        console.error('Error fetching tools:', error);
    }
}

async function create_list_tools(recipe_id) {
    try {
        // Adding an empty row to be filled in by the user.
        add_tool_display_row('', recipe_id, true);

        document.getElementById("edit_tools_popup").style.display = "block";
        document.getElementById("update-form-tools").addEventListener('submit', (event) => {
            add_tools(event, recipe_id);
        });    
    } catch (error) {
        // Logs any errors to the console.
        console.error('Error fetching tools:', error);
    }
}

function add_tool_display_row(tool_id, recipe_id, add = false) {
    const row = document.createElement("div");
    row.className = "tool-row";

    // If the user is adding the format of the form is slightly altered.
    if (add) {
        row.innerHTML = `
        <input type="text" name="tools[]" placeholder="Tools" id="Tools" required value="${""}">
        <br>
        <input type="hidden" name="recipe-id" placeholder="recipe-id" required value="${recipe_id}">
        <button type="button" onclick="if (remove_conditional(this)">X</button>
    `;
    } else {
    // Displays information and creates button which removes tool on click.
    row.innerHTML = `
        <label for "Tools">${window.tools[tool_id]}</label>
        <input type="text" name="tools[]" placeholder="Tools" id="Tools" required value="${tool_id}">
        <br>
        <input type="hidden" name="recipe-id" placeholder="recipe-id" required value="${recipe_id}">
        <button type="button" onclick="if (remove_conditional(this)">X</button>
    `;
    }
    document.getElementById("tools_list_container").appendChild(row);
}

// Closes the recipe tools popup.
function close_edit_tools_popup() {
    document.getElementById("edit_tools_popup").style.display = "none";
    location.reload();
}

async function update_tools(event) {
    event.preventDefault();

    // Recreates the form.
    const form = event.target;
    const formData = new FormData(form);
    
    // Fetches the flask route to update the tools in the database.
    const response = await fetch('/admin/item_view/update_recipe_tools', {
             method: 'POST',
             body: formData,
    });
     
    // Waits until result is recieved.
    const result = await response.json();
     
    if (result.success) {
        close_edit_tools_popup();
    } else {
        alert('There was an error updating the item.');
    }
}

async function add_tools(event) {
    event.preventDefault();

    // Recreates the form.
    const form = event.target;
    const formData = new FormData(form);
    
    // Fetches the flask route for adding tools to the database.
    const response = await fetch('/admin/item_view/add_recipe_tools', {
             method: 'POST',
             body: formData,
    });
     
    // Waits until result is recieved.
    const result = await response.json();
     
    if (result.success) {
        close_edit_tools_popup();
    } else {
        alert('There was an error updating the item.');
    }
}

function remove_conditional(button) {
    const parent = button.parentElement;
    const container = parent.parentElement;

    // Can only remove a text field if there is more than 1.
    if (container.children.length > 1) {
        parent.remove();
    }
}