from flask import Flask, url_for, render_template, session

app = Flask(__name__)

@app.route('/')
def index():
    if 'username' in session:
        return render_template('home.html')
    else:
        return render_template('signin.html')

@app.route('/signup/')
def signup():
    return render_template('signup.html')