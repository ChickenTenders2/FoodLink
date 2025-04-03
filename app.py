from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,IntegerField, SelectField, EmailField, HiddenField, TextAreaField, PasswordField, BooleanField
from wtforms.validators import Length, NumberRange, InputRequired, Email, DataRequired
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, \
    login_required
from datetime import date

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = "top secret password don't tell anyone this"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://FoodLink:Pianoconclusiontown229!@80.0.43.124/FoodLink'

db = SQLAlchemy(app)
lm = LoginManager(app)
lm.login_view = 'login'

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), index=True, unique=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(32), unique = True)                         
    password = db.Column(db.String(255))

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    @staticmethod
    def register(username, email, password):           
        user = User(username=username, email=email, name='John abc')     
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    def __repr__(self):
        return '<User {0}>'.format(self.username)
    
with app.app_context():
         # creates the empty table

        if User.query.filter_by(username='john').first() is None:
            user = User.register('john', 'john@gmail.com', '123456')
            db.session.add(user)
            db.session.commit()
   

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

@app.route('/',methods=['GET', 'POST'])

def index():
    return render_template('index.html')

@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/createAccount', methods=['GET', 'POST'])
def createAccount():
    form = CreateAccountForm()
    msg = ""
        
    if form.validate_on_submit():

        existing_user = User.query.filter((User.username == form.username.data) | (User.email == form.email.data)).first()
        
        if existing_user is not None:
            if existing_user.username == form.username.data:
                flash("Username already exists.")
            if existing_user.email == form.email.data:
                flash("Email already exists.")
        else:    
            if form.password.data == form.passwordConfirm.data:
                User.register(form.username.data,form.email.data, form.password.data)          
                msg = "New account created. Please sign in."
                return redirect(url_for('login'))
            else:
                msg = "Passwords mismatached." 


    return render_template('createAccount.html', form=form, msg=msg)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = None

    session["username"] = []
    
    if form.validate_on_submit():

        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.verify_password(form.password.data):
            error = "Error: Invalid Credentials"
        else:
            login_user(user, form.remember_me.data)
            #flash("You were successfully logged in!")

            session["username"] = form.username.data
        
            return redirect(url_for('index'))
    
    return render_template('login.html', form=form, error=error)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('username', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    
    app.run(debug=True)
