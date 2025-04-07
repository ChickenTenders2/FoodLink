from flask import Flask, jsonify, render_template, request, redirect, url_for, session
import os
import mariadb
from shoppingList import shoppingList


app = Flask(__name__, template_folder="templates")
app.secret_key = os.urandom(24)



# Dashboard Route

# Login Route

# Register Route

# Logout Route

# Inventory Interface Route

# Shopping List Interface Route
shop = shoppingList()

@app.route('/shopping-list', methods=['GET', 'POST'])
def get_shoppingList():
    user_id = 2

    if request.method == 'POST':
        try:
            if 'clear' in request.form:
                shop.clear_items(user_id)
                return jsonify({"success": True, "action": "clear"})
            elif 'remove' in request.form:
                item_id = request.form['remove']
                shop.remove_item(item_id)
                return jsonify({"success": True, "action": "remove", "item_id": item_id})
            elif 'mark_bought' in request.form:
                item_id = request.form['mark_bought']
                bought_str = request.form.get('bought', 0)
                bought = int(bought_str)
                print("Updating bought field:", item_id, bought)
                shop.item_bought(item_id, bought)
                return jsonify({"success": True, "action": "mark_bought"})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})
    
    items = shop.get_items(user_id)
    unbought_items = [item for item in items if item[3] == 0]
    bought_items = [item for item in items if item[3] == 1]

    low_stock = shop.low_stock_items(user_id)
    print("low stock items:", low_stock)
    print('items:', items)
    return render_template("shoppinglist.html", items=items, unbought_items=unbought_items, bought_items=bought_items, low_stock=low_stock)

@app.route('/add-shopping-item', methods=['POST'])
def add_shopping_item():
    user_id = 2
    try:
        item_name = request.form['item_name']
        quantity = request.form['quantity']
        shop.add_item(user_id, item_name, quantity)
        return jsonify({"success": True, "action": "add", "item": item_name})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    # return redirect(url_for('get_shoppingList'))

@app.route('/update-shopping-item', methods=['POST'])
def update_shopping_item():
    user_id = 2
    try:
        item_id = request.form['item_id']
        item_name = request.form['item_name']
        quantity = request.form['quantity']
        shop.update_item(item_id, item_name, quantity)
        return jsonify({"success": True, "action": "update", "item": item_name})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)