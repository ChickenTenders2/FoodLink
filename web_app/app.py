from flask import Flask, jsonify, render_template, request, redirect, url_for, session
import os
import json
import time
import requests
from inventory import inventory
from notification import notification
from thingsboard import thingsboard

app = Flask(__name__, template_folder="templates")
app.secret_key = os.urandom(24)

# notification class instance
notif = notification()  

# thingsboard class instance
tb = thingsboard()

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

    user_id = 2

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
# Login Route

# Register Route

# Logout Route

# Inventory Interface Route

if __name__ == '__main__':
    app.run(debug=True)

