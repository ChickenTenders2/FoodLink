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
    def remove_reports(self, identifier, type):
        cursor = self.connection.cursor()
        query = "DELETE error FROM item_error error JOIN item i ON (error.new_item_id = i.id) WHERE "
        if type == "name":
            query += "i.name = %s;"
        elif type == "barcode":
            query += "i.barcode = %s;"
        elif type == "id":
            query += "error.item_id = %s;"
        data = (identifier,)
        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()

    # gets each user_id from reports where the item is the same
    def get_reports_user_id(self, identifier, type):
        cursor = self.connection.cursor()
        query = "SELECT error.user_id from FoodLink.item_error error JOIN item i ON (error.new_item_id = i.id) WHERE "
        if type == "name":
            query += "i.name = %s;"
        elif type == "barcode":
            query += "i.barcode = %s;"
        elif type == "id":
            query += "error.item_id = %s;"
        data = (identifier,)
        cursor.execute(query, data)
        items = cursor.fetchall()
        cursor.close()
        return items

    def get_reports(self):
        cursor = self.connection.cursor()
        query = """SELECT new_item_id, item_id, error_type, date_created, admin.username 
                    FROM FoodLink.item_error error 
                    LEFT JOIN FoodLink.admin admin ON (error.admin_id = admin.id);"""
        cursor.execute(query)
        reports = cursor.fetchall()
        cursor.close()
        return reports

    def get_report(self, new_item_id):
        cursor = self.connection.cursor()
        query = """SELECT i.id, i.barcode, i.name, i.brand, i.expiry_time, i.default_quantity, i.unit, 
                    i2.id, i2.barcode, i2.name, i2.brand, i2.expiry_time, i2.default_quantity, i2.unit 
                    from FoodLink.item_error error 
                    JOIN item i ON (error.new_item_id = i.id) 
                    LEFT JOIN item i2 on (error.item_id = i2.id)
                    WHERE new_item_id = %s;"""
        data = (new_item_id,)
        cursor.execute(query, data)
        report = cursor.fetchall()
        cursor.close()
        return report
