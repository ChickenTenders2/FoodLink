import mariadb
from flask_sqlalchemy import SQLAlchemy
import logging

# SQLAlchemy for database management
db = SQLAlchemy()

# shared connection for entire app
connection = mariadb.connect(
    host = "81.109.118.20",
    user = "FoodLink",
    password = "Pianoconclusiontown229!",
    database = "FoodLink"
)

def close_connection():
    if connection:
        try:
            logging.info("[INFO] Closing database connection...")
            connection.close()
        except Exception as e:
            logging.warn(f"[WARN] Error while closing connection: {e}")
