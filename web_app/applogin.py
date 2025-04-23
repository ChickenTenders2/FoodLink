from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length

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

class CombinedResetForm(FlaskForm):
    email = StringField('Email', validators=[Length(1, 64)])
    otp = StringField('Security code')  
    submit_email = SubmitField('Send Code')
    submit_otp = SubmitField('Verify Code')

class ResetPasswordForm(FlaskForm):
    password = PasswordField(' New password', validators=[DataRequired()])
    passwordConfirm = PasswordField('New Password(ReType)', validators=[DataRequired(),Length(min=6,message="Password must be at least 6 characters long.")],)
    submit = SubmitField('Continue')    

class AdminCreateForm(FlaskForm):
        username = StringField('Username', validators=[DataRequired(), Length(1, 16)])
        name = StringField("Name", validators=[DataRequired(), Length(1, 16)])
        email = StringField('Email', validators=[DataRequired(), Email()])
        password = PasswordField('Password', validators=[DataRequired()])
        submit = SubmitField('Add Admin')

class AdminPasswordForm(FlaskForm):
        current_password = PasswordField('Current Password', validators=[DataRequired()])
        new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
        confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
        submit = SubmitField("Update Password")
