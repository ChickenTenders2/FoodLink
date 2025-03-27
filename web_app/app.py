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

if __name__ == '__main__':
    #app.run(debug=True)
    get_inventory()

