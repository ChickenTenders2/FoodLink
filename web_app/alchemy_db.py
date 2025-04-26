from flask_sqlalchemy import SQLAlchemy
# for cathcing connection failed errors
from sqlalchemy.exc import DBAPIError
import logging

# SQLAlchemy for database management
db = SQLAlchemy()

# *args **kwargs means variables can be parsed without using lambda
def safe_execute(func, *args, **kwargs):
    try:
        # parses variables to function
        return func(*args, **kwargs)
    except Exception as e:
        # if error is a dead connection
        if isinstance(e, DBAPIError) and e.connection_invalidated:
            logging.error(f"[ERROR] Database connection lost during operation: {e}")
            reconnect_session()
        else:
            logging.error(f"[ERROR] Alchemy operation failed: {e}")
            safe_rollback()
        # sends general error back to flask (so users cant see details)
        raise DBAPIError("A database error occurred. Please try again later.")

# any db command using alchemy must be rolledback upon failure (even .get i.e. SELECT)
def safe_rollback():
    try:
        db.session.rollback()
    except Exception as e:
        logging.error(f"[ERROR] Rollback also failed after operation failure: {e}")

def reconnect_session():
    try:
        logging.info("[INFO] Reconnecting SQLAlchemy session...")
        # closes broken session
        db.session.close() 
        # fully closes old connections
        db.engine.dispose()  
        # after disposing, the next use of db.session will automatically reconnect to db
    except Exception as e:
        logging.error(f"[ERROR] Failed to reconnect SQLAlchemy session: {e}")
        raise DBAPIError("Failed to reconnect to the database.")

