from flask import Flask, jsonify, render_template, request, redirect, url_for, session
import os
import paho.mqtt.client as mqtt
import json
import time
import requests
from inventory import inventory
from notification import notification

app = Flask(__name__, template_folder="templates")
app.secret_key = os.urandom(24)

# notification class instance
notif = notification()  

def get_jwt_token():
    login_url = "https://thingsboard.cs.cf.ac.uk/api/auth/login"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "username": "group01@cardiff.ac.uk",
        "password": "group012025"
    }

    response = requests.post(login_url, json=data, headers=headers)

    if response.status_code == 200:
        print('Login successful')
        token = response.json()['token']
        print("JET token:", token)
        return token
    else:
        print("Login failed: ", response.json())

def get_telemetry(token, device_id):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
     }

    url = f"https://thingsboard.cs.cf.ac.uk/api/plugins/telemetry/DEVICE/{device_id}/values/timeseries?keys=temperature,humidity"

    # s = requests.Session()
    response = requests.get(url, headers=headers)

    if response.status_code == 401:
        print("Token expired, refreshing...")
        new_token = get_jwt_token()
        if new_token:
            return get_telemetry(new_token, device_id)
        else:
            return None
    elif response.ok:
        data = response.json()
        return data
    else:
        print("Error: ", response.status_code, response.text)
        return None


# Dashboard Route
@app.route('/')
def index():
    # JWT_TOKEN = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJncm91cDAxQGNhcmRpZmYuYWMudWsiLCJzY29wZXMiOlsiVEVOQU5UX0FETUlOIl0sInVzZXJJZCI6IjQ5ODQwYWQwLWQxOTQtMTFlZi05NjkzLWY3NWRhNjRlN2IzYSIsImVuYWJsZWQiOnRydWUsImlzUHVibGljIjpmYWxzZSwidGVuYW50SWQiOiJjY2E5MzhjMC1kMTkxLTExZWYtOTY5My1mNzVkYTY0ZTdiM2EiLCJjdXN0b21lcklkIjoiMTM4MTQwMDAtMWRkMi0xMWIyLTgwODAtODA4MDgwODA4MDgwIiwiaXNzIjoidGhpbmdzYm9hcmQuaW8iLCJpYXQiOjE3NDQyMDEwODYsImV4cCI6MTc0NDIxMDA4Nn0.BWM6GJX9qHUSLM8x21bAzVBkxmCNc1qAn94U-4ulUQ9h_D5f0LWVASdA_InfZOrZU5H3hA781Wubdrz81i_KsA"
    device_id = "15b7a650-0b03-11f0-8ef6-c9c91908b9e2"

    # headers = {
    #     "Authorization": f"Bearer {JWT_TOKEN}",
    #     "Content-Type": "application/json"
    # }

    # url = f"https://thingsboard.cs.cf.ac.uk/api/plugins/telemetry/DEVICE/{device_id}/values/timeseries?keys=temperature,humidity"

    # # s = requests.Session()
    # response = requests.get(url, headers=headers)

    # if response.ok:
    #     data = response.json()
    #     print("Telemetry: ", data)
    # else:
    #     print("Error: ", response.status_code, response.text)

    token = get_jwt_token()
    data = get_telemetry(token, device_id)
    temperature = humidity = None

    if data:
       temperature = float(data['temperature'][0]['value'])
       humidity = float(data['humidity'][0]['value'])

    user_id = 2

    temp_url = "https://thingsboard.cs.cf.ac.uk/dashboard/9c597b10-0b04-11f0-8ef6-c9c91908b9e2?publicId=0d105160-0daa-11f0-8ef6-c9c91908b9e2" 
    humid_url = "https://thingsboard.cs.cf.ac.uk/dashboard/74d87180-0dbc-11f0-8ef6-c9c91908b9e2?publicId=0d105160-0daa-11f0-8ef6-c9c91908b9e2"

    # temperature = get_thingsboard_value("temperature")
    # humidity = get_thingsboard_value("humidity")
    # print(temperature, humidity)

    notif.temperature_humidity_notification(user_id, temperature, humidity)

    notifications = notif.get_notifications(user_id)

    return render_template('index.html', temp_url=temp_url, humid_url = humid_url, notifications=notifications)
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

if __name__ == '__main__':
    app.run(debug=True)

