from flask import Flask, jsonify, render_template, request, url_for, Response
from item import item_table
from recipe import recipe_table
from input_handling import input_handling
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

# Removes a item from the items table.
@app.route('/admin/recipe_view/delete', methods = ['POST'])
def delete_recipe():
    try:
        id = request.data.decode('utf-8')
        recipe.remove_recipe(id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/item_view/update_item', methods = ['POST'])
def update_item_admin(): 
    try:
        input_check.sanitise_all(['name', 'brand', 'quantity', 'expiry', 'unit', 'user-id'])
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    inventory_id = request.form['inventory_id']
    name = request.form['name']
    brand = request.form['brand']
    quantity = request.form['quantity']
    expiry_date = request.form['expiry']
    unit = request.form['unit']
    barcode = request.form['barcode']
    user = request.form['user-id']
    if barcode == "None":
        barcode = None
    if user == "":
        user = None
    valid = input_check.validate_expiry(expiry_date)
    if valid:
        try:
            item.update_item(inventory_id, barcode, name, brand, expiry_date, quantity, unit, user)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    else:
         return jsonify({'success': False, 'error': str("Expiry formatted incorrectly")})
    
@app.route('/admin/item_view/update_recipe', methods = ['POST'])
def update_recipe_admin():
    try:
        input_check.sanitise_all(['name', 'instructions', 'user-id'])
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    recipe_id = request.form['recipe-id']
    name = request.form['name']
    instructions = request.form['instructions']
    user = request.form['user-id']
    if user == "":
        user = None
    try:
        recipe.update_recipe(recipe_id, name, instructions, user)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
@app.route('/admin/item_view/add_item', methods = ['POST'])
def add_item_admin():
    try:
        input_check.sanitise_all(['barcode', 'name', 'brand', 'quantity', 'expiry', 'unit', 'user-id'])
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    barcode = request.form['barcode']
    name = request.form['name']
    brand = request.form['brand']
    quantity = request.form['quantity']
    expiry_date = request.form['expiry']
    unit = request.form['unit']
    user = request.form['user-id']
    if barcode == "":
        barcode = None
    if user == "":
        user = None
    valid = input_check.validate_expiry(expiry_date)
    if valid:
        try:
            item.add_item(barcode, name, brand, expiry_date, quantity, unit, user)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    else:
         return jsonify({'success': False, 'error': str("Expiry formatted incorrectly.")})
    
@app.route('/admin/recipe_view/add_item', methods = ['POST'])
def add_recipe_admin():
    try:
        input_check.sanitise_all(['name', 'instructions', 'user-id'])
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    name = request.form['name']
    instructions = request.form['instructions']
    user = request.form['user-id']
    if user == "":
        user = None
    try:
        recipe.add_recipe(name, instructions, user)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # Classes for handling sql expressions
    input_check = input_handling()
    item = item_table()
    recipe = recipe_table()
    app.run(debug=True)