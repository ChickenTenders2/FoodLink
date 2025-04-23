from flask import Flask, jsonify, render_template, request, url_for, Response
from item import item_table
from recipe import Recipe
from input_handling import InputHandling
from flask_session import Session

app = Flask(__name__, template_folder = "templates")

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
                # Splits the items so that 30 are displayed per page.
                for index, row in enumerate(item_list, start = 1):
                    if index % 30 == 0:
                        items.append(current_page)
                        current_page = []
                    else:
                        current_page.append(row)
                items.append(current_page)
                max = len(items) - 1
                # Renders the page with the given index query.
                return render_template("item_view.html", items = items[int(search_query)], max = max)
        else:
            # Searches for an item if query is provided otherwise gets all items.
            result = item.get_item_from_name(search_query)
            if result != [None]:
                return render_template("item_view_search.html", items = result)
            else:
                result = item.get_all()
                return render_template("item_view_search.html", items = [])
        
# Recipe table interface.
@app.route('/admin/recipe_view')
def get_recipes():
    recipes = recipe.get_all()
    return render_template("recipe_view.html", recipes = recipes)

@app.route('/admin/recipe_view/add_item/<int:recipe_id>', methods=['GET'])
def get_ingredients(recipe_id):
    ingredients = recipe.get_recipe_items(recipe_id)
    return jsonify(ingredients)

@app.route('/admin/recipe_view/get_tools_ids/<int:recipe_id>', methods=['GET'])
def get_tools_ids(recipe_id):
    tools = recipe.get_recipe_tools(recipe_id)
    return jsonify(tools)

# Returns the tools as a dictionary so that names can be mapped to ids in the js code. 
@app.route('/admin/recipe_view/get_tools/', methods=['GET'])
def get_tools():
    tools = recipe.get_tools()
    tools = dict(tools)
    return jsonify(tools)

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
    
# Removes an item from the item table.
@app.route('/admin/recipe_view/delete', methods = ['POST'])
def delete_recipe():
    try:
        # Form data is formatted in utf-8 so it needs to be decoded since id was not submitted in a form.
        id = request.data.decode('utf-8')
        recipe.remove_recipe(id)
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
            return jsonify({'success': False, 'error': str(e)})
    else:
         return jsonify({'success': False, 'error': str("Expiry formatted incorrectly")})
    
# Adds a new item to the database.
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
        return jsonify({'success': False, 'error': str(e)})
    
# Adds the details of a selected recipe in the recipe table.
@app.route('/admin/item_view/add_recipe', methods = ['POST'])
def add_recipe_admin():
    # Sanitise the input to prevent sql injection.
    sanitised_fields = input_check.sanitise_all(['name', 'instructions', 
                                                'prep', 'cook', 'servings'])
    name = sanitised_fields[0]
    instructions = sanitised_fields[1]
    prep = sanitised_fields[2]
    cook = sanitised_fields[3]
    servings = sanitised_fields[4]
    try:
        recipe.add_recipe(name, servings, prep, cook, instructions)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
@app.route('/admin/item_view/update_recipe_ingredients', methods=['POST'])
def update_recipe_ingredients():
    try:
        # Requests lists since the rows are dynamically generated.
        names = request.form.getlist('name[]')
        units = request.form.getlist('unit[]')
        quantities = request.form.getlist('quantity[]')
        recipe_id = request.form['recipe-id']  

        recipe.update_recipe_ingredients(recipe_id, names, units, quantities)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/item_view/add_recipe_ingredients', methods=['POST'])
def add_recipe_ingredients():
    try:
        # Requests lists since the rows are dynamically generated.
        names = request.form.getlist('name[]')
        units = request.form.getlist('unit[]')
        quantities = request.form.getlist('quantity[]')
        recipe_id = request.form['recipe-id']  

        recipe.add_recipe_ingredients(recipe_id, names, units, quantities)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/recipe_view/recipe_id/', methods=['GET'])
def get_recipe_id():
    try:
        id = recipe.get_id()
        return jsonify(id)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/item_view/update_recipe_tools', methods=['POST'])
def update_recipe_tools():
    try:
        tool_ids = request.form.getlist('tools[]')
        recipe_id = request.form['recipe-id']  
        recipe.update_recipe_tools(recipe_id, tool_ids)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
@app.route('/admin/item_view/add_recipe_tools', methods=['POST'])
def add_recipe_tools():
    try:
        tool_ids = request.form.getlist('tools[]')
        recipe_id = request.form['recipe-id']  
        recipe.add_recipe_tools(recipe_id, tool_ids)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # Classes for handling sql expressions
    input_check = InputHandling()
    item = item_table()
    recipe = Recipe()
    app.run(debug=True)