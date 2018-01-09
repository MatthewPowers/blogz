from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Blogz:pass@localhost:8889/Blogz'
#app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3Blasdkfj'



class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    userposts = db.relationship('Post', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password



class Post(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    blog = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, blog, owner):
        self.title = title
        self.blog = blog
        self.owner = owner



@app.before_request
def require_login():
    allowed_routes = ['login', 'home', 'all_posts', 'new_user', 'index', 'users_posts', 'single_post']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')



@app.route('/')
def index():
    return redirect('/home')



@app.route('/home')
def home():
    users = User.query.all()
    return render_template('home.html', users=users)



@app.route('/single_post')
def single_post():

    #users = User.query.all()
    post_id = request.args.get('post_id')
    post = Post.query.get(post_id)
    return render_template('single_post.html', post=post)#, users=users)



@app.route('/all_posts', methods=['POST', 'GET'])
def all_posts():

    posts = Post.query.all()
    #user = User.query.all()
    return render_template('all_posts.html', posts=posts)#, user=user)



@app.route('/login', methods=['POST', 'GET'])
def login():
   
    if request.method == 'POST':
        error = 0
        username = request.form['username']
        password = request.form['password']
        user_error = ''
        pass_error = ''
        user = User.query.filter_by(username=username).first()

        if not user:
            error = error + 1
            user_error = 'User does not exsist'

        elif user.password != password:
            error = error + 1
            pass_error = 'Invaled Password'

        if error == 0:
            if user and user.password == password:
                session['username'] = username
                flash("Logged in")
                return redirect('/new_post')
        else:
            return render_template('login.html', user_error=user_error, pass_error=pass_error)

    return render_template('login.html')



@app.route('/logout')
def logout():

    del session['username']
    return redirect('/')



@app.route('/new_post', methods=['POST', 'GET'])
def new_post():

    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        name = request.form['blog_name']
        storys = request.form['add_blog']

        error_blog_name = ''
        error_blog_story = ''
        error = 0

        if len(name) == 0:
            error_blog_name = 'invaled title'
            error = error + 1
        else:
            error_blog_name = ''

        if len(storys) == 0:
            error_blog_story = 'invaled blog'
            error = error + 1
        else:
            error_blog_story = ''

        if error > 0:
            return render_template('new_post.html', 
            error_blog_name=error_blog_name, 
            error_blog_story=error_blog_story, blog_name=name, add_blog=storys)

        else:
            new_post = Post(name, storys, owner)
            db.session.add(new_post)
            db.session.commit()
            user_id = request.args.get('user_id')
            print (user_id)
            return redirect('/users_posts?user_id=' + str(new_post.owner.id))

    return render_template('new_post.html')



@app.route('/users_posts')
def users_posts():
       
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    post = Post.query.filter_by(owner_id=user_id)
    return render_template('users_posts.html', user=user, posts=post)  



@app.route('/user_sighnup', methods=['POST', 'GET'])
def new_user():    

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conf_pass = request.form["confurm_pass"]

        old_user = ''
        username_error = ''
        password_error = ''
        conf_pass_error = ''
        error = 0

        if len(username) < 3 or len(username) > 20:
            username_error = 'Not a valid user name'
            error = error + 1

        for char in username:
            if char == ' ':
                username_error = 'Not a valid user name'
                error = error + 1

        if len(password) < 3 or len(password) > 20:
            password_error = 'Not a valid password'
            error = error + 1

        for char in password:
            if char == ' ':
                password_error = 'Not a valid user name'
                error = error + 1

        if password != conf_pass:
            conf_pass_error = 'Does not match password'
            error = error + 1

        if error == 0:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                return redirect('/login')
            else:
                old_user = 'User already Registerd'
                return render_template('user_sighnup.html', old_user=old_user, username=username)
        else:
            return render_template('user_sighnup.html', username=username, 
            username_error=username_error, password_error=password_error, 
            conf_pass_error=conf_pass_error)

    return render_template('user_sighnup.html')


if __name__ == '__main__':
    app.run()