import time
import requests
import sys
import os
import grovepi

# The following 2 LCD functions are adapted from the IoT Lab Code:

# Send command to display.   
def textCommand(cmd):
    bus.write_byte_data(DISPLAY_TEXT_ADDR,0x80,cmd)
 
# Set the display text \n for second line so that the text can wrap automatically. 
def setText(text):
    #Clears the display
    textCommand(0x01)
    time.sleep(.05)
    # Turns the display on without the cursor.
    textCommand(0x08 | 0x04)
    # Sets the display to display 2 lines.
    textCommand(0x28)
    time.sleep(.05)
    count = 0
    row = 0
    for c in text:
        if c == '\n' or count == 16:
            count = 0
            row += 1
            if row == 2:
                break
            textCommand(0xc0)
            if c == '\n':
                continue
        count += 1
        bus.write_byte_data(DISPLAY_TEXT_ADDR,0x40,ord(c))

# Gets the jwt token for a secure connection to ThingsBoard
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
        print("JWT token:", token)
        return token
    else:
        print("Login failed: ", response.json())

# Gets the telemetry data from ThingsBoard
def get_telemetry(token, device_id):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
     }

    url = f"https://thingsboard.cs.cf.ac.uk/api/plugins/telemetry/DEVICE/{device_id}/values/timeseries?keys=message,distance"
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

def buzz():
    grovepi.digitalWrite(buzzer, 1)
    time.sleep(0.2)
    grovepi.digitalWrite(buzzer, 0)

# Triggers the buzzer 3 times.
def alarm():
    x = 'CLOSE DOOR!'
    setText(x)
    for i in range(3):
        buzz()
        time.sleep(1)
    x = 'FOODLINK'
    setText(x)

if __name__=="__main__":
    
    # ID of the device (used to connect to ThingsBoard).
    device_id = "15b7a650-0b03-11f0-8ef6-c9c91908b9e2"
    start_time = time.time()
    
    # The distance measured by the ultrasonic sensor when the door is closed.
    # Needs to be altered depending on the fridge model. 
    door_to_wall = 10

    last_time = ""

    buzzer = 8

    grovepi.pinMode(buzzer, "output")
    grovepi.set_bus("RPI_1")

    if sys.platform == 'uwp':
        import winrt_smbus as smbus
        bus = smbus.SMBus(1)
    else:
        import smbus
        import RPi.GPIO as GPIO
        rev = GPIO.RPI_REVISION
        if rev == 2 or rev == 3:
            bus = smbus.SMBus(1)
        else:
            bus = smbus.SMBus(0)

    DISPLAY_TEXT_ADDR = 0x3e

    token = get_jwt_token()
    x = 'FOODLINK'
    setText(x)

    countdown = False
    delay = 30
    
    while True:
          
        try:
             
          data = get_telemetry(token, device_id)
          if data:
            distance = float(data['distance'][0]['value'])
            if distance > door_to_wall:
                if not countdown:
                    countdown = True
                    start_time = time.time()
            else:
                countdown = False
          
          # If a new message (new timestamp) is recieved from ThingsBoard 
          # then the display is updated for 5 seconds (when an item is added
          # on the website.
          if data and 'message' in data:
           time_stamp = data['message'][0]['ts']
           
           if time_stamp != last_time:
            x = 'ADDED!'
            setText(x)
            buzz()
            time.sleep(5)
            x = 'FOODLINK'
            setText(x)
            
           last_time = time_stamp
          
          # Triggers the alarm if the door is left open for two minutes.
          if time.time() - start_time >= delay and countdown:
            alarm()
                
        except KeyboardInterrupt:
            print ("Terminated.")
            os._exit(0)