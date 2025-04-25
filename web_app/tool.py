from database import connection

def add_tool(name, tool_type):
    cursor = None
    try:
        cursor = connection.cursor()
        query = "INSERT INTO tool (name, type) VALUES (%s, %s);"
        data = (name, tool_type)
        cursor.execute(query, data)
        connection.commit()
        return {"success": True}
    except Exception as e:
        print(f"[add_tool error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def get_tools(type=None):
    cursor = None
    try:
        cursor = connection.cursor()
        if type:
            query = "SELECT id, name FROM tool WHERE type = %s ORDER BY name;"
            data = (type,)
            cursor.execute(query, data)
        else:
            query = "SELECT id, name FROM tool ORDER BY type, name;"
            cursor.execute(query)
        tools = cursor.fetchall()
        return {"success": True, "tools": tools}
    except Exception as e:
        print(f"[get_tools error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def get_user_tool_ids(user_id):
    cursor = None
    try:
        cursor = connection.cursor()
        # gets the tool_id for each tool a user has selected previously
        query = "SELECT tool_id FROM user_tool WHERE user_id = %s;"
        data = (user_id,)
        cursor.execute(query, data)
        ids = cursor.fetchall()
        # formats each id into a list
        ids = [id[0] for id in ids]
        return {"success": True, "ids": ids}
    except Exception as e:
        print(f"[get_user_tool_ids error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def save_user_tools(user_id, tool_ids):
    cursor = None
    try:
        cursor = connection.cursor()
        # removes all tools so any unhighlighted options are removed
        query = "DELETE FROM user_tool WHERE user_id = %s;"
        data = (user_id,)
        cursor.execute(query, data)

        # stops inserting tools if none were selected
        if not tool_ids:
            return {"success": False, "error": "No tools were selected."}

        query = "INSERT INTO user_tool (user_id, tool_id) VALUES (%s, %s);"
        # creates list of the data needed to execute each query for storing user tools
        data = [(user_id, tool_id) for tool_id in tool_ids]
        # executes all queries
        cursor.executemany(query, data)
        connection.commit()
        return {"success": True}
    except Exception as e:
        print(f"[save_user_tools error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()
