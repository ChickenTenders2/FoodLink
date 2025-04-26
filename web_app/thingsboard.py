import requests
import logging

# makes sure requests dont retry and wait forever
# stops page reloading taking forever after clicking rapdily
timeout = 3

def get_jwt_token():
    try:
        login_url = "https://thingsboard.cs.cf.ac.uk/api/auth/login"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "username": "group01@cardiff.ac.uk",
            "password": "group012025"
        }

        response = requests.post(login_url, json=data, headers=headers, timeout=timeout)

        if response.status_code == 200:
            token = response.json()['token']
            return token
        else:
            print("Login failed: ", response.json())
    except Exception as e:
        logging.error(f"[get_jwt_token error] {e}")
        return None

def get_telemetry(token, device_id):
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        url = f"https://thingsboard.cs.cf.ac.uk/api/plugins/telemetry/DEVICE/{device_id}/values/timeseries?keys=temperature,humidity"

        response = requests.get(url, headers=headers, timeout=timeout)

        if response.status_code == 401:
            new_token = get_jwt_token()
            if new_token:
                return get_telemetry(new_token, device_id)
            else:
                return None
        elif response.ok:
            return response.json()
        else:
            return None
    except Exception as e:
        logging.error(f"[get_telemetry error] {e}")
        return None
