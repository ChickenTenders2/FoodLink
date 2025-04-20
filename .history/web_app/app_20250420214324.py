from flask import Flask, jsonify, render_template, request, url_for, Response
from item import item_table
from recipe import Recipe
from input_handling import InputHandling
from flask_session import Session
import json
app = Flask(__name__, template_folder = "templates")
app.config["SESSION_PERMANENT"] = False     
app.config["SESSION_TYPE"] = "filesystem"

# Initialize Flask-Session
Session(app)

# session["user"] = (get the user id)
# session["user"] = (get the user type (admin or client))

# Item table interface
@app.route('/admin/item_view')
def get_items():
    # Splits the list of items into several pages.
    item_list = item.get_all()
    current_page = []
    items = []
    for index, row in enumerate(item_list, start = 1):
        if index % 30 == 0:
            items.append(current_page)
            current_page = []
        else:
            current_page.append(row)
    items.append(current_page)
    max = len(items) - 1
    return render_template("item_view.html", items = items[0], max = max)

# allows for no search query to be entered
@app.route('/admin/item_view/get', defaults={'search_query': None})
@app.route('/admin/item_view/get/<search_query>')
def search_items(search_query = None):
        # Checks if the search is for a specifc page.
        if search_query.isnumeric():
                item_list = item.get_all()
                current_page = []
                items = []
                for index, row in enumerate(item_list, start = 1):
                    if index % 30 == 0:
                        items.append(current_page)
                        current_page = []
                    else:
                        current_page.append(row)
                items.append(current_page)
                max = len(items) - 1
                return render_template("item_view.html", items = items[int(search_query)], max = max)
        else:
            # searches for an item if query is provided otherwise gets all items.
            result = item.get_item_from_name(search_query)
            if result != [None]:
                return render_template("item_view_search.html", items = result)
            else:
                result = item.get_all()
                return render_template("item_view_search.html", items = [])
        
# Recipe table interface
@app.route('/admin/recipe_view')
def get_recipes():
    recipes = recipe.get_all()
    return render_template("recipe_view.html", recipes = recipes)

@app.route("/recipes/update", methods=["POST"])
def update_recipe():
    try:
        recipe_id = request.form.get("recipe_id")
        name = request.form.get("name")
        ingredients = request.form.get("ingredients")
        servings = request.form.get("servings")
        prep_time = request.form.get("prep_time")
        cook_time = request.form.get("cook_time")
        instructions = request.form.get("instructions")
        
        ingredients_string = request.form.get("ingredients")
        tool_ids_string = request.form.get("tool_ids")

        if not (ingredients or tool_ids):
            return jsonify({"success": False, "error": "ingredients or tool were empty."})
        
        # list variables must be stringified client side so lists transfer correctly
        # they are so decoded to get original data type back
        ingredients = json.loads(ingredients_string)
        tool_ids = json.loads(tool_ids_string)

        print(ingredients)
        print(tool_ids)

        # performs update functions
        #### WHEN REMOVING OOP MAKE SURE TO USE SINGLE CURSOR AND COMMIT FOR THESE FUNCTIONS
        recipe.edit_recipe(recipe_id, name, servings, prep_time, cook_time, instructions)
        print("updated recipe")
        recipe.edit_recipe_items(recipe_id, ingredients)
        print("updated recipe_items")
        recipe.edit_recipe_tools(recipe_id, tool_ids)
        print("updated recipe_tools")

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Recipe table interface
@app.route('/admin/recipe_view/edit', defaults={'id': None})
@app.route('/admin/recipe_view/edit/<id>', methods = ['GET', 'POST'])
def get_tools_items(id):
    tools = recipe.get_tools(id)
    items = recipe.get_recipe_items(id)
    return render_template("recipe_view_edit.html", tools = tools, items=items)

# Removes an item from the item table.
@app.route('/admin/item_view/delete', methods = ['POST'])
def delete_item():
    try:
        # Form data is formatted in utf-8 so it needs to be decoded.
        id = request.data.decode('utf-8')
        item.remove_item(id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Updates the details of a selected item in the item table.
@app.route('/admin/item_view/update_item', methods = ['POST'])
def update_item_admin(): 
    # Sanitise the input to prevent sql injection.
    sanitised_fields = input_check.sanitise_all(['name', 'brand', 'quantity', 
                                                'expiry', 'unit'])
    inventory_id = request.form['inventory_id']
    name = sanitised_fields[0]
    brand = sanitised_fields[1]
    quantity = sanitised_fields[2]
    expiry_date = sanitised_fields[3]
    unit = sanitised_fields[4]
    barcode = request.form['barcode']
    if barcode == "None":
        barcode = None
    # Checks that the format is correct for the expiry date.
    valid = input_check.validate_expiry(expiry_date)
    if valid:
        try:
            item.update_item(inventory_id, barcode, name, brand, expiry_date, quantity, unit)
            return jsonify({'success': True})
        except Exception as e:
            print(e)
            return jsonify({'success': False, 'error': str(e)})
    else:
         return jsonify({'success': False, 'error': str("Expiry formatted incorrectly")})

# Updates the details of a selected recipe in the recipe table.
@app.route('/admin/item_view/update_recipe', methods = ['POST'])
def update_recipe_admin():
    # Sanitise the input to prevent sql injection.
    sanitised_fields = input_check.sanitise_all(['name', 'instructions', 
                                                'prep', 'cook', 'servings'])
    name = sanitised_fields[0]
    instructions = sanitised_fields[1]
    recipe_id = request.form['recipe-id']
    prep = sanitised_fields[2]
    cook = sanitised_fields[3]
    servings = sanitised_fields[4]
    try:
        recipe.update_recipe(recipe_id, name, servings, prep, cook, instructions)
        return jsonify({'success': True})
    except Exception as e:
        print(e)
        return jsonify({'success': False, 'error': str(e)})

# Adds a new item to the item table.
@app.route('/admin/item_view/add_item', methods = ['POST'])
def add_item_admin():
    # Sanitise the input to prevent sql injection.
    sanitised_fields = input_check.sanitise_all(['name', 'brand', 'quantity', 
                                                'expiry', 'unit', 'barcode'])
    name = sanitised_fields[0]
    brand = sanitised_fields[1]
    quantity = sanitised_fields[2]
    expiry_date = sanitised_fields[3]
    unit = sanitised_fields[4]
    barcode = sanitised_fields[5]
    # Barcodes and user ids can be empty. 
    if barcode == "":
        barcode = None
    # Checks that the format is correct for the expiry date.
    valid = input_check.validate_expiry(expiry_date)
    if valid:
        try:
            item.add_item(barcode, name, brand, expiry_date, quantity, unit)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    else:
         return jsonify({'success': False, 'error': str("Expiry formatted incorrectly.")})

# Adds a new recipe to the recipe table.   
@app.route('/admin/recipe_view/add_item', methods = ['POST'])
def add_recipe_admin():
    # Sanitise the input to prevent sql injection.
    sanitised_fields = input_check.sanitise_all(['name', 'instructions', 
                                                'prep', 'cook', 'servings'])
    name = sanitised_fields[0]
    instructions = sanitised_fields[1]
    prep = sanitised_fields[2]
    cook = sanitised_fields[3]
    servings = sanitised_fields[4]
    if user == "":
        user = None
    try:
        recipe.add_recipe(name, servings, prep, cook, instructions)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # Classes for handling sql expressions
    input_check = InputHandling()
    item = item_table()
    recipe = Recipe()
    app.run(debug=True)