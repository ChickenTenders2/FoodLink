import random
from flask_mail import Message
from flask import current_app, session

def generate_verification_code():
    return str(random.randint(100000, 999999))


## action text is either "verify" or "reset" and mofifies email text to match accordingly
def send_verification_code(user, mail, action_text):
    code = generate_verification_code()
    if "verification_codes" not in session:
        session["verification_codes"] = {}
    # stores the verification code in a users session instead of globally
    # improves scaling and reduces risk of code mixing between users
    session["verification_codes"][user.email] = code
    # ensures flask saves changes
    session.modified = True 

    msg = Message(
        f'FoodLink - {"Verify Your Email" if action_text == "verify" else "Reset Your Password"}',
        recipients=[user.email],
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )

    
    # Email content
    msg.body = f"""
    Hello {user.username},

    Your email verification code for FoodLink is: {code}

    Enter this code on the verification page to {"verify your email" if action_text == "verify" else "reset your password"}.

    This code will expire in 1 hour.

    {"If you did not create an account" if action_text == "verify" else "If you did not request to reset your password"}, please ignore this email.

    Regards,
    The FoodLink Team
    """
        
    msg.html = f"""
    <p>Hello {user.username},</p>
    <p>Your email verification code for FoodLink is:</p>
    <h2 style="background-color: #f5f5f5; padding: 10px; text-align: center; font-family: monospace;">{code}</h2>
    <p>Enter this code on the verification page to {"verify your email" if action_text == "verify" else "reset your password"}.</p>
    <p>This code will expire in 1 hour.</p>
    <p>{"If you did not create an account" if action_text == "verify" else "If you did not request to reset your password"}, please ignore this email.</p>
    <p>Regards,<br>The FoodLink Team</p>
    """
        
        # Send the email
    mail.send(msg)
    
    # For testing/debugging - print the code to console as well
    print(f"\n----- VERIFICATION CODE for {user.email}: {code} -----\n")
