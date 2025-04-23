from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, login_required, current_user, login_user, logout_user, UserMixin
from flask_mail import Mail, Message
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import Length, InputRequired, Email, DataRequired
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash


# Import database and user model
from models import db, User, Admin

# Initialize Flask application
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'top secret password dont tell anyone this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://FoodLink:Pianoconclusiontown229!@81.109.118.20/FoodLink'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'foodlink2305@gmail.com'  
app.config['MAIL_PASSWORD'] = 'fmgz nrxz mwul nqju'    
app.config['MAIL_DEFAULT_SENDER'] = 'FoodLink <foodlink2305@gmail.com>'

# Initialize extensions
bootstrap = Bootstrap(app)
db.init_app(app)
mail = Mail(app)

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Define forms from applogin.py
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

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    #return User.query.get(int(user_id)) was working but adding user_type makes life easier in the future
    user_type = session.get("user_type")
    if user_type == "admin":
        return Admin.query.get(int(user_id))
    else:
        return User.query.get(int(user_id))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    error = None
    
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin and check_password_hash(admin.password, form.password.data):
            login_user(admin, remember=False)
            session["username"] = admin.username
            session["user_type"] = "admin"
            flash("Logged in successfully as admin.", "success")
            return redirect(url_for("AdminDashboard"))
        else:
            error = "Invalid admin credentials."

    return render_template('admin_login.html', form=form, error=error)



@app.route("/admin/add", methods=["GET", "POST"])
@login_required
def AddAdmin():
    # Must be advanced admin
    if not isinstance(current_user._get_current_object(), Admin) or not current_user.advanced_privileges:
        flash("You are not authorized to add new admins.", "danger")
        return redirect(url_for("AdminDashboard"))

    class AdminCreateForm(FlaskForm):
        username = StringField('Username', validators=[DataRequired(), Length(1, 16)])
        name = StringField("Name", validators=[DataRequired(), Length(1, 16)])
        email = StringField('Email', validators=[DataRequired(), Email()])
        password = PasswordField('Password', validators=[DataRequired()])
        submit = SubmitField('Add Admin')

    form = AdminCreateForm()
    message = None

    if form.validate_on_submit():
        existing_admin = Admin.query.filter(
            (Admin.username == form.username.data) | 
            (Admin.email == form.email.data)
        ).first()

        if existing_admin:
            message = "Admin already exists."
        else:
            new_admin = Admin(
                name=form.name.data,
                username=form.username.data,
                email=form.email.data,
                password=generate_password_hash(form.password.data),
                advanced_privileges=False
            )
            db.session.add(new_admin)
            db.session.commit()
            flash("New admin added successfully!", "success")
            return redirect(url_for('AdminDashboard'))

    return render_template("admin_add.html", form=form, message=message)

@app.route("/admin/update-password", methods=["GET", "POST"])
@login_required
def AdminUpdatePassword():
    if not isinstance(current_user._get_current_object(), Admin):
        flash("Unauthorized access.", "danger")
        return redirect(url_for("admin_login"))

    class AdminPasswordForm(FlaskForm):
        current_password = PasswordField('Current Password', validators=[DataRequired()])
        new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
        confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
        submit = SubmitField("Update Password")

    form = AdminPasswordForm()
    message = None

    if form.validate_on_submit():
        if not check_password_hash(current_user.password, form.current_password.data):
            message = "Current password is incorrect."
        elif form.new_password.data != form.confirm_password.data:
            message = "New passwords do not match."
        else:
            current_user.password = generate_password_hash(form.new_password.data)
            db.session.commit()
            flash("Password updated successfully!", "success")
            return redirect(url_for("AdminDashboard"))

    return render_template("admin_update_password.html", form=form, message=message)

@app.route("/admin/dashboard")
@login_required
def AdminDashboard():
    return render_template("admin_dashboard.html")
# 
# Logout route
@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    session.clear()
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True)