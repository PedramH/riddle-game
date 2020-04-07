import datetime
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
login_manager.login_message = u"لطفا وارد شوید"
login_manager.init_app(app)


class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    state = db.Column(db.Integer())

def log_input(inputstr):
    f = open("log.txt", "a")
    currentDT = datetime.datetime.now()
    f.write(f"{str(currentDT)};{current_user.name};{current_user.state};{inputstr} \n")
    f.close()

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))

def normalize_string(inputstr=""):
    inputstr = inputstr.replace("ك","ک")
    inputstr = inputstr.replace("ي","ی")
    return inputstr

@app.route('/')
@login_required
def index():
    return render_template('index.html',pagetitle="Main Page")

@app.route('/login')
def login():
    return render_template('login.html',pagetitle="Login!")

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get("username").lower()
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
    username = request.form.get("username").lower()
    print(username)
    name = request.form.get("name")
    password = request.form.get("password")
    user = User.query.filter_by(username=username).first()
    if user:
        flash("This email already exists! Try loging in.")
        return redirect(url_for('signup',pagetitle="Login!"))
    new_user = User(username=username, name=name, password=password, state = 0)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/resetprogress')
@login_required
def reset_progress():
    current_user.state = 1
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/resume')
@login_required
def resume_game():
    """ Redirect the user to the current state """
    level = current_user.state
    page = f"level{level}"
    return redirect(url_for(page))

@app.route('/leaderboard')
@login_required
def leader_board():
    """ Show the users current level """
    users_data = []
    users = User.query.all()
    for user in users:
        users_data.append((user.name,user.state))

    return render_template('leaderboard.html',data=users_data)

@app.route('/log')
@login_required
def user_input_log():
    """ Show the users inputs """
    f = open('log.txt', 'r') 
    Lines = f.readlines() 
    data = []
    for line in Lines:
        data.append(line.strip().split(";"))
        print (line)
    
    return render_template('showlog.html',data=data)


# ---------------------------------------------------------Riddle Pages------------------------------------------------
# ----------------------------------------------------------- Level1 --------------------------------------------------
@app.route('/level1')
@login_required
def level1():
    imageurl='/static/assets/img/1.jpg'
    formaction='/level2'
    pagetitle = 'Level1: '
    #clue = '<p class="iransanse rtl transparentcolor"> سلام سلام  </p>'
    clue = current_user.state
    return render_template('levels.html',imageurl=imageurl,formaction=formaction,pagetitle=pagetitle, clue = clue)

@app.route('/level1', methods = ['POST'])
@login_required
def level1_post():
    return redirect(url_for('level1'))

# ----------------------------------------------- Level2 -------------------------------------------------------------
@app.route('/level2')
@login_required
def level2():
    #check if user is authorized to access this level
    this_level_number = 2
    if current_user.state  < this_level_number :
        return render_template('wronglevel.html',title="ای شیطون")
    imageurl='/static/assets/img/2.jpg'
    pagetitle = 'Level2: '
    clue = '<p class="iransanse rtl trcolor"> سلام سلام  </p>'
    formaction='/level3'
    return render_template('levels.html',imageurl=imageurl,formaction=formaction,pagetitle=pagetitle, clue = clue)

@app.route('/level2', methods = ['POST'])
@login_required
def level2_post():
    this_level_number = 2
    prev_level_answer = 'level1pass'
    prev_level = 'level1'
    this_level = 'level2'
    answer = normalize_string(request.form.get("answer"))
    log_input(answer)
    if answer == prev_level_answer:
        if current_user.state < this_level_number:
            current_user.state = this_level_number
            db.session.commit()
        #return redirect(url_for(this_level))
        return render_template("msg.html", title='Correct!',msg="خیلی خوش گذشت",link=url_for(this_level))
    else:
        flash('نه! جواب اشتباه بود. دوباره سعی کن!')
        return redirect(url_for(prev_level))

# ----------------------------------------------- Level3 -------------------------------------------------------------
@app.route('/level3')
@login_required
def level3():
    #check if user is authorized to access this level
    this_level_number = 3
    if current_user.state  < this_level_number :
        return render_template('wronglevel.html',title="ای شیطون")
    imageurl='/static/assets/img/3.jpg'
    pagetitle = 'Level3: '
    clue = '<p class="iransanse rtl transparentcolor"> سلام سلام  </p>'
    formaction='/level4'  #this should indicate the next level
    return render_template('levels.html',imageurl=imageurl,formaction=formaction,pagetitle=pagetitle, clue = clue)

@app.route('/level3', methods = ['POST'])
@login_required
def level3_post():
    this_level_number = 3
    prev_level_answer = 'level2pass'
    prev_level = 'level2'
    this_level = 'level3'
    answer = normalize_string(request.form.get("answer"))
    log_input(answer)
    if answer == prev_level_answer:
        if current_user.state < this_level_number:
            current_user.state = this_level_number
            db.session.commit()
        return redirect(url_for(this_level))
    else:
        flash('نه! جواب اشتباه بود. دوباره سعی کن!')
        return redirect(url_for(prev_level))

# ----------------------------------------------- Level 4 -------------------------------------------------------------
@app.route('/level4')
@login_required
def level4():
    #check if user is authorized to access this level
    this_level_number = 4
    if current_user.state  < this_level_number :
        return render_template('wronglevel.html',title="ای شیطون")
    imageurl='/static/assets/img/4.jpg'
    pagetitle = 'Level4: '
    clue = '<p class="iransanse rtl transparentcolor"> سلام سلام  </p>'
    formaction='/level5'  #this should indicate the next level
    return render_template('levels.html',imageurl=imageurl,formaction=formaction,pagetitle=pagetitle, clue = clue)

@app.route('/level4', methods = ['POST'])
@login_required
def level4_post():
    this_level_number = 4
    prev_level_answer = 'level3pass'
    prev_level = 'level3'
    this_level = 'level4'
    answer = normalize_string(request.form.get("answer"))
    log_input(answer)
    if answer == prev_level_answer:
        if current_user.state < this_level_number:
            current_user.state = this_level_number
            db.session.commit()
        return redirect(url_for(this_level))
    else:
        flash('نه! جواب اشتباه بود. دوباره سعی کن!')
        return redirect(url_for(prev_level))

# ----------------------------------------------- Level 5 -------------------------------------------------------------
@app.route('/level5')
@login_required
def level5():
    #check if user is authorized to access this level
    this_level_number = 5
    if current_user.state  < this_level_number :
        return render_template('wronglevel.html',title="ای شیطون")
    imageurl='/static/assets/img/4.jpg'
    pagetitle = 'Level5: '
    clue = '<p class="iransanse rtl transparentcolor"> سلام سلام  </p>'
    formaction='/level6'  #this should indicate the next level
    return render_template('levels.html',imageurl=imageurl,formaction=formaction,pagetitle=pagetitle, clue = clue)

@app.route('/level5', methods = ['POST'])
@login_required
def level5_post():
    this_level_number = 5
    prev_level_answer = 'level4pass'
    prev_level = 'level4'
    this_level = 'level5'
    answer = normalize_string(request.form.get("answer"))
    log_input(answer)
    if answer == prev_level_answer:
        if current_user.state < this_level_number:
            current_user.state = this_level_number
            db.session.commit()
        return redirect(url_for(this_level))
    else:
        flash('نه! جواب اشتباه بود. دوباره سعی کن!')
        return redirect(url_for(prev_level))

if __name__ == '__main__':
    app.run('0.0.0.0',5000,debug=True)