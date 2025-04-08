class database():
    def __init__(self):
        self.connection = self.connect()

    # returns db connection
    def connect(self):
        return mariadb.connect(
            host = "80.0.43.124",
            user = "FoodLink",
            password = "Pianoconclusiontown229!",
            database = "FoodLink"
        )

class notification(database):
    def temperature_humidity_notification(self, user_id, temperature, humidity):
        cursor = self.connection.cursor()
        query = "SELECT min_temperature, max_temperature, max_humidity, temperature_alerts FROM settings WHERE user_id = %s;"
        data = (user_id,)
        cursor.execute(query, data)
        settings = cursor.fetchone()

        if settings:
            min_temperature, max_humidity, max_humidity, alerts_enabled = settings
        
        if alerts_enabled:
            if temperature is not None:
                if temperature < min_temperature:
                    query = "INSERT INTO notification (user_id, type, message, date_created, read, severity) VALUES (%s, 'temperature', %s, NOW(), 0, 'warning')"
                    data = (user_id, f"Low temperature detected: {temperature}°C")
                elif temperature > max_temperature:
                    query = "INSERT INTO notification (user_id, type, message, date_created, read, severity) VALUES (%s, 'temperature', %s, NOW(), 0, 'critical')"
                    data = (user_id, f"High temperature detected: {temperature}°C")
                
            if humidity is not None:
                if humidity > max_humidity:
                    query = "INSERT INTO notification (user_id, type, message, date_created, read, severity) VALUES (%s, 'humidity', %s, NOW(), 0, 'warning')"
                    data = (user_id, f"High humidity detected: {humidity}%")
