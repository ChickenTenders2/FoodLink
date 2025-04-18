from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import Length, DataRequired
import random
from flask import current_app
from flask_mail import Message

# Store verification codes (in a real app, you'd use the database)
verification_codes = {}

# Form classes
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 16)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Continue')

class CreateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 16)])
    email = StringField('Email', validators=[DataRequired(), Length(1, 64)])               
    password = PasswordField('Password', validators=[DataRequired()])
    passwordConfirm = PasswordField('Password(ReType)', validators=[DataRequired()])
    submit = SubmitField('Continue')

# Email verification functions
def generate_verification_code():
    """Generate a 6-digit verification code"""
    return str(random.randint(100000, 999999))

def send_verification_code(user, mail):
    """Send verification email with code"""
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