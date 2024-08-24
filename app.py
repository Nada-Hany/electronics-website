from flask import Flask, render_template, request, redirect, url_for, session, flash
import db
import os
import utils
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import validators

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.secret_key = "SUPER-SECRET"
limiter = Limiter(app=app, key_func=get_remote_address,
                  default_limits=["50 per minute"], storage_uri="memory://")

UPLOAD_FOLDER = 'static/uploads'

connection = db.connect_to_database()


db.init_db(connection)
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
        username= request.form['username']
        password= request.form['password']
        user = db.get_user(connection,username)
        if user:
            if utils.is_password_match(password,user[2]):
                session['username']= user[1]
                return redirect(url_for('index'))
            else:
                flash("wrong password","danger")
                return render_template('login.html')
        else:
            print("invalid username")
            flash("invalid username","danger")
            return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

#Resister 
@app.route('/register', methods=['GET','POST'])
@limiter.limit("10 per minute")
def signUp():
   if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        phone = request.form.get('phone')
        if not username or not password or not email or not phone :
            flash("Missing Data", "danger")
        elif not utils.valid_username(username):
            flash("invalid username", "danger")
            return render_template('signUp.html')    
        elif not utils.is_strong_password(password):
            flash("Weak Password Please Choose a stronger one", "danger")
            return render_template('signUp.html')
        elif not utils.valid_email(email):
            flash("invalid email", "danger")
            return render_template('signUp.html')
        elif not utils.valid_phone(phone):
            flash("invalid phone number", "danger")
            return render_template('signUp.html')
        else :
          user = db.get_user(connection, username)
          if user:
            flash("Username already exists.", "danger")
            return render_template('signUp.html')
          else:
            db.add_user(connection, username, password , email, phone )
            return redirect(url_for('login'))

   return render_template("signUp.html")


@app.route('/product', methods=[ 'Get','POST'])
def product():
    if request.method == 'POST':
        photoPath = ""
        form_type = request.form.get('form_name')
        if form_type == 'upload_photo':
            photo = request.files.get('profile_picture')
            if photo:
                if not validators.allowed_file_size(photo):
                    return f"Unallowed photo size."
                elif not validators.allowed_file(photo.filename):
                    return f"Unallowed photo extention."
            photoPath=os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
            photo.save(photoPath)
        elif form_type == 'upload_product':
            product_data = {
                    "name": request.form.get('product_name'),
                    "description": request.form.get('description'),
                    "price": request.form.get('price'),
                    "img": "photoPath",
                    "Category": request.form.get('Category')
            }
            for data in product_data.values():
                if data == None or data =='':
                    return 'enter full data'
            db.add_product(connection,product_data)
            return f'product added'
    
    return render_template('add-product.html')
    

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

