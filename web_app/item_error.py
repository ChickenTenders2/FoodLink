from database import database

class item_error(database):
    def __init__(self):
        super().__init__()

    def add_report(self, new_item_id, item_id, user_id):
        cursor = self.connection.cursor()
        query = "INSERT INTO item_error (new_item_id, item_id, error_type, user_id, date_created) VALUES (%s, %s, %s, %s, NOW());"
        # calculates error type
        error_type = "missing" if item_id is None else "misinformation"
        data = (new_item_id, item_id, error_type, user_id)
        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()

    # removes an error and any duplicate reports once it has been solved
    def remove_report(self, new_item_id):
        cursor = self.connection.cursor()
        query = "DELETE FROM item_error WHERE new_item_id = %s;"
        data = (new_item_id,)
        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()

    # gets each report where the original item id or barcode is the same (as these are unique identifiers)
    # also gets the report by new_item_id incase item is missing and barcode is null
    def get_duplicate_reports(self, new_item_id, identifier, type):
        cursor = self.connection.cursor()
        query = """SELECT error.new_item_id, error.user_id from FoodLink.item_error error 
                    JOIN item i ON (error.new_item_id = i.id) 
                    WHERE new_item_id = %s OR """
        if type == "barcode":
            query += "i.barcode = %s;"
        elif type == "id":
            query += "error.item_id = %s;"
        data = (new_item_id, identifier)
        cursor.execute(query, data)
        reports = cursor.fetchall()
        cursor.close()
        return reports

    def get_reports(self):
        cursor = self.connection.cursor()
        query = """SELECT new_item_id, item_id, error_type, date_created, admin.username, i.name 
                    FROM FoodLink.item_error error 
                    LEFT JOIN FoodLink.admin admin ON (error.admin_id = admin.id)
                    JOIN item i ON (error.new_item_id = i.id);""" 
        cursor.execute(query)
        reports = cursor.fetchall()
        cursor.close()
        return reports
