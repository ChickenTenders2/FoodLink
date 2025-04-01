from flask import Flask, jsonify, render_template, request, redirect, url_for, session
import os
from inventory import inventory


app = Flask(__name__, template_folder="templates")
app.secret_key = os.urandom(24)



# Dashboard Route

# Login Route

# Register Route

# Logout Route

# Inventory Interface Route
inv = inventory()

@app.route('/inventory')
def get_inventory():
    user_id = 2
    search_query = request.args.get('search')
    sort_by = request.args.get('sort_by')

    # searches for an item if query is provided otherwise gets all items
    if search_query:
        items = inv.search_items(user_id, search_query)
    else:
        items = inv.get_items(user_id)
    
    if sort_by in ['name', 'expiry']:
        # sorts by name or expiry
        items = sorted(items, key=lambda x: x[2] if sort_by == 'name' else x[6])

    return render_template("inventory.html", items=items, sort_by=sort_by)

@app.route('/update_item', methods=['POST'])
def update_item():
    # gets variables needed to update item
    inventory_id = request.form['inventory_id']
    quantity = request.form['quantity']
    expiry_date = request.form['expiry_date']
    
    try:
        # Update the database with new quantity and expiry date
        inv.update_item(inventory_id, quantity, expiry_date)
        # returns response to js code
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)

