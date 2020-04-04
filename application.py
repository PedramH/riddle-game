from flask import Flask , render_template, redirect , url_for, request , flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager , login_required, current_user , UserMixin, login_user , logout_user
from werkzeug.security import generate_password_hash, check_password_hash

import config
# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

# init flask app 
app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

#User Acount
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    state = db.Column(db.Integer())


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get("username")
    password= request.form.get("password")
    remember = True
    user = User.query.filter_by(username=username).first()
    if user:
        if password == user.password:
            login_user(user, remember=remember)
            return redirect(url_for('index'))
        else:
            flash("Wrong password!")
            return redirect(url_for('login'))
    else:
        flash("Email address does not exist, mabe try signing up!")
        return redirect(url_for('login'))

            
@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_post():
    # code to validate and add user to database goes here
    username = request.form.get("username")
    name = request.form.get("name")
    password = request.form.get("password")
    user = User.query.filter_by(username=username).first()
    if user:
        flash("This email already exists! Try loging in.")
        return redirect(url_for('signup'))
    # create new user with the form data. Hash the password so plaintext version isn't saved.
    new_user = User(username=username, name=name, password=password, state = 0)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))





if __name__ == '__main__':
    app.run('0.0.0.0',5000,debug=True)