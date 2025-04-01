from flask import Flask, request, jsonify
import mariadb

app = Flask(__name__)

# Database connection details
HOST = "80.0.43.124"
USER = "FoodLink"
PASSWORD = "Pianoconclusiontown229!"
DATABASE = "FoodLink"

def get_db_connection():
    return mariadb.connect(
        host=HOST, user=USER, password=PASSWORD, database=DATABASE
    )

#common kitchen utensils
COMMON_UTENSILS = [
    "Knife", "Cutting Board", "Frying Pan", "Saucepan", "Oven", "Microwave",
    "Blender", "Whisk", "Grater", "Rolling Pin", "Toaster", "Pressure Cooker",
    "AirFrier"
]

@app.route("/get-utensils", methods=["GET"])
def get_utensils():
    return jsonify(COMMON_UTENSILS)

@app.route("/save-utensils", methods=["POST"])
def save_utensils():
    data = request.json
    user_id = data.get("user_id")
    selected_utensils = data.get("utensils", [])

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Clear existing utensils for this user
        cursor.execute("DELETE FROM user_tool WHERE user_id = ?", (user_id,))

        # Insert new utensils
        for utensil in selected_utensils:
            cursor.execute("INSERT INTO user_tool (user_id, tool_id) SELECT ?, id FROM tool WHERE name = ?", (user_id, utensil))

        conn.commit()

        # Get the updated list of user's utensils
        cursor.execute("SELECT t.name FROM tool t JOIN user_tool ut ON t.id = ut.tool_id WHERE ut.user_id = ?", (user_id,))
        user_utensils = [row[0] for row in cursor.fetchall()]

        return jsonify({"message": "Utensils saved successfully!", "user_utensils": user_utensils})

    except mariadb.Error as e:
        return jsonify({"error": str(e)})

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    app.run(debug=True)
