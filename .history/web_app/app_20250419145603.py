from flask import Flask, jsonify, render_template, request, url_for, Response
from item import item_table
from recipe import recipe_table
app = Flask(__name__, template_folder = "templates")

# Dashboard Route
@app.route('/')
def index():
    temp_url = "https://thingsboard.cs.cf.ac.uk/dashboard/9c597b10-0b04-11f0-8ef6-c9c91908b9e2?publicId=0d105160-0daa-11f0-8ef6-c9c91908b9e2" 
    humid_url = "https://thingsboard.cs.cf.ac.uk/dashboard/74d87180-0dbc-11f0-8ef6-c9c91908b9e2?publicId=0d105160-0daa-11f0-8ef6-c9c91908b9e2"
    return render_template('index.html', temp_url = temp_url, humid_url = humid_url)

# Item table interface
@app.route('/admin/item_view')
def get_items():
    items = item.get_all()
    return render_template("item_view.html", items = items)

# Item table interface
@app.route('/admin/recipe_view')
def get_recipes():
    recipes = recipe.get_all()
    return render_template("recipe_view.html", recipes = recipes)

@app.route('/admin/item_view/delete', methods = ['POST'])
def delete_item():
    try:
        id = request.data.decode('utf-8')
        item.remove_item(id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
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
    inventory_id = request.form['inventory_id']
    name = request.form['name']
    brand = request.form['brand']
    quantity = request.form['quantity']
    expiry_date = request.form['expiry']
    unit = request.form['unit']
    barcode = request.form['barcode']
    if barcode == "None":
        barcode = None
    try:
        item.update_item(inventory_id, barcode, name, brand, expiry_date, quantity, unit)
        return jsonify({'success': True})
    except Exception as e:
        print(e)
        return jsonify({'success': False, 'error': str(e)})
    
@app.route('/admin/item_view/update_recipe', methods = ['POST'])
def update_recipe_admin():
    recipe_id = request.form['recipe_id']
    name = request.form['name']
    instructions = request.form['instructions']
    try:
        recipe.update_recipe(recipe_id, name, instructions)
        return jsonify({'success': True})
    except Exception as e:
        print(e)
        return jsonify({'success': False, 'error': str(e)})
    
@app.route('/admin/item_view/add_item', methods = ['POST'])
def add_item_admin():
    barcode = request.form['barcode']
    name = request.form['name']
    brand = request.form['brand']
    quantity = request.form['quantity']
    expiry_date = request.form['expiry']
    unit = request.form['unit']
    if barcode.strip() == "":
        barcode = None
    try:
        item.add_item(barcode, name, brand, expiry_date, quantity, unit)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
@app.route('/admin/recipe_view/add_item', methods = ['POST'])
def add_recipe_admin():
    name = request.form['name']
    instructions = request.form['instructions']
    print(instructions)
    try:
        recipe.add_recipe(name, instructions)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # Classes for handling sql expressions
    item = item_table()
    recipe = recipe_table()
    app.run(debug=True)