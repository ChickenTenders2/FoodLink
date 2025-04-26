import mariadb
import logging


# lambda function to create a new connection
create_connection = lambda: mariadb.connect(
    host="81.109.118.20",
    user="FoodLink",
    password="Pianoconclusiontown229!",
    database="FoodLink"
)

# Shared connection for the entire app
connection = create_connection()

def get_connection():
    global connection
    try:
        connection.ping()
    except mariadb.InterfaceError as e:
        logging.error(f"[ERROR] Lost connection, reconnecting: {e}")
        try:
            connection = create_connection()
            logging.info("[INFO] Reconnected to database.")
        except Exception as reconnect_error:
            logging.error(f"[ERROR] Failed to reconnect to database: {reconnect_error}")
            # sends error back to flask route so it returns request with 500
            raise Exception("Failed to reconnect to database.")
    return connection

def get_cursor():
    connect = get_connection()
    return connect.cursor()

def commit():
    connection.commit()

def safe_rollback():
    global connection
    try:
        connection.rollback()
    except mariadb.InterfaceError as e:
        logging.error(f"[ERROR] Rollback failed, connection lost: {e}")
        try:
            connection = create_connection()
            logging.info("[INFO] Reconnected to database after rollback failure.")
        except Exception as reconnect_error:
            logging.error(f"[ERROR] Failed to reconnect after rollback: {reconnect_error}")
            # sends error back to flask route so it returns request with 500
            raise Exception("Failed to reconnect to database.")
    except Exception as e:
        logging.error(f"[ERROR] Rollback failed: {e}")

def close_connection():
    global connection
    if connection:
        try:
            logging.info("[INFO] Closing database connection...")
            connection.close()
        except Exception as e:
            logging.warning(f"[WARN] Error while closing connection: {e}")
