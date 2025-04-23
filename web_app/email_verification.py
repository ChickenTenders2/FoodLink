import random
from flask_mail import Message
from flask import current_app

verification_codes = {}

def generate_verification_code():
    return str(random.randint(100000, 999999))

def send_verification_code(user, mail):
    code = generate_verification_code()
    verification_codes[user.email] = code

    msg = Message(
        'FoodLink - Verify Your Email',
        recipients=[user.email],
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )

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

    mail.send(msg)
    print(f"\n----- VERIFICATION CODE for {user.email}: {code} -----\n")