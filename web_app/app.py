from flask import Flask, jsonify, render_template, request, url_for, Response
from inventory import inventory
from barcode import barcode
from item import item_table
from datetime import date
from dateutil.relativedelta import relativedelta

app = Flask(__name__, template_folder = "templates")

# Dashboard Route
@app.route('/')
def index():
    temp_url = "https://thingsboard.cs.cf.ac.uk/dashboard/9c597b10-0b04-11f0-8ef6-c9c91908b9e2?publicId=0d105160-0daa-11f0-8ef6-c9c91908b9e2" 
    humid_url = "https://thingsboard.cs.cf.ac.uk/dashboard/74d87180-0dbc-11f0-8ef6-c9c91908b9e2?publicId=0d105160-0daa-11f0-8ef6-c9c91908b9e2"
    return render_template('index.html', temp_url = temp_url, humid_url = humid_url)
# Login Route

# Register Route

# Logout Route


### INVENTORY ROUTES ###

# Inventory interface
@app.route('/inventory/')
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

    # formats each item as list for easier modification of date format
    items = [list(i) for i in items]
    # formats date for front end
    for item in items:
        item[6] = item[6].strftime('%Y-%m-%d')

    return render_template("inventory.html", items = items, sort_by = sort_by)

# Add item to inventory interface
@app.route("/inventory/add_item/")
def add_to_inventory():
    user_id = 2
    return render_template("inventory_add.html")

# Add item to inventory
@app.route("/inventory/add_item/add", methods=["POST"])
def append_inventory():
    user_id = 2
    try:
        id = request.form["item_id"]
        quantity = request.form["quantity"]
        expiry = request.form["expiry_date"]
        inv.add_item(user_id, id, quantity, expiry)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Update quantity and expiry of item in inventory
@app.route('/inventory/update_item', methods = ['POST'])
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


### BARCODE SCANNING ROUTES ###

# Opens camera module and returns feed
@app.route('/get_scanner')
def get_scanner():
    return Response(scanner.decode_barcode(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Closes camera module
@app.route('/close_scanner')
def close_scanner():
    scanner.release_capture()
    return jsonify({"success":True})

# Returns the barcode number if one is found
@app.route('/get_barcode')
def get_barcode():
    barcode = scanner.get_barcode()
    if (barcode):
        return jsonify({"success": True, "barcode": barcode})
    else:
        return jsonify({"success": False})

# Resets the barcode number to null
@app.route('/clear_barcode')
def clear_barcode():
    scanner.clear_barcode()
    return jsonify({"success":True})


### ITEM ROUTES ###

# Get items by text search
@app.route("/items/text_search", methods=["POST"])
def text_search():
    user_id = 2
    try:
        search_term = request.form["search_term"]
        items = item.text_search(user_id, search_term)
        # formats each item as list for easier modification of date format
        #items = [list(i) for i in items]
        return jsonify({"success": True, "items": items})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Get item by barcode search
@app.route("/items/barcode_search", methods = ["POST"])
def get_item_by_barcode():
    user_id = 2
    try:
        barcode_number = request.form["barcode"]
        item_info = item.barcode_search(user_id, barcode_number)
        print(item_info)
        if item_info:
            # one item per barcode so only a single item will be returned
            item_info = list(item_info[0])
            # converts expiry time to the estimated expiry of the item
            expiry_time_values = item_info[3].split("/")
            days = int(expiry_time_values[0])
            months = int(expiry_time_values[1])
            years = int(expiry_time_values[2])
            estimated_expiry = date.today() + relativedelta(years = years, months = months, days = days)
            item_info[3] = estimated_expiry.strftime('%Y-%m-%d')
            return jsonify({"success": True, "item": item_info})
        else:
            return jsonify({"success": False, "error": "Item not found."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Add item interface
@app.route('/add_item')
def add_item():
    return render_template("add_item.html")

# Add item to item table
@app.route('/add_item/add', methods=["POST"])
def append_item_db():
    try:
        # gets item information
        barcode = request.form.get("barcode")
        name = request.form.get("name")
        brand = request.form.get("brand")
        default_quantity = request.form.get("default_quantity")
        unit = request.form.get("unit")

        # gets expiry time and converts to int to remove any leading zeros
        # also checks inputs are numbers
        day = int(request.form.get("expiry_day"))
        month = int(request.form.get("expiry_month"))
        year = int(request.form.get("expiry_year"))

        # makes sure expire date is not 0 and that each number is within the correct range
        if (day == 0 and month == 0 and year == 0) \
            or not (0 <= day < 31 and 0 <= month < 12 and 0 <= year < 100):
            return jsonify({"success": False, "error": "Expiry time out of range."})

        # formats expiry time as string
        expiry_time = f"{day}/{month}/{year}"

        # adds item to db and gets item id
        item_id = item.add_item(barcode, name, brand, expiry_time, default_quantity, unit)

        # gets image if uploaded otherwise equals none
        image = request.files.get("item_image", None)
        # if an image is uploaded
        if image:
            # store image in server with name item id
            path = f"static/images/{item_id}.jpg"
            image.save(path)

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


if __name__ == '__main__':
    # Classes for handling sql expressions
    inv = inventory()
    item = item_table()
    # Class for handling barcode scanning
    scanner = barcode()
    # Runs the app
    app.run(debug=True)

