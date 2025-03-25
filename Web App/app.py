from flask import Flask, render_template, request, redirect, url_for, session
import mariadb
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database connection function
def get_db_connection():
    return mariadb.connect(
        host = "foodlink.ddns.net",
        user = "FoodLink",
        password = "Pianoconclusiontown229!",
        database = "FoodLink"
    )

# Dashboard Route

# Login Route

# Register Route

# Logout Route

# Inventoy Interface Route

if __name__ == '__main__':
    app.run(debug=True)