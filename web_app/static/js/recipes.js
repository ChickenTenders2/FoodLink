//      DISPLAY RECIPE POPUP FUNCTIONS

function open_recipe_popup(recipe) {
    display_information(recipe);

    // sets recipe to be used if user creates recipe
    document.getElementById("create_recipe").onclick = () => open_ingredients_overview(recipe);

    // allow editing options if recipe is a users
    if (recipe.personal) {
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
            const delete_button = document.getElementById("delete_recipe");
            
            // switches to cancel edit button if edit mode is entered (edit recipe is pressed)
            if (is_editing) {
                edit_button.innerText = "Cancel Edit";

                //lets content be editable and shows buttons
                toggle_edit_features(true);
                
                //shows delete button
                delete_button.style.display = "inline-block";

            // cancels edits and switches buttons back to be hidden
            } else {
                // if cancel button is pressed, reload the original information
                display_information(recipe);
                // make sure edit popups are closed
                close_edit_ingredients_popup();
                close_edit_tools_popup();

                //stops content being editable and hides buttons
                toggle_edit_features(false);
                
                edit_button.innerText = "Edit Recipe";
    
                //hides delete button
                delete_button.style.display = "none";
            }
            delete_button.onclick = () => delete_recipe(recipe.id);
            // sets save recipe button to update recipe with id
            document.getElementById("save_recipe").onclick = () => update_recipe(recipe.id);
        };
    }
    
    document.getElementById("recipe_popup").style.display = "block";
}

function open_create_recipe_popup() {
    // creates empty recipe and displays it
    const recipe = {
        "name": "",
        "instructions": "",
        "servings": "",
        "prep_time": "",
        "cook_time": "",
        "tool_ids": [],
        "missing_tool_ids": [],
        "ingredients": []
    }
    display_information(recipe);
    // shows edit buttons
    toggle_edit_features(true);
    // sets save button to add recipe
    document.getElementById("save_recipe").onclick = () => add_recipe();
    document.getElementById("recipe_popup").style.display = "block";

    // change close button to functionality for closing add popup
    const close_button = document.getElementById("close_recipe_popup");
    close_button.onclick = () => {
        toggle_edit_features(false);
        document.getElementById("recipe_popup").style.display = "none";
        // changes it back to orginal function after closing
        close_button.onclick = () => close_recipe_popup();
    }
}

function toggle_edit_features(show) {
    const title_input = document.getElementById("recipe_popup_title");
    const edit_ingredients = document.getElementById("edit_ingredients");
    const edit_tools = document.getElementById("edit_tools");
    const save_recipe = document.getElementById("save_recipe");
    const instructions_box = document.getElementById("recipe_popup_instructions");
    const servings = document.getElementById("recipe_popup_servings");
    const prep_time = document.getElementById("recipe_popup_prep");
    const cook_time = document.getElementById("recipe_popup_cook");
    if (show) {
        edit_ingredients.style.display = "inline-block";
        edit_tools.style.display = "inline-block";
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
    } else {
        edit_ingredients.style.display = "none";
        edit_tools.style.display = "none";
        save_recipe.style.display = "none";
        
        // stops information being editable
        instructions_box.contentEditable = false;
        servings.readOnly = true;
        prep_time.readOnly = true;
        cook_time.readOnly = true;
        title_input.readOnly = true;

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
        // stops null values from being added to tools
        if (dropdown.value) {
            const selected_id = parseInt(dropdown.value);
            add_tool_display_row(selected_id, dropdown);
            // makes sure the now hidden tool is not selected still
            dropdown.value = null;
        }
    };

    addContainer.appendChild(dropdown);
    addContainer.appendChild(addButton);

    // displays initial tools for recipe
    for (let id of tool_ids) {
        add_tool_display_row(id, dropdown);
    }
    // deselects so a hidden tool cant accidentally be added
    dropdown.value = null;

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
}

async function get_tools() {
    const response = await fetch("/tools/get")
    const result = await response.json();
    if (result.success) {
        return result.tools;
    } 
}

// INGREDIENT OVERVIEW FUNCTIONS

async function open_ingredients_overview(recipe) {
    const popup = document.getElementById("ingredient_overview_popup");
    const container = document.getElementById("ingredient_scroll_container");
    container.innerHTML = "";

    window.recipe_ingredients = recipe.ingredients;
    window.inventory_ingredients = recipe.inventory_ingredients;

    for (let i = 0; i < recipe.ingredients.length; i++) {
        const [name, quantity, unit, status] = recipe.ingredients[i];

        const block = document.createElement("div");
        block.className = "ingredient-block";

        const ingredient_info = document.createElement("div");
        ingredient_info.innerHTML = `<strong>${name} - ${quantity} ${unit}:</strong>`;
        block.appendChild(ingredient_info);

        if (!(status == "missing")) {
            const inventory_item = await add_inventory_ingredient(i);
            block.appendChild(inventory_item);
        } else {
            block.appendChild(createAddButton(i));
        }

        container.appendChild(block);
    }
    // adds div to store additional ingredients
    const additional_block = document.createElement("div");
    additional_block.id = "additional-ingredients";
    // adds text to show what div is for
    const additional_add = document.createElement("div");
    additional_add.innerHTML = `<strong>Additional ingredients:</strong>`;
    additional_block.appendChild(additional_add);
    container.appendChild(additional_block);
    container.appendChild(createAddButton());

    popup.style.display = "block";
}

async function add_inventory_ingredient(i, additional = false) {
    let inventory_item = await create_item_tile(window.inventory_ingredients[i]);
    inventory_item.className = "inventory-match";
    const invQty = window.inventory_ingredients[i][4];
    const usedQty = document.createElement("input");
    usedQty.type = "number";
    usedQty.min = 1;
    usedQty.max = invQty;
    if (!additional) {
        usedQty.value = Math.min(invQty, parseFloat(window.recipe_ingredients[i][1])); // default to ingredient quantity
    } else {
        usedQty.value = invQty;
    }
    usedQty.className = "used-quantity-input";
    usedQty.title = "Quantity to use from inventory";

    inventory_item.appendChild(usedQty);

    // remove button, shows add button once pressed so different item can be selected
    const remove_button = document.createElement("button");
    remove_button.innerText = "X";
    remove_button.onclick = () => {
        // clear item from list
        if (!additional) {
            window.inventory_ingredients[i] = [];
            // replaces the item with an add button
            const add_button = createAddButton(i);
            inventory_item.parentElement.replaceChild(add_button, inventory_item);
        } else {
            // removes item from list
            window.inventory_ingredients.splice(i, 1);
            // removes item from screen
            inventory_item.remove();
        }
    };
    inventory_item.appendChild(remove_button);
    return inventory_item;
}

async function create_item_tile(item) {
    const [ , item_id, name, brand, quantity, unit, expiry_date] = item;
    // only items in inventory are stored in list, so only increments if not missing
    const item_tile = document.createElement("div");
    const image_path = await get_image_path(item_id);
    let brand_text = "";
    if (brand) {
        brand_text = `(${brand})`;
    }
    item_tile.innerHTML = `
    <img src="${image_path}" alt="${name}" class="item_img">
    <div class="item_info">
        ${name} ${brand_text} - ${quantity} ${unit}
        <br>
        (${expiry_date})
    </div>`;
    return item_tile;
}

function createAddButton(i = null) {
    const wrapper = document.createElement("div");
    wrapper.className = "inventory-placeholder";

    const addBtn = document.createElement("button");
    addBtn.innerText = "+ Add from Inventory";
    addBtn.onclick = () => {
        inventory_selector(i, wrapper);
    };

    wrapper.appendChild(addBtn);
    return wrapper;
}

async function inventory_selector(i, tile) {
    //const searchParam = document.getElementById("selector-search-input").value || "";
    const searchParam = "";

    const response = await fetch("/inventory/get/" + searchParam);
    const result = await response.json();

    if (result.success) {
        document.getElementById("select_inventory_popup").style.display = "block";
        const container = document.getElementById("inventory_items_scroll");
        container.innerHTML = "";
        //console.log(result.items)
        for (let item of result.items) {
            const item_tile = await create_item_tile(item);
            item_tile.className = "inventory-tile";
            // for filtering
            item_tile.dataset.name = item[2];
            item_tile.onclick = async () => {
                const inv_id = item[0];
                const expiry = new Date(item[6]);
                const now = new Date();

                // makes sure item is not expired
                if (expiry < now) {
                    alert("This item is expired and cannot be added.");
                    return;
                }

                // makes sure item is not already added
                const is_duplicate = window.inventory_ingredients.some(
                    (existing) => existing[0] === inv_id
                );

                if (is_duplicate) {
                    alert("This inventory item has already been added.");
                    return;
                }

                if (i == null) {
                    // appends additional item
                    window.inventory_ingredients.push(item);
                    // gets indexed of newly appended item
                    i = window.inventory_ingredients.length - 1;
                    console.log(window.inventory_ingredients);
                    console.log(i);
                    const inventory_item = await add_inventory_ingredient(i, true);
                    // adds item to bottom of list
                    document.getElementById("additional-ingredients").appendChild(inventory_item);
                    close_inventory_selector();
                } else {
                    // updates list
                    window.inventory_ingredients[i] = item;
                    // replaces the add button with the item
                    const inventory_item = await add_inventory_ingredient(i);
                    tile.parentElement.replaceChild(inventory_item, tile);
                    close_inventory_selector();
                }
            }
            container.appendChild(item_tile);
        }
    } else {
      alert(result.error);
    }
}

function close_inventory_selector() {
    document.getElementById("select_inventory_popup").style.display = "none";
}

function close_ingredient_overview() {
    document.getElementById("ingredient_overview_popup").style.display = "none";
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
        div.classList.add("recipe-card");
        div.innerHTML = `
            <h3>${recipe.name} ${recipe.personal ? "(Personal)" : ""}</h3>
            <div class="recipe-meta">
            <p><span class="icon">🍽️</span><strong>Servings:</strong> ${recipe.servings}</p>
            <p><span class="icon">🕑</span><strong>Prep Time:</strong> ${recipe.prep_time} mins</p>
            <p><span class="icon">🔥</span><strong>Cook Time:</strong> ${recipe.cook_time} mins</p>
            </div>
        `;
        div.onclick = () => open_recipe_popup(recipe);
        container.appendChild(div);
    }
}


// STORING PERSONAL RECIPE FUNCTIONS

// gets all data needed to update/add recipe
function get_recipe_form() {
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
    formData.append("servings", servings);
    formData.append("prep_time", prep_time);
    formData.append("cook_time", cook_time);
    formData.append("instructions", instructions);
    // formdata converts to list to string so stringify so it can be loaded server side
    formData.append("ingredients", JSON.stringify(ingredients));
    formData.append("tool_ids", JSON.stringify(tool_ids));

    return formData;
}

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

// SEARCH FORM HANDLING

// preserves checked boxes on page reload
document.addEventListener("DOMContentLoaded", () => {
    const checkboxes = ["personal_only", "missing_items", "insufficient_items", "missing_tools"];

    checkboxes.forEach(id => {
        const box = document.getElementById(id);
        if (box) {
            // Restore saved state
            const saved = localStorage.getItem(id);
            if (saved !== null) {
                box.checked = saved === "true";
            }

            // Save on change
            box.addEventListener("change", () => {
                localStorage.setItem(id, box.checked);
            });
        }
    });
});

// toggles the visibility of the recipe search filters via the Filter button
document.getElementById('filter-toggle').addEventListener('click', () => {
    const filters = document.getElementById('filter-options');
    const toggleBtn = document.getElementById('filter-toggle');

    if (filters.style.display == 'none') {
      filters.style.display = 'block';
      toggleBtn.textContent = 'Hide Filters';
    } else {
      filters.style.display = 'none';
      toggleBtn.textContent = 'Show Filters';
    }
})