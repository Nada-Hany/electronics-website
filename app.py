from flask import Flask, render_template, request, redirect, url_for, session, flash
import db
import os
import utils
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = 'static/uploads'
connection = db.connect_to_database()
# app.secret_key = "SUPER-SECRET"
# limiter = Limiter(app=app, key_func=get_remote_address,
#                   default_limits=["50 per minute"], storage_uri="memory://")


db.init_db(connection)


@app.route('/admin_list', methods=['GET', 'POST'])
def admin_list():
    if request.method == 'GET':
        users = db.get_all_users(connection)
        return render_template('userList.html', users=users)
    elif request.method == 'POST':
        action = request.form.get('action')
        temp_username = request.form.get('user_username')
        if action == 'edit':
            
            return redirect(url_for('admin_list'))
            # call update function 
        elif action == 'delete':

            db.delete_user(connection,temp_username) 
            return redirect(url_for('admin_list'))

            # return redirect(url_for('admin_list'))

    # if 'username' in session:
    #     if session['username'] == 'admin':
    #         users = db.get_all_users(connection)
    #         return render_template('admin_dashboard.html', users=users)
    #     else:
    #         return render_template('index.html')
    # return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

