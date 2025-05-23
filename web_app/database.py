import mariadb
import logging
from os import getenv
from dotenv import load_dotenv

load_dotenv()

# lambda function to create a new connection
create_connection = lambda: mariadb.connect(
    host=getenv("DB_HOST"),
    user=getenv("DB_USER"),
    password=getenv("DB_PASS"),
    database=getenv("DB_NAME")
)

# Shared connection for the entire app
connection = create_connection()

def get_connection():
    """
    Returns a valid MariaDB connection object.
    Checks if the current connection is alive using .ping().
    If not, attempts to reconnect and logs the process.
    
    Raises:
        Exception: If reconnection fails.
    
    Returns:
        mariadb.Connection: Active MariaDB connection.
    """
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
    """
    Returns a new cursor from the active database connection.
    
    Returns:
        mariadb.Cursor: New cursor for executing SQL queries.
    """
    connect = get_connection()
    return connect.cursor()

def commit():
    """
    Commits the current transaction to the database.
    """
    connection.commit()

def safe_rollback():
    """
    Attempts to rollback the current transaction.
    If the connection is lost, tries to reconnect and logs the event.
    Raises an exception if reconnection fails.
    """
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
    """
    Closes the current database connection gracefully.
    Logs any error encountered during the close operation.
    """
    global connection
    if connection:
        try:
            logging.info("[INFO] Closing database connection...")
            connection.close()
        except Exception as e:
            logging.warning(f"[WARN] Error while closing connection: {e}")
