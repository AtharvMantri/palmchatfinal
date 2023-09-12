from flask import Flask, request, render_template, redirect, session, flash
import google.generativeai as palm
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database Initializations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/palmchat'
db = SQLAlchemy(app)  # Initialize SQLAlchemy with the Flask app
app.secret_key = 'palmchatsecret'

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    message = db.Column(db.Text, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.String(10000), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(200), nullable=False)

# Set your PaLM API key here
palm.configure(api_key='AIzaSyAkbv4lemKTxx1pW2_4YzTEHYMB2DWRq4c')

# Default chat parameters
defaults = {
    'model': 'models/chat-bison-001',
    'temperature': 0.25,
    'candidate_count': 1,
    'top_k': 40,
    'top_p': 0.95,
}

@app.route('/', methods=['GET', 'POST'])
def index():
    blogs = Blog.query.filter_by(id=1)
    return render_template('index.html', blogs=blogs)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        
        contact = Contact(name=name, email=email, phone=phone, message=message)
        db.session.add(contact)
        db.session.commit()
        return redirect('/')
    return render_template('contact.html')


@app.route('/blog/<int:blog_id>')
def blog(blog_id):
    blog = Blog.query.get(blog_id)

    return render_template('blog.html', blog=blog)

@app.route('/addblog', methods=['GET', 'POST'])
def addblog():
    if request.method=='POST':
        title = request.form.get('title')
        content = request.form.get('content')
        author = request.form.get('author')
        date = get_current_time()

        blog = Blog(title=title, content=content, author=author, date=date)
        db.session.add(blog)
        db.session.commit()
        flash("Blog Added to site")
        return redirect('/addblog')
    return render_template('addpost.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')

        user = User(name=name, email=email, phone=phone, password=password)
        db.session.add(user)
        db.session.commit()
        session['name'] = name
        session['email'] = email
        session['phone'] = phone
        session['user'] = True
        return redirect('/')
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')

        user = User.query.filter_by(name=name).first()

        if user:
            if user.password == password:
                session['name'] = name
                session['email'] = user.email
                session['phone'] = user.phone
                session['user'] = True
                flash("Login Successful")
                return redirect('/')
            else:
                flash("Incorrect Password")
        else:
            flash("User Doesn't Exist")
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Clear the user session
    session.pop('name', None)
    session.pop('email', None)
    session.pop('phone', None)
    session.pop('user', None)
    
    flash("Logout Successful")
    
    # Redirect to the homepage or any other desired page after logout
    return redirect('/')

@app.route('/palmchat', methods=['GET', 'POST'])
def palmchat():
    response_text = []
    user_input = None

    if request.method == 'POST':
        user_input = request.form.get('user_input')
        context = "You are an ai Language model developed by atharv mantri who is 12 years old and studies at medicaps international school in class 8th B and he build you and your name is palm chat 2 you were developed to make an alternative of ChatGPT"
        examples = []
        messages = [user_input]

        response = palm.chat(
            **defaults,
            context=context,
            examples=examples,
            messages=messages
        )
        ai_response = response.last

        # Replace '\n' with '<br>' in the AI response
        ai_response = ai_response.replace('\n', '<br>')

        response_text.append(('user', user_input, get_current_time()))
        response_text.append(('ai', ai_response, get_current_time()))

    return render_template('chat.html', response_text=response_text, user_input=user_input)


def get_current_time():
    time = datetime.now()
    timedate = f"{amorpm(time)} | {month(time)} {time.day}"
    return timedate


def amorpm(time):
    if time.hour >= 12 and time.second >= 1:
        return str(time.hour - 12) + ":" + str(time.minute) + " PM"
    else:
        return str(time.hour) + ":" + str(time.minute) + " AM"


def month(time):
    if time.month == 1:
        return "Jan"

    elif time.month == 2:
        return "Feb"

    elif time.month == 3:
        return "Mar"

    elif time.month == 4:
        return "Apr"

    elif time.month == 5:
        return "May"

    elif time.month == 6:
        return "Jun"

    elif time.month == 7:
        return "Jul"

    elif time.month == 8:
        return "Aug"

    elif time.month == 9:
        return "Sep"

    elif time.month == 10:
        return "Oct"

    elif time.month == 11:
        return "Nov"

    elif time.month == 12:
        return "Dec"

    else:
        return "Unknown"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
