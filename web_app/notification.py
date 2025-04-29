from database import get_cursor, commit, safe_rollback
import logging
from datetime import datetime, date
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email import charset

def get_notifications(user_id):
    cursor = None
    try:
        cursor = get_cursor()
        query = """
            SELECT id, type, message, date_created, is_read, severity
            FROM notification
            WHERE user_id = %s
            ORDER BY date_created DESC;
        """
        cursor.execute(query, (user_id,))
        notifications = cursor.fetchall()
        return {"success": True, "notifications": notifications}
    except Exception as e:
        logging.error(f"[get_notifications error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

# changes the is_read value from 0 to 1 when user reads the notification and clicks it to confirm read
def mark_read(notif_id):
    cursor = None
    try:
        cursor = get_cursor()
        query = "UPDATE notification SET is_read = 1 WHERE id = %s;"
        cursor.execute(query, (notif_id,))
        commit()
        return {"success": True}
    except Exception as e:
        safe_rollback()
        logging.error(f"[mark_read error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

# checks for duplicate notification
def notification_exists(user_id, notif_type, message):
    cursor = None
    try:
        cursor = get_cursor()
        query = "SELECT COUNT(*) FROM notification WHERE user_id = %s AND type = %s AND message = %s;"
        cursor.execute(query, (user_id, notif_type, message))
        count = cursor.fetchone()[0]
        return count != 0
    except Exception as e:
        logging.error(f"[notification_exists error] {e}")
        # set as true even with error so duplicate notifications do not occur
        return True
    finally:
        if cursor:
            cursor.close()

# add notifications into the notification table
def insert_notification(user_id, notif_type, message, severity):
    cursor = None
    try:
        cursor = get_cursor()
        query = """
            INSERT INTO notification (user_id, type, message, date_created, is_read, severity)
            VALUES (%s, %s, %s, NOW(), 0, %s);
        """
        cursor.execute(query, (user_id, notif_type, message, severity))
        commit()
        return {"success": True}
    except Exception as e:
        safe_rollback()
        logging.error(f"[insert_notification error] {e}")
        # deatiled report of error for admins
        return {"success": False, 
                "error": f"""[insert_notification error]:
                Inputs: 
                user_id: {user_id},
                notif_type: {notif_type},
                message: {message},
                severity: {severity},
                Error: {e}"""
            }
    finally:
        if cursor:
            cursor.close()

def support_notification(user_id, message):
    send_email(user_id, 'support', message)
    return insert_notification(user_id, 'support', message, 'info')

def expiry_notification(user_id):
    cursor = None
    try:
        cursor = get_cursor()

        settings_query = "SELECT expiring_food FROM FoodLink.settings WHERE user_id = %s;"
        cursor.execute(settings_query, (user_id,))
        settings = cursor.fetchone()

        if not settings or not settings[0]:
            return

        query = """
            SELECT i.name, expiry_date
            FROM FoodLink.inventory inv
            JOIN FoodLink.item i ON (inv.item_id = i.id)
            WHERE inv.user_id = %s;
        """
        cursor.execute(query, (user_id,))
        expiries = cursor.fetchall()
        today = date.today()
        # expiry_date is parsed from mariadb as datetime.date object
        for name, expiry_date in expiries:
            days_left = (expiry_date - today).days
            if days_left == 2:
                message, severity = f"{name} will expire in 2 days.", "info"
            elif days_left == 1:
                message, severity = f"{name} will expire tomorrow!", "warning"
            elif days_left == 0:
                message, severity = f"{name} expires today!", "critical"
            elif days_left < 0:
                message, severity = f"{name} has expired!", "critical"
            else:
                continue
            if not notification_exists(user_id, 'expiry', message):
                insert_notification(user_id, 'expiry', message, severity)
                send_email(user_id, 'expiry', f"{message} Please check your inventory.")
    except Exception as e:
        logging.error(f"[expiry_notification error] {e}")
    finally:
        if cursor:
            cursor.close()

def temperature_humidity_notification(user_id, temperature, humidity):
    cursor = None
    try:
        cursor = get_cursor()
        # retrieve user settings
        cursor.execute("SELECT min_temperature, max_temperature, max_humidity, temperature_alerts FROM settings WHERE user_id = %s;", (user_id,))
        settings = cursor.fetchone()
        if not settings:
            return
        min_temp, max_temp, max_hum, alerts_enabled = float(settings[0]), float(settings[1]), float(settings[2]), settings[3]
        if not alerts_enabled:
            return
        if temperature is not None:
            temperature = round(float(temperature), 2)
            notif_type = 'temperature'
            #check temperture against thresholds
            if temperature < min_temp:
                message = f"Low temperature detected: {temperature}°C"
                # send new notification if cooldown minutes are satisfied
                if not cooldown_check(user_id, notif_type):
                    insert_notification(user_id, notif_type, message, 'warning')
                    send_email(user_id, notif_type, f"Warning: Your fridge temperature is below {min_temp}°C.\nDetected: {temperature}°C")
            elif temperature > max_temp:
                message = f"High temperature detected: {temperature}°C"
                # send new notification if cooldown minutes are satisfied
                if not cooldown_check(user_id, notif_type):
                    insert_notification(user_id, notif_type, message, 'critical')
                    send_email(user_id, notif_type, f"Warning: Your fridge temperature is above {max_temp}°C.\nDetected: {temperature}°C")
        if humidity is not None:
            humidity = round(float(humidity), 2)
            # check humidity aginst threshold
            if humidity > max_hum:
                notif_type = 'humidity'
                message = f"High humidity detected: {humidity}%"
                # send new notification if cooldown minutes are satisfied
                if not cooldown_check(user_id, notif_type):
                    insert_notification(user_id, notif_type, message, 'warning')
                    send_email(user_id, notif_type, f"Warning: Your fridge humidity is above {max_hum}%.\nDetected: {humidity}%")
    except Exception as e:
        logging.error(f"[temperature_humidity_notification error] {e}")
    finally:
        if cursor:
            cursor.close()

def cooldown_check(user_id, notif_type, cooldown_minutes=10):
    # """
    # Returns True if a notification of the given type was sent within cooldown_minutes.
    # Otherwise returns False, meaning it's okay to send a new one.
    # """
    cursor = None
    try:
        cursor = get_cursor()
        query = """
            SELECT date_created FROM notification 
            WHERE user_id = %s AND type = %s 
            ORDER BY date_created DESC LIMIT 1;
        """
        cursor.execute(query, (user_id, notif_type))
        result = cursor.fetchone()
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
    except Exception as e:
        logging.error(f"[cooldown_check error] {e}")
        return True 
    finally:
        if cursor:
            cursor.close()


def send_email(user_id, subject_type, message_text):
    cursor = None
    try:
        cursor = get_cursor()
        cursor.execute("SELECT email_notifications FROM settings WHERE user_id = %s;", (user_id,))
        enabled = cursor.fetchone()
        if not enabled or not enabled[0]:
            return {"success": True}
        cursor.execute("SELECT email FROM user WHERE id = %s;", (user_id,))
        recipient_email = cursor.fetchone()[0]
    except Exception as e:
        logging.error(f"[send_email DB error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()
    # Define subject labels and styles per type
    subjects = {
        "temperature": {"title": "Temperature Alert", "color": "#f44336"}, #red
        "humidity": {"title": "Humidity Alert", "color": "#ff9800"}, #orange
        "expiry": {"title": "Item Expiry Notification", "color": "#ffd54f"}, #yellow
        "support": {"title": "Support Message", "color": "#4caf50"}, #green
    }
    notif = subjects.get(subject_type, {"title": "Notification", "color": "#90caf9"})
    charset.add_charset('utf-8', charset.SHORTEST, None, 'utf-8')
    # Set up the email
    msg = MIMEMultipart("alternative")
    # encoding for header
    msg['Subject'] = Header(notif["title"], 'utf-8')
    msg['From'] = "foodlink2305@gmail.com"
    msg['To'] = recipient_email
    ## encoding for message
    msg.set_charset("utf-8")
    html = f"""
    <html><body><div style="border-left:6px solid {notif['color']}; padding:16px;">
        <h2 style="color:{notif['color']};">{notif['title']}</h2>
        <p>{message_text}</p>
        <small style="color: #999;">FoodLink • Smart Fridge Assistant</small>
    </div></body></html>
    """
    msg.attach(MIMEText(html, "html", _charset="utf-8"))
    try:
        # Connect to Gmail SMTP
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login("foodlink2305@gmail.com", "fimz txhp fhwk qwbk")
            server.sendmail("foodlink2305@gmail.com", recipient_email, msg.as_bytes())
        return {"success": True}
    except Exception as e:
        logging.error(f"[send_email SMTP error] {e}")
        return {"success": False, "error": "An internal error occurred."}
