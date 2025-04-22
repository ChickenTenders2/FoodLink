from database import database
from datetime import datetime
import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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
            # compare temperature against temperature thresholds and send notification to user if it exceeds
            if temperature is not None:
                temperature = round(temperature, 2)
                notif_type = 'temperature'
                if temperature < min_temperature:
                    message = f"Low temperature detected: {temperature}°C"
                    if not self.cooldown_check(user_id, notif_type):
                        self.insert_notification(user_id, notif_type, message, 'warning')
                        self.send_email(
                            user_id=user_id,
                            subject_type=notif_type,
                            message_text=f"Warning: Your fridge temperature is BELOW the maximum threshold {min_temperature}°C. TEMPERATURE DETECTED: {temperature}°C"
                        )
                elif temperature > max_temperature:
                    message = f"High temperature detected: {temperature}°C"
                    if self.cooldown_check(user_id, notif_type) == False:
                        self.insert_notification(user_id, notif_type, message, 'critical')
                        self.send_email(
                            user_id=user_id,
                            subject_type=notif_type,
                            message_text=f"Warning: Your fridge temperature is above the maximum threshold {max_temperature}°C. TEMPERATURE DETECTED: {temperature}°C"
                        )
            # compare humdity against humidity threshold and send notification to user if it exceeds threshold  
            if humidity is not None:
                humidity = round(humidity, 2)
                if humidity > max_humidity:
                    notif_type = 'humidity'
                    message = f"High humidity detected: {humidity}%"
                    if not self.cooldown_check(user_id, notif_type):
                        self.insert_notification(user_id, notif_type, message, 'warning')
                        self.send_email(
                            user_id=user_id,
                            subject_type=notif_type,
                            message_text=f"Warning: Your fridge humidity is above the maximum threshold {max_humidity}%. HUMIDITY DETECTED: {humidity}%"
                        )
        cursor.close()

    def expiry_notification(self, user_id):
        cursor = self.connection.cursor()
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

            # handling alert severity based on days left to expiration
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
            # the notification will be sent only if it doesn;t already exist
            if is_exists == 0:
                self.insert_notification(user_id, notif_type, message, severity)
        cursor.close()

    def support_notification(self, user_id, message):
        self.insert_notification(user_id, 'support', message, 'info')

    # checks for duplicate notification
    def notification_exists(self, user_id, notif_type, message):
        cursor = self.connection.cursor()
        query = "SELECT COUNT(*) FROM notification WHERE user_id = %s AND type = %s AND message = %s;"
        data = (user_id, notif_type, message)
        cursor.execute(query, data)
        exact_exists = cursor.fetchone()[0]
        cursor.close()
        return exact_exists

    # add notifications into the notification table
    def insert_notification(self, user_id, notif_type, message, severity):
        cursor = self.connection.cursor()
        query = "INSERT INTO notification (user_id, type, message, date_created, is_read, severity) VALUES (%s, %s, %s, NOW(), 0, %s)"
        data = (user_id, notif_type, message, severity)
        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()

    # chnages the is_read value from 0 to 1 when user reads the notification and clicks it to confirm read
    def mark_read(self, notif_id):
        cursor = self.connection.cursor()
        query = "UPDATE notification SET is_read = 1 WHERE id = %s"
        data = (notif_id,)
        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()

    def cooldown_check(self, user_id, notif_type, cooldown_minutes=5):
        # """
        # Returns True if a notification of the given type was sent within cooldown_minutes.
        # Otherwise returns False, meaning it's okay to send a new one.
        # """
        cursor = self.connection.cursor()
        query = """
            SELECT date_created FROM notification 
            WHERE user_id = %s AND type = %s 
            ORDER BY date_created DESC; 
        """
        cursor.execute(query, (user_id, notif_type))
        result = cursor.fetchone()
        print(result)
        cursor.close()

        print(result)

        if result:
            last_time = result[0]

            if isinstance(last_time, str):  # If stored as string
                last_time = datetime.strptime(last_time, "%Y-%m-%d %H:%M:%S")

            now = datetime.now()
            diff_in_seconds = (now - last_time).total_seconds()

            print(f"[DEBUG] Last notification at: {last_time}")
            print(f"[DEBUG] Current time: {now}")
            print(f"[DEBUG] Seconds since last: {diff_in_seconds}")

            if diff_in_seconds < cooldown_minutes * 60:
                return True  # Cooldown active

        return False


    def send_email(self, user_id, subject_type, message_text):
        cursor = self.connection.cursor()
        query = "SELECT email_notifications FROM FoodLink.settings WHERE user_id = %s;"
        data = (user_id,)
        cursor.execute(query, data)
        email_enabled = cursor.fetchone()

        email_query = "SELECT email FROM FoodLink.user WHERE id = %s;"
        email_data = (user_id,)
        cursor.execute(email_query, email_data)
        recipient_email = cursor.fetchone()[0]
        cursor.close()

        # Define subject labels and styles per type
        subjects = {
            "temperature": {
                "title": "Temperature Alert",
                "color": "#f44336",  # red
            },
            "humidity": {
                "title": "Humidity Alert",
                "color": "#ff9800",  # orange
            },
            "expiry": {
                "title": "Item Expiry Notification",
                "color": "#ffd54f",  # yellow
            },
            "support": {
                "title": "Support Message",
                "color": "#4caf50",  # green
            }
        }

        notif = subjects.get(subject_type, {
        "title": "Notification",
        "color": "#90caf9"  # default blue
        })

        if email_enabled:
            # Set up the email
            msg = MIMEMultipart("alternative")
            msg['Subject'] = notif["title"]
            msg['From'] = "foodlink2305@gmail.com"
            msg['To'] = recipient_email

            html = f"""
            <html>
            <head>
                <style>
                    .container {{
                        font-family: Arial, sans-serif;
                        background-color: #f9f9f9;
                        padding: 20px;
                    }}
                    .card {{
                        background-color: white;
                        padding: 20px;
                        border-radius: 10px;
                        border-left: 6px solid {notif['color']};
                        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                        max-width: 500px;
                        margin: auto;
                    }}
                    .title {{
                        font-size: 20px;
                        font-weight: bold;
                        color: {notif['color']};
                        margin-bottom: 10px;
                    }}
                    .message {{
                        font-size: 16px;
                        color: #444;
                    }}
                    .footer {{
                        margin-top: 20px;
                        font-size: 12px;
                        color: #999;
                        text-align: center;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="card">
                        <div class="title">{notif['title']}</div>
                        <div class="message">{message_text}</div>
                        <div class="footer">FoodLink • Smart Fridge Assistant</div>
                    </div>
                </div>
            </body>
            </html>
            """

            msg.attach(MIMEText(html, "html", _charset="utf-8"))

            # Connect to Gmail SMTP
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login("foodlink2305@gmail.com", "fimz txhp fhwk qwbk")
                server.sendmail("foodlink2305@gmail.com", recipient_email, msg.as_string())