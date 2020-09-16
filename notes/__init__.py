from flask import Flask, url_for, flash, render_template, session, request, redirect
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'seckey'
app.config["MONGO_URI"] = "mongodb://localhost:27017/Notes"
mongo = PyMongo(app)



@app.route('/')
def index():
    if 'username' in session:
        user= mongo.db.users.find_one({'username': session['username']})
        notebooks = mongo.db.notebooks.find({"user_id": user['_id']})
        names = []
        for n in notebooks:
            names.append(n)
        return render_template('home.html', user = user, names=names)
    else:
        return render_template('signin.html')



@app.route('/signup/', methods = ['GET', 'POST'])
def signup():
    if request.method =='GET':
        return render_template('signup.html')
    else:
        userlist = mongo.db.users
        check_email = userlist.find_one({'email': request.form['email']})
        check_username = mongo.db.users.find_one({'username': request.form['username']})

        if check_email :
            flash('Email address already registered!')
            return redirect(url_for('signup'))
        elif check_username:
            flash('Username already exists!')
            return redirect(url_for('signup'))
        else:
            new_user = {
                'username': request.form['username'],
                'email': request.form['email'],
                'password': generate_password_hash(request.form['password'])
            }
            mongo.db.users.insert(new_user)
            first_notebook = {
                'name': 'Notebook 1',
                'description': 'This is a new notebook',
                'user_id': new_user['_id']
            }
            mongo.db.notebooks.insert(first_notebook)
            first_note = {
                'title': 'New Note',
                'note': 'Take a note!',
                'notebook_id': first_notebook['_id']
            }
            mongo.db.notes.insert(first_note)
        return redirect(url_for('index'))


@app.route('/signin/', methods=['GET','POST'])
def signin():
    if request.method == "GET":
        return render_template('signin.html')
    else:
        userlist = mongo.db.users
        loginuser = userlist.find_one({'email': request.form['email']})
        if loginuser:
            if check_password_hash(loginuser['password'], request.form['password']):
                session['username'] = loginuser['username']
            else:
                flash("Invalid Email or Password")
            return redirect(url_for('index'))
        else:
            flash("Invalid Email or Password")
            return render_template('signin.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')



@app.route('/new_notebook', methods = ['GET', 'POST'])
def new_notebook():
    user= mongo.db.users.find_one({'username': session['username']})
    length = mongo.db.notebooks.count_documents({'user_id': user['_id']})
    new_notebook = {
                'name': 'Notebook {}'.format(length+1),
                'description': 'This is a new notebook',
                'user_id': user['_id']
            }
    mongo.db.notebooks.insert(new_notebook)
    new_note = {
                'title': 'New Note',
                'note': 'Take a note!',
                'notebook_id': new_notebook['_id']
            }
    mongo.db.notes.insert(new_note)
    return redirect(url_for('notebook', notebook_id = new_notebook['_id']))



@app.route('/notebook/<notebook_id>', methods=['GET', 'POST'])
def notebook(notebook_id):
    notebook = mongo.db.notebooks.find_one({'_id':ObjectId(notebook_id)})
    notes = mongo.db.notes.find({'notebook_id': ObjectId(notebook_id)})
    all_notes = []
    for note in notes:
        all_notes.append(note)
    edit = False
    delete = False
    if request.method == 'POST':
        if request.form.get('edit'):
            edit = True
        elif request.form.get('delete'):
            delete= True
            flash('Are you sure you want to delete this notebook? Once deleted it cannot be recovered!')

        return render_template('notebook.html', notebook= notebook,edit=edit, delete=delete, all_notes=all_notes)
    else:
        return render_template('notebook.html', notebook= notebook,edit=edit, delete=delete, all_notes=all_notes)



@app.route('/save_changes/<notebook_id>', methods=['POST'])
def save_changes(notebook_id):
    notebook = mongo.db.notebooks.find_one({'_id': ObjectId(notebook_id)})
    notebook['name'] = request.form['name']
    notebook['description'] = request.form['description']
    mongo.db.notebooks.save(notebook)
    return redirect(url_for('notebook', notebook_id=notebook['_id']))



@app.route('/delete/<notebook_id>', methods = ['GET','POST'])
def delete_notebook(notebook_id):
    mongo.db.notebooks.delete_one({'_id': ObjectId(notebook_id)})
    mongo.db.notes.delete_many({'notebook_id': ObjectId(notebook_id)})
    return redirect(url_for('index'))
    


@app.route('/new_note/<notebook_id>', methods = ['GET', 'POST'])
def new_note(notebook_id):
    new_note = {
                'title': 'New Note',
                'note': 'Take a note!',
                'notebook_id': ObjectId(notebook_id)
            }
    mongo.db.notes.insert(new_note)
    return redirect(url_for('note', note_id=new_note['_id'], notebook_id=notebook_id))


@app.route('/note/<note_id>/<notebook_id>', methods=['GET', 'POST'])
def note(note_id, notebook_id):
    note = mongo.db.notes.find_one({'_id': ObjectId(note_id)})
    notebook = mongo.db.notebooks.find_one({'_id': ObjectId(notebook_id)})
    edit = False
    delete = False
    if request.method == 'POST':
        if request.form.get('edit'):
            edit = True
        elif request.form.get('delete'):
            delete= True
            flash('Delete Note?')
        return render_template('note.html', note=note, edit=edit, delete=delete, notebook=notebook)
    else:
        return render_template('note.html', note=note, edit=edit, delete=delete, notebook=notebook)



@app.route('/save_note/<note_id>', methods=['POST'])
def save_note(note_id):
    note = mongo.db.notes.find_one({'_id': ObjectId(note_id)})
    note['title'] = request.form['title']
    note['note'] = request.form['note']
    mongo.db.notes.save(note)
    return redirect(url_for('note',note_id = note_id, notebook_id=note['notebook_id']))



@app.route('/delete_note/<note_id>', methods = ['GET', 'POST'])
def delete_note(note_id):
    note = mongo.db.notes.find_one({'_id': ObjectId(note_id)})
    notebook_id = note['notebook_id']
    mongo.db.notes.delete_one({'_id': ObjectId(note_id)})
    return redirect(url_for('notebook', notebook_id=notebook_id))