from flask import Flask, jsonify, render_template, request, url_for, Response
from inventory import Inventory
from scanner import Scanner
from item import Item
#from success import Success
from report import Report
from shoppingList import shoppingList
from os.path import isfile as file_exists
from notification import notification
from thingsboard import thingsboard

app = Flask(__name__, template_folder = "templates")

user_id = 2

# Dashboard Route
@app.route('/', methods=['GET', 'POST'])
def index():
    device_id = "15b7a650-0b03-11f0-8ef6-c9c91908b9e2"

    token = tb.get_jwt_token()
    data = tb.get_telemetry(token, device_id)
    temperature = humidity = None

    if data:
       temperature = float(data['temperature'][0]['value'])
       humidity = float(data['humidity'][0]['value'])

    temp_url = "https://thingsboard.cs.cf.ac.uk/dashboard/9c597b10-0b04-11f0-8ef6-c9c91908b9e2?publicId=0d105160-0daa-11f0-8ef6-c9c91908b9e2" 
    humid_url = "https://thingsboard.cs.cf.ac.uk/dashboard/74d87180-0dbc-11f0-8ef6-c9c91908b9e2?publicId=0d105160-0daa-11f0-8ef6-c9c91908b9e2"

    notif.temperature_humidity_notification(user_id, temperature, humidity)
    notif.expiry_notification(user_id)

    notifications = notif.get_notifications(user_id)
    unread_count = sum(1 for n in notifications if n[4] == 0)

    if request.method == 'POST' and request.json.get('mark_read'): 
        try: 
            notif_id = request.json.get('mark_read') 
            notif.mark_read(notif_id) 
            return jsonify({'success': True})
        except Exception as e: 
            return jsonify({'success': False, 'error': str(e)})

    return render_template('index.html', temp_url=temp_url, humid_url = humid_url, notifications=notifications, unread_count=unread_count)

# Dynamtically update notification bar
@app.route('/get_notifications', methods=['GET'])
def get_notifications():
    user_id = 2

    device_id = "15b7a650-0b03-11f0-8ef6-c9c91908b9e2"
    token = tb.get_jwt_token()
    data = tb.get_telemetry(token, device_id)

    temperature = humidity = None
    if data:
        temperature = float(data['temperature'][0]['value'])
        humidity = float(data['humidity'][0]['value'])

    notif.temperature_humidity_notification(user_id, temperature, humidity)
    notif.expiry_notification(user_id)

    notifications = notif.get_notifications(user_id)
    unread_count = sum(1 for n in notifications if n[4] == 0)

    return jsonify({
        'notifications': [
            {
                'id': n[0],
                'message': n[2],
                'timestamp': n[3].strftime('%Y-%m-%d %H:%M'),
                'severity': n[5],
                'read': n[4] == 1
            }
            for n in notifications
        ],
        'unread_count': unread_count
    })


# Login Route

# Register Route

# Logout Route


# @app.route('/success')
# def added_successfully():
#   try:
#     # Triggers the success alert function when the route is fetched
#     # so that the Raspberry Pi LCD updates with the message 'Added!'.
#     success.alert()
#     return jsonify({"success": True})
#   except Exception as e:
#         return jsonify({"success": False, "error": str(e)})
  

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
            items = inventory.search_items(user_id, search_query)
        else:
            items = inventory.get_items(user_id)

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
    response = inventory.process_add_form(user_id, item_id, request.form)    
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
        inventory.update_item(inventory_id, quantity, expiry_date)
        # returns response to js code
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
@app.route('/remove_item', methods=['POST'])
def remove_item():
    try:
        inventory_id = request.form['inventory_id']
        print("Inventory ID received:", request.form['inventory_id'])
        inventory.remove_item(inventory_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route("/inventory/add_item/new", methods = ["POST"])
def new_item():
    response = item.process_add_form(request.form, user_id)
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
    
    response = inventory.process_add_form(user_id, item_id, request.form)
    if response["success"]:
        return jsonify({"success": True, "item_id": item_id, "message": "Item added to inventory and personal items."})
    else:
        return jsonify(response)


### BARCODE SCANNING ROUTES ###

# Opens camera module and returns feed
@app.route('/scanner/get')
def get_scanner():
    return Response(scanner.scan(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Closes camera module
@app.route('/scanner/close')
def close_scanner():
    scanner.release_capture()
    return jsonify({"success":True})

# Returns the barcode number if one is found
@app.route('/scanner/get_object')
def get_object():
    object = scanner.get_scanned()
    if (object):
        scanner.clear_scanned()
        return jsonify({"success": True, "object": object})
    else:
        return jsonify({"success": False})

@app.route("/unpause_scanner")
def unpause_scanner():
    scanner.unpause_scanner()
    return jsonify({"success":True})

@app.route("/scanner/toggle_mode/<value>")
def toggle_scan_mode(value):
    if value == "true":
        scanner.toggle_mode(True)
        return jsonify({"success":True})
    elif value =="false":
        scanner.toggle_mode(False)
        return jsonify({"success":True})
    else:
        return jsonify({"success":False})


### ITEM ROUTES ###

@app.route("/items/single_text_search/<item_name>")
def single_item_search(item_name):
    try:
        items = item.text_search(user_id, item_name)
        item_info = items[0]
        return jsonify({"success": True, "item": item_info})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

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

# Get item by id
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

# Check if item has an image
@app.route("/find_image/<item_id>")
def find_image(item_id):
    path = f"static/images/{item_id}.jpg"
    exists = file_exists(path)
    return jsonify({"success": exists})


### ITEM REPORT ROUTES

@app.route("/items/reports/new", methods=["POST"])
def report_item():
    try:
        new_item_id = request.form.get("new_item_id")
        item_id = request.form.get("item_id") or None
        report.add_report(new_item_id, item_id, user_id)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error":str(e)})

@app.route("/items/reports")
def display_reports():
    return render_template("reports.html")

@app.route("/items/reports/get")
def get_reports():
    return jsonify({"success": True, "reports": report.get_reports()})

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
            reports = report.get_reports_by(new_item_id)
            # report will be singular
            _, personal_item_name, user_id = reports[0]
            # removes the report
            report.remove_report(new_item_id)
            # notification message
            message = lambda item_name : f"""Thank you for reporting the missing item, {item_name}. 
                        Unfortunately, your item is not currently elligible to be added at this time.
                        However, you can still continue to use your personal item. 
                        """

            # notify user of the change
            notif.support_notification(user_id, message(personal_item_name))

            return jsonify({"success": True})
        # if the proposed error was with an item having incorrect information (misinformation)
        if original_item_id:
            # if the original item had an error
            if action == "approve":
                # updates original item with correct information if approved
                # sets the user_id = null for the item so it appears for all users
                item.process_update_form(original_item_id, request.form)
                # updates image if uploaded
                item.add_item_image(image, original_item_id)
                # notification message
                message = lambda item_name : f"""Thank you for reporting an error with item, {item_name}. 
                            Your personal item has been successfully replaced."""
            # if original item was already correct
            else:
                # notification message
                message = lambda item_name : f"""Thank you for reporting an error with item, {item_name}. 
                        However the original item was already correct! 
                        Please be careful to double check before reporting an item.
                        Your personal item has been successfully replaced."""

            # id of item to replace personal items with
            replace_id = original_item_id

            # finds reports that report the original item
            duplicate_reports = report.get_reports_by(new_item_id, original_item_id, "id")

        # if the error was a missing item and it got approved
        else:
            # adds the missing item to the table
            # sets the user_id = null for the item so it appears for all users
            response = item.process_add_form(request.form)
            # gets the id to replace the personal items with
            replace_id = response["item_id"]

            # adds image if uploaded or uses users personal item image if possible
            item.add_item_image(image, replace_id, new_item_id)
    
            # notification message
            message = lambda item_name : f"""Thank you for reporting the missing item, {item_name}.
                        Your request has been approved!
                        Your personal item has been successfully replaced."""

            # find other reports that reported the missing item
            # finds by same barcode as their is no original item for missing items
            # also searches using the new_item_id incase the item has no barcode
            duplicate_reports = report.get_reports_by(new_item_id, barcode, "barcode")

        # gets the limit that a users item can have for quantity
        default_quantity = item.get_default_quantity(replace_id)
        # for each report of an item
        for personal_item_id, personal_item_name, user_id in duplicate_reports:
            # replace the personal item the user made with the now corrected / new item
            inventory.correct_personal_item(personal_item_id, replace_id, default_quantity)
            # removes the users personal item as it is no longer needed
            item.remove_item(personal_item_id)
            # removes the report
            report.remove_report(personal_item_id)
            # notify user of the change
            notif.support_notification(user_id, message(personal_item_name))

        return jsonify({"success": True})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# Shopping List Interface Route

@app.route('/shopping_list', methods=['GET', 'POST'])
def get_shoppingList():
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
                shop.item_bought(item_id, bought)
                return jsonify({"success": True, "action": "mark_bought"})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})
    
    items = shop.get_items(user_id)
    unbought_items = [item for item in items if item[3] == 0]
    bought_items = [item for item in items if item[3] == 1]

    low_stock = shop.low_stock_items(user_id)
    return render_template("shoppinglist.html", items=items, unbought_items=unbought_items, bought_items=bought_items, low_stock=low_stock)

@app.route('/shopping_list/add', methods=['POST'])
def add_shopping_item():
    try:
        item_name = request.form['item_name']
        quantity = request.form['quantity']
        shop.add_item(user_id, item_name, quantity)
        return jsonify({"success": True, "action": "add", "item": item_name})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/shopping_list/update', methods=['POST'])
def update_shopping_item():
    try:
        item_id = request.form['item_id']
        item_name = request.form['item_name']
        quantity = request.form['quantity']
        shop.update_item(item_id, item_name, quantity)
        return jsonify({"success": True, "action": "update", "item": item_name})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    # Classes for handling sql expressions
    inventory = Inventory()
    item = Item()
    report = Report()
    # Class for handling barcode scanning
    scanner = Scanner()

    shop = shoppingList()

    #success = Success()

    # notification class instance
    notif = notification()  

    # thingsboard class instance
    tb = thingsboard()

    # Runs the app
    app.run(debug=True)