from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask.views import MethodView
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Device, Settings
from extensions import db

# Create blueprint
settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

# Base class for settings views
class BaseSettingsView(MethodView):
    decorators = [login_required]

# Main settings page
class SettingsView(BaseSettingsView):
    def get(self):
        # login_required ensures a user is authenticated
        user_id = current_user.id
        
        # Get user devices
        devices = Device.query.filter_by(user_id=user_id).all()
        
        # Get or create notification preferences
        notification_prefs = Settings.query.filter_by(user_id=user_id).first()
        if not notification_prefs:
            notification_prefs = Settings(user_id=user_id)
            db.session.add(notification_prefs)
            db.session.commit()
            
        return render_template('settings.html', 
                              user=current_user, 
                              devices=devices,
                              notification_prefs=notification_prefs)
    
# Account Management Views
class AccountUpdateView(BaseSettingsView):
    def post(self):
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
            
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('settings.settings_page'))
    
class AccountDeleteView(BaseSettingsView):
    def post(self):
        password = request.form.get('password')
        
        # Verify password before deletion
        if not check_password_hash(current_user.password, password):
            flash('Incorrect password', 'danger')
            return redirect(url_for('settings.settings_page'))
            
        # Delete all user data
        db.session.delete(current_user)
        db.session.commit()
        
        flash('Your account has been deleted', 'info')
        return redirect(url_for('auth.logout'))
    
# Security Settings Views
class PasswordChangeView(BaseSettingsView):
    def post(self):
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
        db.session.commit()
        
        flash('Password updated successfully', 'success')
        return redirect(url_for('settings.settings_page'))

class TwoFactorToggleView(BaseSettingsView):
    def post(self):
        enable_2fa = request.form.get('enable_2fa') == 'on'
        current_user.two_factor_enabled = enable_2fa
        db.session.commit()
        
        if enable_2fa:
            flash('Two-factor authentication enabled', 'success')
        else:
            flash('Two-factor authentication disabled', 'info')
            
        return redirect(url_for('settings.settings_page'))

class DeviceRemoveView(BaseSettingsView):
    def post(self, device_id):
        device = Device.query.filter_by(id=device_id, user_id=current_user.id).first()
        
        if device:
            db.session.delete(device)
            db.session.commit()
            flash('Device removed successfully', 'success')
        else:
            flash('Device not found', 'danger')
            
        return redirect(url_for('settings.settings_page'))

# Notification Settings View
class NotificationUpdateView(BaseSettingsView):
    def post(self):
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
            db.session.add(notification_prefs)
        
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
            
        db.session.commit()
        flash('Notification preferences updated', 'success')
        return redirect(url_for('settings.settings_page'))

# Appearance Settings View
class ThemeUpdateView(BaseSettingsView):
    def post(self):
        theme = request.form.get('theme', 'light')
        current_user.theme = theme
        db.session.commit()
        
        # Update session for immediate effect
        session['theme'] = theme
        
        flash('Theme updated successfully', 'success')
        return redirect(url_for('settings.settings_page'))

# Register routes: Connect URL paths to their matching functions
settings_bp.add_url_rule('/', view_func=SettingsView.as_view('settings_page'))
settings_bp.add_url_rule('/account/update', view_func=AccountUpdateView.as_view('update_account'))
settings_bp.add_url_rule('/account/delete', view_func=AccountDeleteView.as_view('delete_account'))
settings_bp.add_url_rule('/security/change-password', view_func=PasswordChangeView.as_view('change_password'))
settings_bp.add_url_rule('/security/toggle-2fa', view_func=TwoFactorToggleView.as_view('toggle_2fa'))
settings_bp.add_url_rule('/security/devices/remove/<int:device_id>', view_func=DeviceRemoveView.as_view('remove_device'))
settings_bp.add_url_rule('/notifications/update', view_func=NotificationUpdateView.as_view('update_notifications'))
settings_bp.add_url_rule('/appearance/theme', view_func=ThemeUpdateView.as_view('update_theme'))
settings_bp.add_url_rule('/signout', view_func=lambda: redirect(url_for('auth.logout')), methods=['GET'])