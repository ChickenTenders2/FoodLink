import requests
import json

class thingsboard():
    def get_jwt_token(self):
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
            # print('Login successful')
            token = response.json()['token']
            # print("JET token:", token)
            return token
        else:
            print("Login failed: ", response.json())

    def get_telemetry(self, token, device_id):
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        url = f"https://thingsboard.cs.cf.ac.uk/api/plugins/telemetry/DEVICE/{device_id}/values/timeseries?keys=temperature,humidity"

        # s = requests.Session()
        response = requests.get(url, headers=headers)

        if response.status_code == 401:
            # print("Token expired, refreshing...")
            new_token = get_jwt_token()
            if new_token:
                return get_telemetry(new_token, device_id)
            else:
                return None
        elif response.ok:
            data = response.json()
            return data
        else:
            # print("Error: ", response.status_code, response.text)
            return None