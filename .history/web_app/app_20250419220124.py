from flask import Flask, jsonify, render_template, request, url_for, Response
from item import item_table
from recipe import RecipeTable
from input_handling import InputHandling
app = Flask(__name__, template_folder = "templates")

# Item table interface
@app.route('/admin/item_view')
def get_items():
    items = item.get_all()
    return render_template("item_view.html", items = items)

# Recipe table interface
@app.route('/admin/recipe_view')
def get_recipes():
    recipes = recipe.get_all()
    return render_template("recipe_view.html", recipes = recipes)

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

# Removes a recipe from the recipe table.
@app.route('/admin/recipe_view/delete', methods = ['POST'])
def delete_recipe():
    try:
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
                                                'expiry', 'unit', 'user-id'])
    inventory_id = request.form['inventory_id']
    name = sanitised_fields[0]
    brand = sanitised_fields[1]
    quantity = sanitised_fields[2]
    expiry_date = sanitised_fields[3]
    unit = sanitised_fields[4]
    barcode = request.form['barcode']
    user = sanitised_fields[5]
    if barcode == "None":
        barcode = None
    if user == "":
        user = None
    # Checks that the format is correct for the expiry date.
    valid = input_check.validate_expiry(expiry_date)
    if valid:
        try:
            item.update_item(inventory_id, barcode, name, brand, expiry_date, quantity, unit, user)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    else:
         return jsonify({'success': False, 'error': str("Expiry formatted incorrectly")})

# Updates the details of a selected recipe in the recipe table.
@app.route('/admin/item_view/update_recipe', methods = ['POST'])
def update_recipe_admin():
    # Sanitise the input to prevent sql injection.
    sanitised_fields = input_check.sanitise_all(['name', 'instructions', 'user-id', 
                                                'prep', 'cook', 'servings'])
    name = sanitised_fields[0]
    instructions = sanitised_fields[1]
    user = sanitised_fields[2]
    recipe_id = request.form['recipe-id']
    if user == "":
        user = None
    try:
        recipe.update_recipe(recipe_id, name, instructions, user)
        return jsonify({'success': True})
    except Exception as e:
        print(e)
        return jsonify({'success': False, 'error': str(e)})

# Adds a new item to the item table.
@app.route('/admin/item_view/add_item', methods = ['POST'])
def add_item_admin():
    # Sanitise the input to prevent sql injection.
    sanitised_fields = input_check.sanitise_all(['name', 'brand', 'quantity', 
                                                'expiry', 'unit', 'barcode',
                                                'user-id'])
    inventory_id = request.form['inventory_id']
    name = sanitised_fields[0]
    brand = sanitised_fields[1]
    quantity = sanitised_fields[2]
    expiry_date = sanitised_fields[3]
    unit = sanitised_fields[4]
    barcode = sanitised_fields[5]
    user = sanitised_fields[6]
    print(sanitised_fields)
    # Barcodes and user ids can be empty. 
    if barcode == "":
        barcode = None
    if user == "":
        user = None
    # Checks that the format is correct for the expiry date.
    valid = input_check.validate_expiry(expiry_date)
    if valid:
        try:
            item.add_item(barcode, name, brand, expiry_date, quantity, unit, user)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    else:
         return jsonify({'success': False, 'error': str("Expiry formatted incorrectly.")})

# Adds a new recipe to the recipe table.   
@app.route('/admin/recipe_view/add_item', methods = ['POST'])
def add_recipe_admin():
    # Sanitise the input to prevent sql injection.
    sanitised_fields = input_check.sanitise_all(['name', 'instructions', 'user-id', 
                                                'prep', 'cook', 'servings'])
    name = sanitised_fields[0]
    instructions = sanitised_fields[1]
    user = sanitised_fields[2]
    if user == "":
        user = None
    try:
        recipe.add_recipe(name, instructions, user)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # Classes for handling sql expressions
    input_check = InputHandling()
    item = item_table()
    recipe = RecipeTable()
    app.run(debug=True)