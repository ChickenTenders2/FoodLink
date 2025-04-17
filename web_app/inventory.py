from database import database

class inventory(database):
    def __init__(self):
        super().__init__()

    def get_items(self, user_id):
        cursor = self.connection.cursor()
        # SQL query for retrieving relevant item details
        query = "SELECT inv.id, i.id, i.name, i.brand, quantity, i.unit, expiry_date, i.default_quantity FROM FoodLink.inventory inv JOIN FoodLink.item i ON (inv.item_id = i.id) WHERE inv.user_id = %s;"
        data = (user_id,)
        cursor.execute(query, data)
        items = cursor.fetchall()
        cursor.close()
        return items

    def add_item(self, user_id, item_id, quantity, expiry_date):
        cursor = self.connection.cursor()
        # SQL query for adding the item item to the inventory table
        query = "INSERT INTO inventory (user_id, item_id, quantity, expiry_date) VALUES (%s, %s, %s, %s);"
        data = (user_id, item_id, quantity, expiry_date)
        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()

    def remove_item(self, inventory_id):
        cursor = self.connection.cursor()
        query = "DELETE FROM inventory WHERE id = %s;"
        # one item tuple
        data = (inventory_id,) 
        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()

    def update_quantity(self, inventory_id, quantity):    
        cursor = self.connection.cursor()
        # SQL query for updating the item quantity in the inventory table
        query = "UPDATE inventory SET quantity = %s WHERE id = %s;"
        data = [quantity, inventory_id]
        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()

    def update_item(self, inventory_id, quantity, expiry_date):
        cursor = self.connection.cursor()
        # SQL query for updating the item in the inventory table
        query = "UPDATE inventory SET quantity = %s, expiry_date = %s WHERE id = %s;"
        data = [quantity, expiry_date, inventory_id]
        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()

    def search_items(self, user_id, search_term):
        cursor = self.connection.cursor()
        # search query uses full text for relevance based searching of items
        query = "SELECT inv.id, i.id, i.name, i.brand, quantity, i.unit, expiry_date, i.default_quantity FROM FoodLink.inventory inv JOIN FoodLink.item i ON inv.item_id = i.id WHERE (inv.user_id = %s AND MATCH(i.name) AGAINST (%s IN NATURAL LANGUAGE MODE));"
        data = (user_id, search_term)
        cursor.execute(query, data)
        items = cursor.fetchall()
        cursor.close()
        return items
    
    def process_add_form(self, user_id, item_id, form):
        try:
            quantity = form["quantity"]
            expiry = form["expiry_date"]
            self.add_item(user_id, item_id, quantity, expiry)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
        
    # Replaces the users peronsal item with the item they reported once its been corrected/added to the table
    # also makes sure the quantity set by the user do not exceed the corrected item max quantity
    def correct_personal_item(self, personal_item_id, item_id, default_quantity):
        # item_id = the item id of the now added item if missing, or the item id of the item that has now been corrected
        # personal_item_id = the users personal item id that they added before reporting

        # if default quantity is 1 then there is not a limit on the quantity
        if default_quantity == 1:
            query = """UPDATE FoodLink.inventory SET 
	                item_id = %s
                WHERE item_id = %s;"""
            data = (item_id, personal_item_id)
        # otherwise the users item should not exceed the default quantity (max amount) of the item
        else:
            # sets quantity to max if it exceeds limit
            query = """UPDATE FoodLink.inventory SET 
	                item_id = %s
                    quantity = CASE
                        WHEN quantity > %s THEN %s
                        ELSE quantity
                    END
                WHERE item_id = %s;"""
            data = (item_id, default_quantity, default_quantity, personal_item_id)

        cursor = self.connection.cursor()
        cursor.execute(query, data)
        self.connection.commit()

