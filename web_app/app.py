from flask import Flask, jsonify, render_template, request, redirect, url_for, session
import os


app = Flask(__name__, template_folder="templates")
app.secret_key = os.urandom(24)



# Dashboard Route

# Login Route

# Register Route

# Logout Route

# Inventory Interface Route

# Shopping List Interface Route

if __name__ == '__main__':
    app.run(debug=True)