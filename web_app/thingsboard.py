import requests
import logging
from os import getenv as get_dotenv

# makes sure requests dont retry and wait forever
# stops page reloading taking forever after clicking rapdily
timeout = 3

login_url = f"{get_dotenv('THINGSBOARD_API')}/api/auth/login"
headers = {
    "Content-Type": "application/json"
}
data = {
    "username": get_dotenv("THINGSBOARD_USER"),
    "password": get_dotenv("THINGSBOARD_PASS")
}
# Authenticates with ThingsBoard and retrieves a JWT token
def get_jwt_token():
    try:
        # Send POST request to login endpoint
        response = requests.post(login_url, json=data, headers=headers, timeout=timeout)

        if response.status_code == 200:
            # If successful, extract and return the JWT token
            token = response.json()['token']
            return token
        else:
             # Log failure with response details
             logging.error(f"[get_jwt_token error] Login Failed: {response.json()}")
    except Exception as e:
        # Log any exception that occurs during the request
        logging.error(f"[get_jwt_token error] {e}")
        return None

# Retrieves temperature and humidity telemetry for a given device
def get_telemetry(token, device_id):
    try:
        headers = {
            "Authorization": f"Bearer {token}", # Use the provided token
            "Content-Type": "application/json"
        }

        # URL to fetch latest timeseries data for temperature and humidity
        url = f"https://thingsboard.cs.cf.ac.uk/api/plugins/telemetry/DEVICE/{device_id}/values/timeseries?keys=temperature,humidity"

         # Send GET request to fetch telemetry
        response = requests.get(url, headers=headers, timeout=timeout)

        if response.status_code == 401:
            # If unauthorized, attempt to get a new token and retry once
            new_token = get_jwt_token()
            if new_token:
                return get_telemetry(new_token, device_id)
            else:
                return None
        elif response.ok:
            # If successful, return parsed JSON response
            return response.json()
        else:
            # Return None for any non-200 response
            return None
    except Exception as e:
        # Log unexpected exceptions
        logging.error(f"[get_telemetry error] {e}")
        return None
