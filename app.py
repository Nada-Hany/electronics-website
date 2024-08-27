from flask import Flask, render_template, request, redirect, url_for, session, flash
import db
import os
import utils
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import validators
from werkzeug.utils import secure_filename
from markupsafe import escape
from urllib.parse import urlparse



app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.secret_key = "SUPER-SECRET"
limiter = Limiter(app=app, key_func=get_remote_address,
default_limits=["50 per minute"], storage_uri="memory://")


UPLOAD_FOLDER = 'static/uploads'

connection = db.connect_to_database()

db.init_db(connection)

@app.route('/',methods=['POST','GET'])
def index():
    if request.method == 'POST':
        search_query = escape(request.form['search_query'])
        print("search query in index - --", search_query)
        return redirect(url_for('search', search_query=search_query))
    if 'username' in session:
        if session.get('username') == 'admin':
            return redirect(url_for('admin_page'))
        else:
            cart_products, counter = db.get_cart_products(connection, session.get('username'))
            print(counter)
            print(cart_products)
            total_price = 0
            products = db.get_all_products(connection)  
            for product in cart_products:
                total_price += product[3]
            return render_template('index.html', products=products,cart_products = cart_products, counter = counter, total_price=total_price)
    return redirect(url_for('login'))


@app.route('/login',methods=['POST','GET'])
@limiter.limit("10 per minute")
def login():
    if request.method == 'POST':
        username= escape(request.form['username'])
        password= escape(request.form['password'])
        username= escape(request.form['username'])
        password= escape(request.form['password'])
        user = db.get_user(connection,username)

        if user:
            if utils.is_password_match(password,user[2]):
                session['username']= user[1]
                if(username != "admin"):
                    print("valid username and pas ---------------------------")
                    return redirect(url_for('index'))
                else:
                    return redirect(url_for('admin_page'))
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
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def signUp():
    if request.method == 'POST':
        username = escape(request.form.get('username'))
        password = escape(request.form.get('password'))
        email = request.form.get('email')
        phone = escape(request.form.get('phone'))
        print("email ---", email)
        # Validate input fields
        if not username or not password or not email or not phone:
            flash("All fields are required.", "danger")
        elif not utils.valid_username(username):
            flash("Invalid username. Must be at least 3 characters long and contain no special characters.", "danger")
        elif utils.is_strong_password(password) != "Password is strong.":
            flash("Weak password. Ensure your password is at least 8 characters long, includes uppercase and lowercase letters, a digit, and a special character.", "danger")
        elif not utils.valid_email(email):
            flash("Invalid email address.", "danger")
        elif not utils.valid_phone(phone):
            flash("Phone number should be 11 digits long and contain only digits.", "danger")
        else:
            user = db.get_user(connection, username)
            email_ = db.get_user_byEmail(connection, email)
            if user or email_:
                flash("Username already exists.", "danger")
            else:
                hashed_password = utils.hash_password(password)
                db.add_user(connection, username, hashed_password, email, phone)
                flash("User registered successfully!", "success")
                return redirect(url_for('login'))  # Redirect to login page or wherever appropriate

    # Render the signup page with any flash messages
    return render_template("signUp.html")


@app.route('/product', methods=['GET', 'POST'])
def product():

    if 'username' not in session:
        return redirect(url_for('login'))
 
    if request.method == 'POST':
        form_type = request.form.get('form_name')

        if form_type == 'upload_product':
            photo = request.files.get('product_picture')
            if photo:
                if not validators.allowed_file_size(photo):
                    return "Unallowed size."
                elif not validators.allowed_file(photo.filename):
                    return "Unallowed extension."
                else:
                    filename = secure_filename(photo.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    photo.save(file_path)
            else:
                filename = None

            product_data = {
                "name": request.form.get('product_name'),
                "description": request.form.get('description'),
                "price": request.form.get('price'),
                "category": request.form.get('category'),
                "img": filename
            }

            db.add_product(connection, **product_data)
            flash('Product added successfully.')

            return redirect(url_for('product', name=product_data["name"]))

    product_name = request.args.get('name')
    product = None
    if product_name:
        product = db.get_product(connection, product_name)

    return render_template('add-product.html', product=product)

    

@app.route('/add_product')
def add_product():
    print("inn add product to cart method ")
    product_id = request.args.get('product_id')
    username = session.get('username', "")
    print(product_id, "product id ----------  ", username)
    db.add_to_cart(connection=connection,username=username,productID=product_id)
    return redirect(url_for('index'))

@app.route('/update-profile', methods=['GET', 'POST'])
def update_profile():
    username = request.args.get('username')
    action = request.args.get('action')

    if 'username' not in session:
        return redirect(url_for('login'))

    if action != '2':
        username = request.args.get('username', session.get('username'))

    if request.method == 'GET':
        if action != '2' and username != session.get('username'):
            return f"unauthorized"
        data = db.get_user(connection, username)
        return render_template('update-profile.html', data=data)

    elif request.method == 'POST':
        form_type = request.form.get('form_name')

        if action != '2' and username != session.get('username'):
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
                username = session.get('username')
                db.update_user_photo(connection, photo.filename, username)
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo.filename))
                return redirect(url_for('update_profile'))
    else:
        return redirect(url_for('login'))


@app.route('/admin_list', methods=['GET', 'POST'])
def admin_list():
    if request.method == 'GET':
        users = db.get_all_users(connection)
        return render_template('userList.html', users=users)
    elif request.method == 'POST':
        action = request.form.get('action')
        temp_username = request.form.get('user_username')
        if action == 'edit':
            return redirect(url_for('update_profile', username = temp_username, action ="2"))
            # call update function 
        elif action == 'delete':
            db.delete_user(connection,temp_username) 
            return redirect(url_for('admin_list'))


@app.route('/admin_page', methods=['POST', 'GET'])
def admin_page():
    action = request.form.get('log-out-btn')
    if request.method == 'POST' and action=='log-out':
        return redirect(url_for('logout'))
    return render_template('admin-page.html')


@app.route('/checkout', methods=['POST', 'GET'])
def checkout ():

    products_id, counter = db.get_cart_products(connection, session.get('username'))
    whole_products = []
    real_price = 0
    for id in products_id:
        whole_products.append(id)
        real_price += id[3]
    session['Correct_MAC'] = utils.create_mac(real_price)

    if request.method == 'POST':
        username = request.form['username']
        card_number = request.form['card-number']
        cardholder=request.form['cardholder']
        address=request.form['address']
        tel=request.form['tel']
        order_notes = escape(request.form.get('order_notes'))
        print(f"Received order notes: {order_notes}")
        user = db.get_user(connection, username)
        if not user:
            flash("Username Not Exists")
            return redirect(url_for('signUP.html'))
        elif not utils.is_valid_card_number(card_number) :
            flash("Invalid card number", "danger")
            return render_template('checkout.html')

        elif utils.validate_input(cardholder):
            flash("Special Characters Are Not Allowed in Cardholder","warning")
            return render_template('checkout.html')

        elif utils.validate_input(address):
            flash("Special Characters Are Not Allowed in Address","warning")
            return render_template('checkout.html')

        elif not utils.validate_phone(tel):
            flash("Invalid Phone Number")
            return render_template('checkout.html')

        else:
            return redirect(url_for('confirm.html'))

    return render_template('checkout.html', products=whole_products, price=real_price, counter = counter, username = session.get('username'))



@app.route('/confirm',methods=['POST', 'GET'])
def confirm():
    
    price = request.args.get('price')
    # price = request.form['price']

    user_Correct_MAC = utils.create_mac(price)

    if 'Correct_MAC' in session and session['Correct_MAC'] == user_Correct_MAC:
        return f"Purchase confirmed at price ${price}."
    else:
        return f"Purchase Failed, Please Try Again",400



@app.route('/search', methods=[ 'GET'])
def search():
    if request.method == 'GET':
        search = request.args.get('search_query')
        print(search, "----------- search")
        if search:
            products = db.get_products_by_category(connection, search)
            return render_template('search-results.html', products=products)
        else:
            return render_template('search-results.html', products=[])
        
    


if __name__ == '__main__':
    db.init_db(connection)
    app.run(debug=True)
