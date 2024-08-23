from flask import Flask ,render_template,url_for , flash, redirect,request
import db
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

@app.route('/login')
def login():
    return render_template("login.html")

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




if __name__=='__main__' :
  db.init_db(connection)
  app.run(debug=True)
