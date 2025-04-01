from flask import Flask, request, jsonify
import mariadb
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database connection details
HOST = "80.0.43.124"
USER = "FoodLink"
PASSWORD = "Pianoconclusiontown229!"
DATABASE = "FoodLink"

def get_db_connection():
    return mariadb.connect(
        host=HOST, user=USER, password=PASSWORD, database=DATABASE
    )

@app.route("/get-utensils", methods=["GET"])
def get_utensils():
    user_id = request.args.get('user_id')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all kitchen tools from database
        cursor.execute("SELECT name FROM tool WHERE type = 'kitchen'")
        all_utensils = [row[0] for row in cursor.fetchall()]
        
        # Get user's selected utensils if user_id provided
        user_utensils = []
        if user_id:
            cursor.execute("""
                SELECT t.name 
                FROM tool t 
                JOIN user_tool ut ON t.id = ut.tool_id 
                WHERE ut.user_id = ?
            """, (user_id,))
            user_utensils = [row[0] for row in cursor.fetchall()]
        
        return jsonify({
            "all_utensils": all_utensils, 
            "user_utensils": user_utensils
        })
    except mariadb.Error as e:
        return jsonify({"error": str(e)})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route("/save-utensils", methods=["POST"])
def save_utensils():
    data = request.json
    user_id = data.get("user_id")
    selected_utensils = data.get("utensils", [])
    
    if not user_id:
        return jsonify({"error": "User ID is required"})
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Clear existing utensils for this user
        cursor.execute("DELETE FROM user_tool WHERE user_id = ?", (user_id,))
        
        # Insert new utensils
        for utensil in selected_utensils:
            # Get the tool_id for the utensil
            cursor.execute("SELECT id FROM tool WHERE name = ?", (utensil,))
            result = cursor.fetchone()
            if result:
                tool_id = result[0]
                cursor.execute("INSERT INTO user_tool (user_id, tool_id) VALUES (?, ?)", 
                               (user_id, tool_id))
        
        conn.commit()
        
        # Get the updated list of user's utensils
        cursor.execute("""
            SELECT t.name 
            FROM tool t 
            JOIN user_tool ut ON t.id = ut.tool_id 
            WHERE ut.user_id = ?
        """, (user_id,))
        user_utensils = [row[0] for row in cursor.fetchall()]
        
        return jsonify({
            "message": "Utensils saved successfully!", 
            "user_utensils": user_utensils
        })
    except mariadb.Error as e:
        return jsonify({"error": str(e)})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')  # Listen on all interfaces
