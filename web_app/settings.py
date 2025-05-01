from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask.views import MethodView
from flask_login import login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import Settings, User
from alchemy_db import db, safe_execute
from database import get_cursor, commit, safe_rollback
import logging

# Create blueprint
settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

# Base class for settings views
class BaseSettingsView(MethodView):
    decorators = [login_required]

# Main settings page
class SettingsView(BaseSettingsView):
    def get(self):
        """
        This function loads the main settings page for the authenticated user.
        Furthermore creates default notifcation preferences if none exists.
        """
        # login_required ensures a user is authenticated
        user_id = current_user.id
        
        # Get or create notification preferences
        notification_prefs = Settings.query.filter_by(user_id=user_id).first()
        if not notification_prefs:
            notification_prefs = Settings(user_id=user_id)
            safe_execute(db.session.add, notification_prefs)
            safe_execute(db.session.commit)
            
        return render_template('settings.html', 
                              user=current_user, 
                              notification_prefs=notification_prefs)
    
# Account Management Views
class AccountUpdateView(BaseSettingsView):
    def post(self):
        """
        This function updates the user's profile information (e.g. username and name).
        Furthermore checks for username uniqueness before updating.
        """
        username = request.form.get('username')
        name = request.form.get('name')
        
        # Update username if provided and different
        if username and username != current_user.username:
            # Check if username is already taken
            existing_user = User.query.filter_by(username=username).first()
            if existing_user and existing_user.id != current_user.id:
                flash('Username already exists', 'danger')
                return redirect(url_for('settings.settings_page'))
            
            current_user.username = username
            
        # Update name if provided
        if name:
            current_user.name = name
            
        safe_execute(db.session.commit)
        flash('Profile updated successfully', 'success')
        return redirect(url_for('settings.settings_page'))

# Delete all data associated with a user from all related tables 
def delete_user_data(user_id):
    """
    This function deletes all data associated with a user from all related tables.
    At the end, the function will return True if successfully deleted, False otherwise.
    """
    cursor = None
    try:
        cursor = get_cursor()
        
        # Find all recipes created by user for later deletion
        cursor.execute("SELECT id FROM recipe WHERE user_id = %s", (user_id,))
        user_recipes = cursor.fetchall()
        recipe_ids = [recipe[0] for recipe in user_recipes]
        
        # Delete from inventory
        cursor.execute("DELETE FROM inventory WHERE user_id = %s", (user_id,))
        
        # Delete personal items (items created by this user)
        cursor.execute("DELETE FROM item WHERE user_id = %s", (user_id,))
        
        # Delete item error reports
        cursor.execute("DELETE FROM item_error WHERE user_id = %s", (user_id,))
        
        # Delete notifications
        cursor.execute("DELETE FROM notification WHERE user_id = %s", (user_id,))
        
        # Delete settings
        cursor.execute("DELETE FROM settings WHERE user_id = %s", (user_id,))
        
        # Delete shopping list
        cursor.execute("DELETE FROM shopping_list WHERE user_id = %s", (user_id,))
        
        # Delete user tools
        cursor.execute("DELETE FROM user_tool WHERE user_id = %s", (user_id,))
        
        # Delete each recipe and its associated items and tools
        for recipe_id in recipe_ids:
            # Delete recipe tools
            cursor.execute("DELETE FROM recipe_tool WHERE recipe_id = %s", (recipe_id,))
            # Delete recipe items
            cursor.execute("DELETE FROM recipe_items WHERE recipe_id = %s", (recipe_id,))
            # Delete recipe itself
            cursor.execute("DELETE FROM recipe WHERE id = %s", (recipe_id,))
        
        commit()
        return True
    except Exception as e:
        safe_rollback()
        logging.error(f"[delete_user_data error] {e}")
        return False
    finally:
        if cursor:
            cursor.close()
    
class AccountDeleteView(BaseSettingsView):
    def post(self):
        """
        This function permanently deletes the user account and all associated data
        after verifying the password. Then logs the user out after deletion.
        """
        password = request.form.get('password')
        user_id = current_user.id
        
        # Verify password before deletion
        if not check_password_hash(current_user.password, password):
            flash('Incorrect password', 'danger')
            return redirect(url_for('settings.settings_page'))
            
        # Delete all user data
        if delete_user_data(user_id):
            safe_execute(db.session.delete, current_user)
            safe_execute(db.session.commit)

            # Log the user out
            logout_user()
        
            flash('Your account has been deleted', 'info')
            return redirect(url_for('auth.logout'))
        else:
            flash('An error occured while deleting your account. PLease try again', 'danger')
            return redirect(url_for('settings.settings_page'))
    
# Security Settings Views
class PasswordChangeView(BaseSettingsView):
    def post(self):
        """
        This function changes the user's password after verifying the current password,
        and confirming the new password matches the confirmation. 
        """
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Verify current password
        if not check_password_hash(current_user.password, current_password):
            flash('Current password is incorrect', 'danger')
            return redirect(url_for('settings.settings_page'))
            
        # Validate new password
        if new_password != confirm_password:
            flash('New passwords do not match', 'danger')
            return redirect(url_for('settings.settings_page'))
            
        # Update password
        current_user.password = generate_password_hash(new_password)
        safe_execute(db.session.commit)
        
        flash('Password updated successfully', 'success')
        return redirect(url_for('settings.settings_page'))

# Notification Settings View
class NotificationUpdateView(BaseSettingsView):
    def post(self):
        """
        This function updates notification and alert preferences, this includes
        email notifications, fridge monitoring alerts, and temperature/humidity thresholds.
        """
        # Get form data
        email_notifications = request.form.get('email_notifications') == 'on'
        fridge_open = request.form.get('fridge_open') == 'on'
        expiring_food = request.form.get('expiring_food') == 'on'
        recipe_suggestions = request.form.get('recipe_suggestions') == 'on'
        temperature_alerts = request.form.get('temperature_alerts') == 'on'
        
        # Get temperature range preferences
        min_temperature = request.form.get('min_temperature', type=float)
        max_temperature = request.form.get('max_temperature', type=float)
        max_humidity = request.form.get('max_humidity', type=float)
        
        # Get or create notification preferences
        notification_prefs = Settings.query.filter_by(user_id=current_user.id).first()
        if not notification_prefs:
            notification_prefs = Settings(user_id=current_user.id)
            safe_execute(db.session.add, notification_prefs)
        
        # Update preferences
        notification_prefs.email_notifications = email_notifications
        notification_prefs.fridge_open = fridge_open
        notification_prefs.expiring_food = expiring_food
        notification_prefs.recipe_suggestions = recipe_suggestions
        notification_prefs.temperature_alerts = temperature_alerts
        
        # Update temperature range if provided
        if min_temperature is not None:
            notification_prefs.min_temperature = min_temperature
        if max_temperature is not None:
            notification_prefs.max_temperature = max_temperature
        if max_humidity is not None:
            notification_prefs.max_humidity = max_humidity
            
        safe_execute(db.session.commit)
        flash('Notification preferences updated', 'success')
        return redirect(url_for('settings.settings_page'))


# Register routes: Connect URL paths to their matching functions
settings_bp.add_url_rule('/', view_func=SettingsView.as_view('settings_page'))
settings_bp.add_url_rule('/account/update', view_func=AccountUpdateView.as_view('update_account'))
settings_bp.add_url_rule('/account/delete', view_func=AccountDeleteView.as_view('delete_account'))
settings_bp.add_url_rule('/security/change-password', view_func=PasswordChangeView.as_view('change_password'))
settings_bp.add_url_rule('/notifications/update', view_func=NotificationUpdateView.as_view('update_notifications'))
settings_bp.add_url_rule('/signout', view_func=lambda: redirect(url_for('logout')), methods=['GET'])