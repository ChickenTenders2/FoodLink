from database import database

class tool(database):
    def __init__(self):
        super().__init__()
    
    def add_tool(self, name, tool_type):
        cursor = self.connection.cursor()
        query = "INSERT INTO tool (name, type) VALUES (%s, %s);"
        data = (name, tool_type)
        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()

    def get_utensils(self):
        cursor = self.connection.cursor()
        query = "SELECT id, name FROM tool2 WHERE type = 'utensil';"
        cursor.execute(query)
        utensils = cursor.fetchall()
        cursor.close()
        return utensils

    def get_appliances(self):
        cursor = self.connection.cursor()
        query = "SELECT id, name FROM tool2 WHERE type = 'appliance';"
        cursor.execute(query)
        appliances = cursor.fetchall()
        cursor.close()
        return appliances
    
    def get_user_tool_ids(self, user_id):
        cursor = self.connection.cursor()
        query = "SELECT tool_id FROM user_tool WHERE user_id = %s;"
        data = (user_id,)
        cursor.execute(query, data)
        ids = cursor.fetchall()
        cursor.close()
        ids = [id[0] for id in ids]
        return ids

    def save_user_tools(self, user_id, tool_ids):
        cursor = self.connection.cursor()
        query = "DELETE FROM user_tool WHERE user_id = %s;"
        data = (user_id,)
        cursor.execute(query, data)

        query = "INSERT INTO user_tool (user_id, tool_id) VALUES (%s, %s);"
        # creates list of the data needed to execute each query for storing user tools
        data = [(user_id, tool_id) for tool_id in tool_ids]
        # executes all queries
        cursor.executemany(query, data)
        self.connection.commit()
        cursor.close()

