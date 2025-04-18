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

user_id = 2
### INVENTORY ROUTES ###

# Inventory interface
@app.route('/inventory/')
def get_inventory():
    return render_template("inventory.html")

# allows for no search query to be entered
@app.route('/inventory/get/', defaults={'search_query': None})
@app.route('/inventory/get/<search_query>')
# used to dynamically get inventory
def api_inventory(search_query = None):
    try:
        # searches for an item if query is provided otherwise gets all items
        if search_query:
            items = inv.search_items(user_id, search_query)
        else:
            items = inv.get_items(user_id)

        return jsonify({"success": True, 'items': items})
    except Exception as e:
        return jsonify({"success": False, "error":str(e)})

# Add item to inventory interface
@app.route("/inventory/add_item/")
def add_to_inventory():
    return render_template("inventory_add.html")

# Add item to inventory
@app.route("/inventory/add_item/add", methods=["POST"])
def append_inventory():
    item_id = request.form.get("item_id")
    response = inv.process_add_form(user_id, item_id, request.form)    
    return jsonify(response)

# Update quantity and expiry of item in inventory
@app.route('/inventory/update_item', methods = ['POST'])
def update_item(): 
    try:
        # gets variables needed to update item
        inventory_id = request.form['inventory_id']
        quantity = request.form['quantity']
        expiry_date = request.form['expiry_date']
        # Update the database with new quantity and expiry date
        inv.update_item(inventory_id, quantity, expiry_date)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
@app.route('/remove_item', methods=['POST'])
def remove_item():
    try:
        inventory_id = request.form['inventory_id']
        print("Inventory ID received:", request.form['inventory_id'])
        inv.remove_item(inventory_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route("/inventory/add_item/new", methods = ["POST"])
def new_item():
    
    response = item.process_add_form(request.form, request.files, user_id)
    item_id = response["item_id"]

    # if the item was not succesffuly added to the item table
    if not response["success"]:
        return jsonify(response)
    else:
        # gets image if uploaded otherwise equals none
        image = request.form.get("item_image", None)
        original_item_id = request.form.get("item_id") or None
        # adds image if uploaded or uses cloned image if possible
        item.add_item_image(image, item_id, original_item_id)
    
    if not request.form.get("add_to_inventory"):
        return jsonify({"success": True, "item_id": item_id, "message": "Item added to personal items."})
    
    response = inv.process_add_form(user_id, item_id, request.form)
    if response["success"]:
        return jsonify({"success": True, "item_id": item_id, "message": "Item added to inventory and personal items."})
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
    
    try:
        search_term = request.form["search_term"]
        items = item.text_search(user_id, search_term)
        return jsonify({"success": True, "items": items})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Get item by barcode search
@app.route("/items/barcode_search/<barcode>")
def get_item_by_barcode(barcode):
    
    try:
        item_info = item.barcode_search(user_id, barcode)
        if item_info:
            # returns the first item in the list as barcodes are unique
            return jsonify({"success": True, "item": item_info})
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
    response = item.process_add_form(request.form)
    if response["success"]:
        item_id = response["item_id"]
        # gets image if uploaded otherwise equals none
        image = request.form.get("item_image", None)
        # adds image if uploaded
        item.add_item_image(image, item_id)
    
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
        
        new_item_id = request.form.get("new_item_id")
        item_id = request.form.get("item_id") or None
        item_report.add_report(new_item_id, item_id, user_id)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error":str(e)})

@app.route("/items/reports")
def display_reports():
    return render_template("reports.html")

@app.route("/items/reports/get")
def get_reports():
    return jsonify({"success": True, "reports": item_report.get_reports()})

@app.route("/items/reports/<new_item_id>/<item_id>")
def display_report(new_item_id, item_id):
    return render_template("report.html", new_item_id = new_item_id, item_id = item_id)

@app.route("/items/reports/resolve", methods=["POST"])
def resolve_report():
    try:
        action = request.form.get("action")
        barcode = request.form.get("barcode") or None
        new_item_id = request.form.get("new_item_id")
        original_item_id = request.form.get("item_id") or None
        # gets image if uploaded otherwise equals none
        image = request.form.get("item_image", None)
        # if the missing item reported isnt elligible for being added 
        if action == "deny" and original_item_id is None:
            # gets the reports
            reports = item_report.get_reports_by(new_item_id)
            # report will be singular
            _, personal_item_name, user_id = reports[0]
            # removes the report
            item_report.remove_report(new_item_id)

            message = """Thank you for reporting a missing item. 
                        Unfortunately, your item is not currently elligible to be added at this time.
                        However, you can still use your personal item. 
                        """

            print(user_id, personal_item_name, message)
            #####################################################
                            ### NOTIFY USER ITEM IS NOT CURRENTLY ELLIGIBLE FOR ADDITION (or something like that) ###
            #####################################################
            return jsonify({"success": True, "message": message})
        # if the proposed error was with an item having incorrect information (misinformation)
        if original_item_id:
            # if the original item had an error
            if action == "approve":
                # updates original item with correct information if approved
                # sets the user_id = null for the item so it appears for all users
                item.process_update_form(original_item_id, request.form)
                # updates image if uploaded
                item.add_item_image(image, original_item_id)
            
                message = """Thank you for reporting an item error. 
                            Your personal item has been successfully replaced."""
            # if original item was already correct
            else:
                message = """Thank you for reporting an item error. 
                        However the original item was already correct! 
                        Please be careful to double check before reporting an item.
                        Your personal item has been successfully replaced."""

            # id of item to replace personal items with
            replace_id = original_item_id

            # finds reports that report the original item
            duplicate_reports = item_report.get_reports_by(new_item_id, original_item_id, "id")

        # if the error was a missing item and it got approved
        else:
            # adds the missing item to the table
            # sets the user_id = null for the item so it appears for all users
            response = item.process_add_form(request.form)
            # gets the id to replace the personal items with
            replace_id = response["item_id"]

            # adds image if uploaded or uses users personal item image if possible
            item.add_item_image(image, replace_id, new_item_id)
    
            message = """Thank you for reporting a missing item.
                        Your request has been approved!
                        Your personal item has been successfully replaced."""

            # find other reports that reported the missing item
            # finds by same barcode as their is no original item for missing items
            # also searches using the new_item_id incase the item has no barcode
            duplicate_reports = item_report.get_reports_by(new_item_id, barcode, "barcode")

        # gets the limit that a users item can have for quantity
        default_quantity = item.get_default_quantity(replace_id)
        # for each report of an item
        for personal_item_id, personal_item_name, user_id in duplicate_reports:
            # replace the personal item the user made with the now corrected / new item
            inv.correct_personal_item(personal_item_id, replace_id, default_quantity)
            # removes the users personal item as it is no longer needed
            item.remove_item(personal_item_id)
            # removes the report
            item_report.remove_report(personal_item_id)

            #####################################################
                        ### NOTIFY USER OF CHANGE ###
            #####################################################
            print(user_id, personal_item_name, message)

        return jsonify({"success": True, "message": message})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    # Classes for handling sql expressions
    inv = inventory()
    item = item_table()
    item_report = item_error()
    # Class for handling barcode scanning
    scanner = barcode()
    # Runs the app
    app.run(debug=True)