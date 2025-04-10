from flask import Flask, jsonify, render_template, request, url_for, Response
from inventory import inventory
from barcode import barcode
from item import item_table
from identify import identify
from datetime import date
from dateutil.relativedelta import relativedelta

app = Flask(__name__, template_folder="templates")

# Dashboard Route
@app.route('/')
def index():
    temp_url = "https://thingsboard.cs.cf.ac.uk/dashboard/9c597b10-0b04-11f0-8ef6-c9c91908b9e2?publicId=0d105160-0daa-11f0-8ef6-c9c91908b9e2" 
    humid_url = "https://thingsboard.cs.cf.ac.uk/dashboard/74d87180-0dbc-11f0-8ef6-c9c91908b9e2?publicId=0d105160-0daa-11f0-8ef6-c9c91908b9e2"
    return render_template('index.html', temp_url=temp_url, humid_url = humid_url)
# Login Route

# Register Route

# Logout Route

# Inventory Interface Route
inv = inventory()
scanner = barcode()
ai = identify()
item = item_table()

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

    # formats each item as list for easier modification of date format
    items = [list(i) for i in items]
    # formats date for front end
    for item in items:
        item[6] = item[6].strftime('%Y-%m-%d')

    return render_template("inventory.html", items=items, sort_by=sort_by)

@app.route("/inventory/add_item/AI")
def add_to_inventory_AI():
    user_id = 2
    return render_template("inventory_add_AI.html")

@app.route("/inventory/add_item")
def add_to_inventory():
    user_id = 2
    return render_template("inventory_add.html")

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

@app.route("/barcode_search", methods = ["POST"])
def get_item_by_barcode():
    user_id = 2
    try:
        barcode_number = request.form["barcode"]
        item_info = item.barcode_search(user_id, barcode_number)
        if item_info:
            print(item_info)
            # converts expiry time to the estimated expiry of the item
            expiry_time_values = item_info[3].split("/")
            days = int(expiry_time_values[0])
            months = int(expiry_time_values[1])
            years = int(expiry_time_values[2])
            estimated_expiry = date.today() + relativedelta(years=years, months=months, days=days)
            item_info[3] = estimated_expiry.strftime('%Y-%m-%d')
            print(item_info)
            return jsonify({"success": True, "item":item_info})
        else:
            return jsonify({"success": False, "error": "Item not found."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/item_search", methods = ["POST"])
def get_item_by_name():
    user_id = 2
    try:
        item_name = request.form["item"]
        item_info = item.item_search(user_id, item_name)
        if item_info:
            print(item_info)
            # converts expiry time to the estimated expiry of the item
            expiry_time_values = item_info[3].split("/")
            days = int(expiry_time_values[0])
            months = int(expiry_time_values[1])
            years = int(expiry_time_values[2])
            estimated_expiry = date.today() + relativedelta(years=years, months=months, days=days)
            item_info[3] = estimated_expiry.strftime('%Y-%m-%d')
            print(item_info)
            return jsonify({"success": True, "item":item_info})
        else:
            return jsonify({"success": False, "error": "Item not found."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

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

@app.route('/barcode_scanner')
def barcode_scanner():
    return Response(scanner.decode_barcode(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/check_barcode')
def check_barcode():
    return jsonify({"barcode": scanner.get_barcode()})

@app.route('/clear_barcode')
def clear_barcode():
    scanner.clear_barcode()
    return jsonify({"success":True})

@app.route('/identify_item')
def identify_item():
    return Response(ai.identify_item(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/check_item')
def check_item():
    return jsonify({"item": ai.get_item()})

@app.route('/clear_item_name')
def clear_item_name():
    ai.clear_item_name()
    return jsonify({"success":True})

@app.route('/close_capture')
def close_capture():
    scanner.release_capture()
    return jsonify({"success":True})

@app.route('/add_item')
def add_item():
    return render_template("add_item.html")

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
    app.run(debug=True)

