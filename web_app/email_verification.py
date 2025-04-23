from flask import Blueprint, render_template, redirect, url_for, flash, current_app, request
from flask_login import current_user, login_required
from flask_mail import Message
import random

# Create blueprint
email_verification_bp = Blueprint('email_verification', __name__)

# These will be initialized when init_email_verification is called
mail = None
db = None

# Store verification codes (in a real app, you'd use the database)
verification_codes = {}

# Generate a 6-digit verification code
def generate_verification_code():
    return str(random.randint(100000, 999999))

# Send verification email with code
def send_verification_code(user):
    # Generate a new code
    code = generate_verification_code()
    # Store the code
    verification_codes[user.email] = code
    
    # Create the email message
    msg = Message(
        'FoodLink - Verify Your Email',
        recipients=[user.email],
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    
    # Email content
    msg.body = f"""
Hello {user.username},

Your email verification code for FoodLink is: {code}

Enter this code on the verification page to verify your email address.

This code will expire in 1 hour.

If you did not create an account, please ignore this email.

Regards,
The FoodLink Team
"""
    
    msg.html = f"""
<p>Hello {user.username},</p>
<p>Your email verification code for FoodLink is:</p>
<h2 style="background-color: #f5f5f5; padding: 10px; text-align: center; font-family: monospace;">{code}</h2>
<p>Enter this code on the verification page to verify your email address.</p>
<p>This code will expire in 1 hour.</p>
<p>If you did not create an account, please ignore this email.</p>
<p>Regards,<br>The FoodLink Team</p>
"""
    
    # Send the email
    mail.send(msg)
    
    # For testing/debugging - print the code to console as well
    print(f"\n----- VERIFICATION CODE for {user.email}: {code} -----\n")

# Route to request verification code
@email_verification_bp.route('/send-code', methods=['POST'])
@login_required
def send_verification_code_route():
    # Check if email is already verified
    if current_user.email_verified:
        flash('Your email is already verified.', 'info')
        return redirect(url_for('email_verification.verification_page'))
    
    # Send verification code
    send_verification_code(current_user)
    flash('A verification code has been sent to your email address.', 'success')
    return redirect(url_for('email_verification.verification_page'))

# Route to verify email with code
@email_verification_bp.route('/verify-code', methods=['POST'])
@login_required
def verify_code():
    # Get submitted code
    entered_code = request.form.get('verification_code')
    
    if not entered_code:
        flash('Please enter a verification code.', 'danger')
        return redirect(url_for('email_verification.verification_page'))
    
    # Check if code matches
    stored_code = verification_codes.get(current_user.email)
    
    if not stored_code:
        flash('No verification code found. Please request a new code.', 'danger')
        return redirect(url_for('email_verification.verification_page'))
    
    if stored_code == entered_code:
        # Code matches, update verification status
        current_user.email_verified = True
        db.session.commit()
        
        # Clear the code
        verification_codes.pop(current_user.email, None)
        
        flash('Your email has been verified successfully!', 'success')
    else:
        flash('Invalid verification code. Please try again.', 'danger')
    
    return redirect(url_for('email_verification.verification_page'))

# Route for email verification page
@email_verification_bp.route('/verification')
@login_required
def verification_page():
    return render_template('email_verification.html')

# Function to initialize the email verification extension
def init_email_verification(app, database, mail_service):
    global db, mail
    db = database
    mail = mail_service