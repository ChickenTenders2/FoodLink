//      DISPLAY RECIPE POPUP FUNCTIONS

function open_recipe_popup(recipe) {
    display_information(recipe);

    // allow editing options if recipe is a users
    if (recipe.personal) {
        const title_input = document.getElementById("recipe_popup_title");
        const edit_button = document.getElementById("toggle_edit");
        edit_button.style.display = "inline-block";
    
        edit_button.onclick = () => {
            //gets editing value
            let is_editing = edit_button.value == "true";
            //toggles it
            is_editing = !is_editing;
            // sets new value
            edit_button.value = is_editing;
    
            // gets hidden buttons
            const edit_ingredients = document.getElementById("edit_ingredients");
            const edit_tools = document.getElementById("edit_tools");
            const delete_button = document.getElementById("delete_recipe");
            const save_recipe = document.getElementById("save_recipe");
            const instructions_box = document.getElementById("recipe_popup_instructions");
            const servings = document.getElementById("recipe_popup_servings");
            const prep_time = document.getElementById("recipe_popup_prep");
            const cook_time = document.getElementById("recipe_popup_cook");
            
            // switches to cancel edit button if edit mode is entered (edit recipe is pressed)
            if (is_editing) {
                edit_button.innerText = "Cancel Edit";
                
                //shows edit buttons
                edit_ingredients.style.display = "inline-block";
                edit_tools.style.display = "inline-block";
                delete_button.style.display = "inline-block";
                save_recipe.style.display = "inline-block";
                
                // makes information editable
                instructions_box.contentEditable = true;
                servings.readOnly = false;
                prep_time.readOnly = false;
                cook_time.readOnly = false;
                title_input.readOnly = false;
                
                // css styling to show now now editable
                title_input.style.backgroundColor = "#fff9db";
                title_input.style.border = "1px dashed #ccc";
                instructions_box.style.border = "1px dashed #ccc";
                instructions_box.style.backgroundColor = "#fff9db";
                servings.style.border = "1px dashed #ccc";
                prep_time.style.border = "1px dashed #ccc";
                cook_time.style.border = "1px dashed #ccc";
                servings.style.backgroundColor = "#fff9db";
                prep_time.style.backgroundColor = "#fff9db";
                cook_time.style.backgroundColor = "#fff9db";
            // cancels edits and switches buttons back to be hidden
            } else {
                // if cancel button is pressed, reload the original information
                display_information(recipe);
                // make sure edit popups are closed
                close_edit_ingredients_popup();
                close_edit_tools_popup();

                edit_button.innerText = "Edit Recipe";
    
                edit_ingredients.style.display = "none";
                edit_tools.style.display = "none";
                delete_button.style.display = "none";
                save_recipe.style.display = "none";
                
                // stops information being editable
                instructions_box.contentEditable = false;
                servings.readOnly = true;
                prep_time.readOnly = true;
                cook_time.readOnly = true;
                title_input.readOnly = true;
                title_input.value = recipe.name; // reset if cancel

                // resets styling
                title_input.style.border = "";
                title_input.style.backgroundColor = "";
                instructions_box.style.border = "";
                instructions_box.style.backgroundColor = "";
                servings.style.border = "";
                prep_time.style.border = "";
                cook_time.style.border = "";
                servings.style.backgroundColor = "";
                prep_time.style.backgroundColor = "";
                cook_time.style.backgroundColor = "";
            }
            delete_button.onclick = () => delete_recipe(recipe.id);
            save_recipe.onclick = () => save_full_recipe(recipe.id);
        };
    }
    
    document.getElementById("recipe_popup").style.display = "block";
}

function close_recipe_popup() {
    // if still in edit mode, simulate click to cancel changes when closing recipe
    // this hides modify buttons and closes popups, plus makes inputs readonly
    const edit_button = document.getElementById("toggle_edit");
    if (edit_button.value == "true") {
        edit_button.click();
    }
    // makes sure edit button is hidden aswell
    edit_button.style.display = "none";

    document.getElementById("recipe_popup").style.display = "none";
}

//shows all the recipe information
function display_information(recipe) {
    document.getElementById("recipe_popup_title").value = recipe.name;
    document.getElementById("recipe_popup_servings").value = recipe.servings;
    document.getElementById("recipe_popup_prep").value = recipe.prep_time;
    document.getElementById("recipe_popup_cook").value = recipe.cook_time;
    document.getElementById("recipe_popup_instructions").innerText = recipe.instructions;
    
    display_ingredients(recipe.ingredients);
    display_tools(recipe.tool_ids, recipe.missing_tool_ids)

}

function display_ingredients(ingredients) {
    // incase recipe is personal and user wants to edit recipe 
    // make sure the newest ingredients are the ones displayed in the edit popup
    const edit_ingredients = document.getElementById("edit_ingredients");
    edit_ingredients.onclick = () => open_edit_ingredients_popup(ingredients);

    // fill ingredients list
    const ingredients_list = document.getElementById("recipe_popup_ingredients");
    ingredients_list.innerHTML = "";
    for (let ingredient of ingredients) {
        // gets ingredient values
        const [name, quantity, unit, status] = ingredient;

        // creates list element
        const li = document.createElement("li");

        // displays information
        li.innerText = `${name} - ${quantity} ${unit}`;

        // stores values directly in the element
        li.dataset.name = name;
        li.dataset.quantity = quantity;
        li.dataset.unit = unit;

        // highlights the ingredient red if missing, or yellow if insufficient quantity
        if (status === "missing") {
            li.classList.add("missing-ingredient");
        } else if (status === "insufficient") {
            li.classList.add("insufficient-ingredient");
        }
    
        ingredients_list.appendChild(li);
    }
}

function display_tools(tool_ids, missing_tool_ids) {
    // incase recipe is personal and user wants to edit recipe 
    // make sure the newest tools are the ones displayed in the edit popup
    const edit_tools = document.getElementById("edit_tools");
    edit_tools.onclick = () => open_edit_tools_popup(tool_ids);
    

    const tools_list = document.getElementById("recipe_popup_tools");
    tools_list.innerHTML = "";
    // for each tool
    for (let tool_id of tool_ids) {
        // create list element
        const li = document.createElement("li");
        // get the tool name from the tools dictionary
        tool_name = window.tools_dict[parseInt(tool_id)];
        li.innerText = tool_name;
        li.value = tool_id;
        // highlights tool red if missing
        if (missing_tool_ids && missing_tool_ids.includes(tool_id)) {
            li.classList.add("missing-tool");
        }
        tools_list.appendChild(li);
    }
}


//       EDIT INGREDIENTS FUNCTIONS

function open_edit_ingredients_popup(ingredients) {
    // make sure other popup closed
    close_edit_tools_popup();

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

//          EDIT TOOLS FUNCTIONS

function open_edit_tools_popup(tool_ids) {
    // make sure other popup closed
    close_edit_ingredients_popup();

    const container = document.getElementById("tools_list_container");
    container.innerHTML = "";

    const addContainer = document.getElementById("tool_add_controls");
    addContainer.innerHTML = "";

    // creates the selection dropdown
    const dropdown = document.createElement("select");
    dropdown.id = "tool_selector";

    // adds options that are not in tool_ids (tool_ids are unique and shouldnt be added twice)
    for (let [tool_id, tool_name] of window.tools) {
        const option = document.createElement("option");
        option.value = tool_id;
        option.innerText = tool_name;
        dropdown.appendChild(option);
    }

    // adds button to add selected from dropdown 
    const addButton = document.createElement("button");
    addButton.innerText = "+ Add Tool";
    addButton.onclick = () => {
        const selected_id = parseInt(dropdown.value);
        add_tool_display_row(selected_id, dropdown);
        dropdown.value = "";
    };

    addContainer.appendChild(dropdown);
    addContainer.appendChild(addButton);

    // displays initial tools for recipe
    for (let id of tool_ids) {
        add_tool_display_row(id, dropdown);
    }
    dropdown.value = "";

    document.getElementById("edit_tools_popup").style.display = "block";
}

function close_edit_tools_popup() {
    document.getElementById("edit_tools_popup").style.display = "none";
}

function add_tool_display_row(tool_id, dropdown) {
    const container = document.getElementById("tools_list_container");
    const row = document.createElement("div");
    row.className = "tool-row";

    // adds tool name to row
    const tool_name = window.tools_dict[tool_id];
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
        // unhides option in dropdown
        const option = dropdown.querySelector(`option[value="${tool_id}"]`);
        if (option) {
            option.hidden = false;
        }
    };

    row.appendChild(remove_button);
    container.appendChild(row);

    // hides option from dropdown
    const option_to_hide = dropdown.querySelector(`option[value="${tool_id}"]`);
    option_to_hide.hidden = true;
}

function update_tools() {
    const rows = document.querySelectorAll("#tools_list_container .tool-row span");
    const tool_ids = [];
    // gets tool_id from each row and adds it to array
    for (let row of rows) {
        const tool_id = parseInt(row.value);
        tool_ids.push(tool_id);
    }

    display_tools(tool_ids);
    close_edit_tools_popup();
}


window.onload = async function() {
    // gets tools with ordering by type, name
    // so appliances are shown a > z with utensils below also shown a > z
    window.tools = await get_tools();
    // makes tool dictionary with (key = id, value = tool name)
    // used to find name of tool_id
    window.tools_dict = {};
    for (const [id, name] of window.tools) {
        window.tools_dict[id] = name;
    }
    console.log(window.tools_dict)
}

async function get_tools() {
    const response = await fetch("/tools/get")
    const result = await response.json();
    if (result.success) {
        return result.tools;
    } 
}

// MAIN RECIPE LIST FUNCTIONS

function change_page(amount) {
    const page = parseInt(document.getElementById("page_number").value);
    const new_page = page + amount;

    // page cant go below 1
    if (new_page < 1) {
        return;
    }
    document.getElementById("page_number").value = new_page;
    document.getElementById("current_page").innerText = `Page ${new_page}`;
    // Gets recipes with the new page number
    get_recipes()
}

async function get_recipes(event) {
    //if called from submit form
    if (event) {
        event.preventDefault(); 
    }

    const form = document.getElementById("recipe-search-form");
    const formData = new FormData(form);

    const response = await fetch("/recipes/get", {
        method: "POST",
        body: formData
    });

    const result = await response.json();
    if (result.success) {
        display_recipe_results(result.recipes);
    } else {
        alert("Error: " + result.error);
    }
}

function display_recipe_results(recipes) {
    const container = document.getElementById("recipe_results");
    container.innerHTML = "";

    // display if no recipes are found
    if (recipes.length == 0) {
        container.innerHTML = "<p>No recipes found.</p>";
        return;
    }

    // for each recipe add a element with the information
    for (const recipe of recipes) {
        const div = document.createElement("div");
        div.innerHTML = `
            <h3>${recipe.name} ${recipe.personal ? "(Personal)" : ""}</h3>
            <p>Servings: ${recipe.servings}</p>
            <p>Prep Time: ${recipe.prep_time} mins</p>
            <p>Cook Time: ${recipe.cook_time} mins</p>
        `;
        div.onclick = () => open_recipe_popup(recipe);
        container.appendChild(div);
    }
}


// UPDATE PERSONAL RECIPE FUNCTIONS


// gets the ingredient list elements and extracts the values into a list
function get_ingredients_from_list() {
    const ingredient_elements = document.querySelectorAll("#recipe_popup_ingredients li");
    const ingredients = [];
    for (let li of ingredient_elements) {
        ingredients.push([
            li.dataset.name,
            li.dataset.quantity,
            li.dataset.unit
        ])
    }
    return ingredients;
}

// gets the tools list elements and extracts the values into a list
function get_tool_ids_from_list() {
    const tool_elements = document.querySelectorAll("#recipe_popup_tools li");
    const tool_ids = [];
    for (let li of tool_elements) {
        tool_ids.push(li.value);
    }
    return tool_ids;
}

async function save_full_recipe(recipe_id) {
    const name = document.getElementById("recipe_popup_title").value.trim();
    const instructions = document.getElementById("recipe_popup_instructions").innerText.trim();
    const servings = document.getElementById("recipe_popup_servings").value;
    const prep_time = document.getElementById("recipe_popup_prep").value;
    const cook_time = document.getElementById("recipe_popup_cook").value;

    // gets values from the list elements
    const ingredients = get_ingredients_from_list();
    const tool_ids = get_tool_ids_from_list();

    const formData = new FormData();
    formData.append("name", name);
    formData.append("recipe_id", recipe_id);
    formData.append("servings", servings);
    formData.append("prep_time", prep_time);
    formData.append("cook_time", cook_time);
    formData.append("instructions", instructions);
    // formdata converts to list to string so stringify so it can be loaded server side
    formData.append("ingredients", JSON.stringify(ingredients));
    formData.append("tool_ids", JSON.stringify(tool_ids));

    const response = await fetch("/recipes/update", {
        method: "POST",
        body: formData
    });

    const result = await response.json();

    if (result.success) {
        alert("Recipe updated successfully.");
        close_recipe_popup();
        get_recipes(); // Refresh list
    } else {
        alert("Error saving recipe: " + result.error);
    }
}

async function delete_recipe(recipe_id) {
    const confirm_delete = confirm("Are you sure you want to delete this recipe?");
    if (!confirm_delete) {
        return;
    }
    const response = await fetch("/recipes/delete/" + recipe_id)
    const result = await response.json();
    if (result.success) {
        alert("Recipe deleted.");
        close_recipe_popup();
        get_recipes();
    } else {
        alert("Error deleting recipe:" + result.error);
    }
}