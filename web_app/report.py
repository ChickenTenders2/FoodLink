from database import get_cursor, commit, safe_rollback
import logging

# user function
def add_report(new_item_id, item_id, user_id):
    """Adds an item error report to the database."""
    cursor = None
    try:
        cursor = get_cursor()
        # adds date created as current time
        query = "INSERT INTO item_error (new_item_id, item_id, error_type, user_id, date_created) VALUES (%s, %s, %s, %s, NOW());"
        # calculates error type
        error_type = "missing" if item_id is None else "misinformation"
        data = (new_item_id, item_id, error_type, user_id)
        cursor.execute(query, data)
        commit()
        return {"success": True}
    except Exception as e:
        safe_rollback()
        logging.error(f"[add_report error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def remove_report(new_item_id):
    """Removes an item error report once its been resolved."""
    cursor = None
    try:
        cursor = get_cursor()
        query = "DELETE FROM item_error WHERE new_item_id = %s;"
        data = (new_item_id,)
        cursor.execute(query, data)
        commit()
        return {"success": True}
    except Exception as e:
        safe_rollback()
        logging.error(f"[remove_report error] {e}")
        # more detailed report for admin only function
        return {"success": False, "error": f"[remove_report error] {e}"}
    finally:
        if cursor:
            cursor.close()

# gets each report where the original item id or barcode is the same (as these are unique identifiers)
# also gets the report by new_item_id incase item was missing and barcode is null
def get_reports_by(new_item_id, identifier=None, type=None):
    """Gets the original report (identified by new_item_id) and all the other reports that report the same item.
    When type is "barcode" it searches by the identifier (barcode) on the barcode field, used for missing item reports.
    When type is "id" it searches by the indentifier (original item id) on the item_id field, used for misinformation reports."""
    cursor = None
    try:
        cursor = get_cursor()
        data = (new_item_id, identifier)
        query = """SELECT error.new_item_id, i.name, error.user_id from FoodLink.item_error error 
                    JOIN item i ON (error.new_item_id = i.id) 
                    WHERE new_item_id = %s"""
        if type == "barcode":
            query += " OR i.barcode = %s;"
        elif type == "id":
            query += " OR error.item_id = %s;"
        else:
            query += ";"
            data = (new_item_id,)
        cursor.execute(query, data)
        reports = cursor.fetchall()
        return {"success": True, "reports": reports}
    except Exception as e:
        logging.error(f"[get_reports_by error] {e}")
        # more detailed report for admin only function
        return {"success": False, "error": f"[get_reports_by error] {e}"}
    finally:
        if cursor:
            cursor.close()

def get_reports():
    """Gets every item error report information."""
    cursor = None
    try:
        cursor = get_cursor()
        # uses a left join so unassigned reports still show
        query = """SELECT new_item_id, item_id, error_type, date_created, admin.username, i.name 
                    FROM FoodLink.item_error error 
                    LEFT JOIN FoodLink.admin admin ON (error.admin_id = admin.id)
                    JOIN item i ON (error.new_item_id = i.id);""" 
        cursor.execute(query)
        reports = cursor.fetchall()
        return {"success": True, "reports": reports}
    except Exception as e:
        logging.error(f"[get_reports error] {e}")
        # more detailed report for admin only function
        return {"success": False, "error": f"[get_reports error] {e}"}
    finally:
        if cursor:
            cursor.close()

def check_assigned(new_item_id):
    """Checks if a report is already assigned to an admin."""
    cursor = None
    try:
        cursor = get_cursor()
        query = """SELECT admin_id FROM item_error WHERE new_item_id = %s;""" 
        data = (new_item_id,)
        cursor.execute(query, data)
        admin_id = cursor.fetchone()
        return {"success": True, "admin_id": admin_id[0]}
    except Exception as e:
        logging.error(f"[check_assigned error] {e}")
        # more detailed report for admin only function
        return {"success": False, "error": f"[check_assigned error] {e}"}
    finally:
        if cursor:
            cursor.close()

def assign(new_item_id, admin_id):
    """Assigns a report (using primary key new_item_id) to and admin with id"""
    cursor = None
    try:
        cursor = get_cursor()
        query = """UPDATE item_error SET admin_id = %s WHERE new_item_id = %s;""" 
        data = (admin_id, new_item_id)
        cursor.execute(query, data)
        commit()
        return {"success": True}
    except Exception as e:
        safe_rollback()
        logging.error(f"[report.assign error] {e}")
        # more detailed report for admin only function
        return {"success": False, "error": f"[report.assign error] {e}"}
    finally:
        if cursor:
            cursor.close()