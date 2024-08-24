from flask import Flask, render_template, request, redirect, url_for, session, flash
import db
import os
import utils
import validators
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename



app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
connection = db.connect_to_database()
app.secret_key = "SUPER-SECRET"
limiter = Limiter(app=app, key_func=get_remote_address,
                  default_limits=["50 per minute"], storage_uri="memory://")


db.init_db(connection)


#----------------------------------------------------------------------------

# This is temporary code until the registration function is completed.

users = [
    {"username": "rusul", "plain_password": "rusul@123456789"},
    {"username": "rusultest", "plain_password": "Rusul@123456789"}
]

for user in users:
    hashed_password = utils.hash_password(user["plain_password"])
    query = f"""
        UPDATE users
        SET password = ?
        WHERE username = ?
    """
    connection.execute(query, (hashed_password, user["username"]))
    connection.commit()


#----------------------------------------------------------------------------
@app.route('/')
def index():
    if 'username' in session:
        if session['username'] == 'admin':
            return list(db.get_all_users(connection))
        else:
            return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/login',methods=['POST','GET'])
@limiter.limit("10 per minute")
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = db.get_user(connection, username)
        
        if user:
            if utils.is_password_match(password, user[2]): 
                session['username'] = user[1]  
                return redirect(url_for('index'))
            else:
                flash("Wrong password", "danger")
                return render_template('login.html')
        else:
            flash("Invalid username", "danger")
            return render_template('login.html')
    
    return render_template('login.html')



@app.route('/update-profile', methods=['GET', 'POST'])
def update_profile():
    if 'username' not in session:
        return redirect(url_for('login'))  
    
    username = request.args.get('username', session['username'])

    if request.method == 'GET':
        if username != session['username']:
            return "unauthorized"
        data = db.get_user(connection, username)
        return render_template('update-profile.html', data=data)

    elif request.method == 'POST':
        form_type = request.form.get('form_name')

        if username != session['username']:
            return 'unauthorized'
    
        if form_type == 'update_user_data':
            user_data = {
                "username": username,
                "password": request.form.get('password'),
                "email": request.form.get('email'),
                "contact": request.form.get('contact'),
                "img": request.form.get('img')
            }
            db.update_user(connection, user_data)
            flash('Profile updated successfully.')

        elif form_type == 'upload_photo':
            photo = request.files.get('profile_picture')
            if photo:
                if not validators.allowed_file_size(photo):
                    return "Unallowed size."
                elif not validators.allowed_file(photo.filename):
                    return "Unallowed extension."
                else:
                    filename = secure_filename(photo.filename)
                    db.update_photo(connection, filename, username)
                    photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    flash('Photo uploaded successfully.')

        data = db.get_user(connection, username)
        if not data:
            return "User not found", 404
        
        return render_template('update-profile.html', data=data)


@app.route('/upload', methods=['POST'])
def upload():
    if 'username' in session:
        photo = request.files.get('profile_picture')
        if photo:
            if not validators.allowed_file_size(photo):
                return "Unallowed size."
            elif not validators.allowed_file(photo.filename):
                return "Unallowed extension."
            else:
                username = session['username']
                db.update_photo(connection, photo.filename, username)
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo.filename))
                return redirect(url_for('update_profile'))
    else:
        return redirect(url_for('login'))



@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    db.init_db(connection)
    app.run(debug=True)