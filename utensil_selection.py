from flask import Flask, jsonify, render_template, request
import mariadb

app = Flask(__name__)

# Database connection
def get_db_connection():
    return mariadb.connect(
        host="80.0.43.124",
        user="FoodLink",
        password="Pianoconclusiontown229!",
        database="FoodLink"
    )

# Linking to utensil selection page
@app.route("/")
def index():
    return render_template("UtensilSelection.html")

# Getting utensils from database
@app.route("/utensils")
def get_utensils():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM tool")
        utensils = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
        conn.close()
        return jsonify(utensils)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Save selected utensils to database for a user
@app.route("/save_selection", methods=["POST"])
def save_selection():
    try:
        data = request.json
        user_id = 1  # Change this to dynamic user authentication later
        selected_utensils = data.get("utensils", [])

        conn = get_db_connection()
        cursor = conn.cursor()

        # Clear previous selection
        cursor.execute("DELETE FROM user_tools WHERE user_id = ?", (user_id,))

        # Insert new selection
        for utensil_id in selected_utensils:
            cursor.execute("INSERT INTO user_tools (user_id, tool_id) VALUES (?, ?)", (user_id, utensil_id))

        conn.commit()
        conn.close()

        return jsonify({"message": "Utensils saved successfully!"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
