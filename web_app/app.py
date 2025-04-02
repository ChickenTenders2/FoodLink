from flask import Flask, jsonify, render_template, request, url_for, Response
import os
from inventory import inventory
from barcode import barcode

app = Flask(__name__, template_folder="templates")
app.secret_key = os.urandom(24)

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

@app.route('/scan_barcode')
def scan_barcode():
    return render_template('scan.html')

@app.route('/check_barcode')
def check_barcode():
    return jsonify({"barcode": scanner.get_barcode()})

@app.route('/clear_barcode')
def clear_barcode():
    scanner.clear_barcode()
    return jsonify({"success":True})

@app.route('/close_capture')
def close_capture():
    scanner.release_capture()
    return jsonify({"success":True})

@app.route('/add_item')
def add_item():
    return render_template("add_item.html")
    
if __name__ == '__main__':
    app.run(debug=True)

