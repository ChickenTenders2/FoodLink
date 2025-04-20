function open_recipe_popup(recipe) {
    document.getElementById("recipe_popup_title").innerText = recipe.name;
    document.getElementById("recipe_popup_servings").innerText = recipe.servings;
    document.getElementById("recipe_popup_prep").innerText = recipe.prep_time;
    document.getElementById("recipe_popup_cook").innerText = recipe.cook_time;

    // Populate ingredients
    const ingredientsList = document.getElementById("recipe_popup_ingredients");
    ingredientsList.innerHTML = "";
    for (let ingredient of recipe.ingredients) {
        const li = document.createElement("li");
        li.innerText = `${ingredient[0]} - ${ingredient[1]} ${ingredient[2]}`;
    
        // Ingredient status is stored in index 3 (e.g., "missing", "insufficient", "matched")
        const status = ingredient[3];
    
        if (status === "missing") {
            li.classList.add("missing-ingredient");
        } else if (status === "insufficient") {
            li.classList.add("insufficient-ingredient");
        }
    
        ingredientsList.appendChild(li);
    }

    // Populate tools
    const toolsList = document.getElementById("recipe_popup_tools");
    toolsList.innerHTML = "";
    for (let tool_id of recipe.tool_ids) {
        const li = document.createElement("li");
        tool_name = window.tools[parseInt(tool_id)];
        li.innerText = tool_name;
        if (recipe.missing_tool_ids.includes(tool_id)) {
            li.classList.add("missing-tool");
        }
        toolsList.appendChild(li);
    }

    const instructionsBox = document.getElementById("recipe_popup_instructions");
    instructionsBox.innerText = recipe.instructions;

    document.getElementById("recipe_popup").style.display = "block";
}

function close_recipe_popup() {
    document.getElementById("recipe_popup").style.display = "none";
}

function change_page(amount) {
    const page = parseInt(document.getElementById("page_number").value);

    const new_page = page + amount;
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

    if (recipes.length == 0) {
        container.innerHTML = "<p>No recipes found.</p>";
        return;
    }

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

window.onload = async function() {
    window.tools = await get_tools();
}

async function get_tools() {
    const response = await fetch("/tools/get")
    const result = await response.json();
    if (result.success) {
        return result.tools;
    } 
}