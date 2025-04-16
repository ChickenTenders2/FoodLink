import mariadb
import requests
from datetime import datetime, timedelta

class database():
    def __init__(self):
        self.connection = self.connect()

    # returns db connection
    def connect(self):
        return mariadb.connect(
            host = "81.109.118.20",
            user = "FoodLink",
            password = "Pianoconclusiontown229!",
            database = "FoodLink"
        ) # old ip: 80.0.43.124

class notification(database):
    def get_notifications(self, user_id):
        cursor = self.connection.cursor()
        query = "SELECT id, type, message, date_created, is_read, severity FROM notification WHERE user_id = %s ORDER BY date_created DESC;"
        data = (user_id,)
        cursor.execute(query, data)
        notifications = cursor.fetchall()
        cursor.close()
        return notifications

    def temperature_humidity_notification(self, user_id, temperature, humidity):
        cursor = self.connection.cursor()
        query = "SELECT min_temperature, max_temperature, max_humidity, temperature_alerts FROM settings WHERE user_id = %s;"
        data = (user_id,)
        cursor.execute(query, data)
        settings = cursor.fetchone()

        print(settings)

        if settings:
            min_temperature = settings[0]
            max_temperature = settings[1]
            max_humidity = settings[2]
            alerts_enabled = settings[3]
                
        temperature = float(temperature)
        humidity = float(humidity)
        min_temperature = float(min_temperature)
        max_temperature = float(max_temperature)
        max_humidity = float(max_humidity)
        
        if alerts_enabled:
            if temperature is not None:
                temperature = round(temperature, 2)
                notif_type = 'temperature'
                if temperature < min_temperature:
                    message = f"Low temperature detected: {temperature}°C"
                    is_exists = self.notification_exists(user_id, notif_type, message)
                    if is_exists == 0:
                        self.insert_notification(user_id, notif_type, message, severity)
                elif temperature > max_temperature:
                    message = f"High temperature detected: {temperature}°C"
                    is_exists = self.notification_exists(user_id, notif_type, message)
                    if is_exists == 0:
                        self.insert_notification(user_id, notif_type, message, severity)
                
            if humidity is not None:
                humidity = round(humidity, 2)
                if humidity > max_humidity:
                    notif_type = 'humidity'
                    message = f"High humidity detected: {humidity}%"
                    is_exists = self.notification_exists(user_id, notif_type, message)
                    if is_exists == 0:
                        self.insert_notification(user_id, notif_type, message, severity)
        cursor.close()

    def expiry_notification(self, user_id):
        cursor = self.connection.cursor()
        # query = "SELECT expiry_date FROM inventory WHERE user_id = %s"
        query = "SELECT inv.id, i.id, i.name, expiry_date FROM FoodLink.inventory inv JOIN FoodLink.item i ON (inv.item_id = i.id) WHERE inv.user_id = %s;"
        data = (user_id,)
        cursor.execute(query, data)
        expiries = cursor.fetchall()

        today = datetime.today().date()
        notif_type = 'expiry'
        message = ''
        severity = ''

        for item in expiries:
            item_name = item[2]
            expiry_date = item[3]

            if isinstance(expiry_date, datetime):
                expiry_date = expiry_date.date()
            
            daysLeft = (expiry_date - today).days

            if daysLeft == 2:
                message = f"{item_name} will expire in 2 days."
                severity = 'info'
            elif daysLeft == 1:
                message = f"{item_name} will expire tomorrow!"
                severity = 'warning'
            elif daysLeft == 0:
                message = f"{item_name} expires today!"
                severity = 'critical'
            elif daysLeft < 0:
                message = f"{item_name} has expired!"
                severity = 'critical'
            # else:
            #     continue
            
            is_exists = self.notification_exists(user_id, notif_type, message)
            if is_exists == 0:
                self.insert_notification(user_id, notif_type, message, severity)
        cursor.close()

    def support_notification(self, user_id, message):
        insert_notification(user_id, 'support', message, 'info')

    def notification_exists(self, user_id, notif_type, message):
        cursor = self.connection.cursor()
        query = "SELECT COUNT(*) FROM notification WHERE user_id = %s AND type = %s AND message = %s;"
        data = (user_id, notif_type, message)
        cursor.execute(query, data)
        is_exists = cursor.fetchone()[0]
        return is_exists

    def insert_notification(self, user_id, notif_type, message, severity):
        cursor = self.connection.cursor()
        query = "INSERT INTO notification (user_id, type, message, date_created, is_read, severity) VALUES (%s, %s, %s, NOW(), 0, %s)"
        data = (user_id, notif_type, message, severity)
        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()

    def mark_read(self, notif_id):
        cursor = self.connection.cursor()
        query = "UPDATE notification SET is_read = 1 WHERE id = %s"
        data = (notif_id,)
        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()
