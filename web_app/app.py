from flask import Flask, jsonify, render_template, request, url_for, Response
from inventory import inventory
from barcode import barcode
from item import item_table
from item_error import item_error
from os.path import isfile as file_exists
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
        items = sorted(items, key = lambda x: x[2] if sort_by == 'name' else x[6])

    # formats each item as list for easier modification of date format
    items = [list(i) for i in items]
    # formats date for front end
    for item in items:
        item[6] = item[6].strftime('%Y-%m-%d')

    return render_template("inventory.html", items = items, sort_by = sort_by)

# Add item to inventory interface
@app.route("/inventory/add_item/")
def add_to_inventory():
    return render_template("inventory_add.html")

# Add item to inventory
@app.route("/inventory/add_item/add", methods=["POST"])
def append_inventory():
    user_id = 2
    item_id = request.form.get("item_id")
    response = inv.process_add_form(user_id, item_id, request.form)
    return jsonify(response)

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
    
@app.route("/inventory/add_item/new", methods = ["POST"])
def new_item():
    user_id = 2
    response = item.process_add_form(request.form, request.files, user_id)

    # if the item was not succesffuly added to the item table
    if not response["success"]:
        return jsonify(response)
    
    if not request.form.get("add_to_inventory"):
        return jsonify({"success": True, "item_id": response["item_id"], "message": "Item added to personal items."})
    
    item_id = response["item_id"]
    response = inv.process_add_form(user_id, item_id, request.form)
    if response["success"]:
        return jsonify({"success": True, "item_id": response["item_id"], "message": "Item added to inventory and personal items."})
    else:
        return jsonify(response)


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
        scanner.clear_barcode()
        return jsonify({"success": True, "barcode": barcode})
    else:
        return jsonify({"success": False})

@app.route("/unpause_scanner")
def unpause_scanner():
    scanner.unpause_scanner()
    return jsonify({"success":True})

### ITEM ROUTES ###

# Get items by text search
@app.route("/items/text_search", methods=["POST"])
def text_search():
    user_id = 2
    try:
        search_term = request.form["search_term"]
        items = item.text_search(user_id, search_term)
        return jsonify({"success": True, "items": items})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Get item by barcode search         ###############              ####### MAKE SURE WHEN ADDING TO ITEM TABLE THERE IS ONLY 1 BARCODE FOR EACH USER_ID IN ITEM TABLE
@app.route("/items/barcode_search/<barcode>")
def get_item_by_barcode(barcode):
    user_id = 2
    try:
        item_info = item.barcode_search(user_id, barcode)
        if item_info:
            # returns the first item in the list as barcodes are unique
            return jsonify({"success": True, "item": item_info[0]})
        else:
            return jsonify({"success": False, "error": "Item not found."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    
@app.route("/items/get_item/<item_id>")
def get_item(item_id):
    try:
        item_info = item.get_item(item_id)
        return jsonify({"success": True, "item": item_info})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Add item interface
@app.route('/items/add_item')
def add_item():
    return render_template("add_item.html")

# Add item to item table
@app.route('/items/add_item/add', methods=["POST"])
def append_item_db():
    response = item.process_add_form(request.form, request.files)
    if response["success"]:
        # item id does not need to be returned
        return jsonify({"success": True})
    else:
        return jsonify(response)


@app.route("/find_image/<item_id>")
def find_image(item_id):
    path = f"static/images/{item_id}.jpg"
    exists = file_exists(path)
    return jsonify({"success": exists})


### ITEM REPORT ROUTES

@app.route("/items/report_item", methods=["POST"])
def report_item():
    try:
        user_id = 2
        new_item_id = request.form.get("new_item_id")
        item_id = request.form.get("item_id") or None
        item_report.add_report(new_item_id, item_id, user_id)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error":str(e)})

@app.route("/items/reports")
def display_reports():
    return render_template("reports.html")

@app.route("/items/get_reports")
def get_reports():
    return jsonify({"success": True, "reports": item_report.get_reports()})

@app.route("/items/reports/<new_item_id>/<item_id>")
def display_report(new_item_id, item_id):
    return render_template("report.html", new_item_id = new_item_id, item_id = item_id)

if __name__ == '__main__':
    # Classes for handling sql expressions
    inv = inventory()
    item = item_table()
    item_report = item_error()
    # Class for handling barcode scanning
    scanner = barcode()
    # Runs the app
    app.run(debug=True)