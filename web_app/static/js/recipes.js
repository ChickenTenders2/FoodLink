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
        div.className = "recipe-tile";
        div.innerHTML = `
            <h3>${recipe.name} ${recipe.personal ? "(Personal)" : ""}</h3>
            <p>Servings: ${recipe.servings}</p>
            <p>Prep Time: ${recipe.prep_time} mins</p>
            <p>Cook Time: ${recipe.cook_time} mins</p>
        `;
        container.appendChild(div);
    }
}