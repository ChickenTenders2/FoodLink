from flask import Flask, render_template, request, redirect, url_for, session
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
    items = inv.get_items(user_id)
    for item in items:
        item[6] = item[6].strftime('%Y-%m-%d')
    return render_template("inventory.html", items=items)

@app.route('/update_item', methods=['POST'])
def update_item():
    inventory_id = request.form['inventory_id']
    quantity = request.form['quantity']
    expiry_date = request.form['expiry_date']
    print(inventory_id, quantity, expiry_date)
    # Update the database with new quantity and expiry date
    inv.update_item(inventory_id, quantity, expiry_date)
    
    return redirect(url_for('get_inventory'))

if __name__ == '__main__':
    app.run(debug=True)

