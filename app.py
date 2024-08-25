from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from markupsafe import escape
from urllib.parse import urlparse
from itsdangerous import TimedSerializer as ts
import db
import os
import utils
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
connection = db.connect_to_database()
app.secret_key = "SUPER-SECRET"
limiter = Limiter(app=app, key_func=get_remote_address,
                  default_limits=["50 per minute"], storage_uri="memory://")


db.init_db(connection)
@app.route('/')
def index():
    if 'username' in session:
        print(session['username'])
        if session['username'] == 'admin':
            return list(db.get_all_users(connection))
        else:
            return render_template('index.html')
    return redirect(url_for('login'))


@app.route('/login',methods=['POST','GET'])
@limiter.limit("10 per minute")
def login():
    if request.method == 'POST':
        username= escape(request.form['username'])
        password= escape(request.form['password'])
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

def is_valid_url(server):
    parsed_url = urlparse(server)
    if parsed_url.scheme not in ['http', 'https']:
        return False
    whitelist = [5000]
    return parsed_url.port in whitelist

@app.route('/forget_password',methods=['POST','GET'])
def forget_password():
    if request.method== 'POST':
        email= escape(request.form['email'])
        user = db.get_user_by_email(connection,email)
        if user:
            
            return "sent email successfully"
        else:
            return render_template('forget-password.html')
    return render_template('forget-password.html')

if __name__ == '__main__':
    db.init_db(connection)
    app.run(debug=True)
        