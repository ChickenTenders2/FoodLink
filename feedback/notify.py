import time
import requests
import sys
import os
import grovepi
import math
import json


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

def get_telemetry(token, device_id):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
     }

    url = f"https://thingsboard.cs.cf.ac.uk/api/plugins/telemetry/DEVICE/{device_id}/values/timeseries?keys=message"
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

device_id = "15b7a650-0b03-11f0-8ef6-c9c91908b9e2"

token = get_jwt_token()
data = get_telemetry(token, device_id)
temperature = humidity = None
last_time = ""

sensor = 4  # The Sensor goes on digital port 4.
blue = 0    # The Blue colored sensor.

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

# this device has two I2C addresses
DISPLAY_RGB_ADDR = 0x62
DISPLAY_TEXT_ADDR = 0x3e

# set backlight to (R,G,B) (values from 0..255 for each)
def setRGB(r,g,b):
    bus.write_byte_data(DISPLAY_RGB_ADDR,0,0)
    bus.write_byte_data(DISPLAY_RGB_ADDR,1,0)
    bus.write_byte_data(DISPLAY_RGB_ADDR,0x08,0xaa)
    bus.write_byte_data(DISPLAY_RGB_ADDR,4,r)
    bus.write_byte_data(DISPLAY_RGB_ADDR,3,g)
    bus.write_byte_data(DISPLAY_RGB_ADDR,2,b)
 
# send command to display (no need for external use)    
def textCommand(cmd):
    bus.write_byte_data(DISPLAY_TEXT_ADDR,0x80,cmd)
 
# set display text \n for second line(or auto wrap)     
def setText(text):
    textCommand(0x01) # clear display
    time.sleep(.05)
    textCommand(0x08 | 0x04) # display on, no cursor
    textCommand(0x28) # 2 lines
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
 

if __name__=="__main__":

        while True:
          x = 'FOODLINK'
          setText(x)
          data = get_telemetry(token, device_id)
          if data and 'message' in data:
           time_stamp = data['message'][0]['ts']
           if time_stamp != last_time:
            setRGB(0,128,64)
            time.sleep(2)
            try:
                time.sleep(3)
                x = 'ADDED!'
                setText(x)
                time.sleep(5)
            except KeyboardInterrupt:
                print ("Terminated.")
                os._exit(0)

            last_time = time_stamp

