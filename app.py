from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from markupsafe import escape
from urllib.parse import urlparse
import db
import os
import utils

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
connection = db.connect_to_database()
app.secret_key = "SUPER-SECRET"
db.init_db(connection)
@app.route('/checkout',methods=['POST', 'GET'])
def checkout ():
    product_id = request.args.get('product_id')
    price = request.args.get('price')
    real_price = utils.get_product_by_id(products, product_id).get('price')
    session['Correct_MAC'] = utils.create_mac(real_price)

    if request.method == 'POST':
        username = request.form['username']
        card_number = request.form['card-number']
        cardholder=request.form['cardholder']
        address=request.form['address']
        tel=request.form['tel']
        user = db.get_user(connection, username)
        if not user:
            flash("Username Not Exists")
            return redirect(url_for('signUP.html'))
        elif not utils.is_valid_card_number(card_number) :
            flash("Invalid card number", "danger")
            return render_template('checkout.html', product_id=product_id, price=price)

        elif utils.validate_input(cardholder):
            flash("Special Characters Are Not Allowed in Cardholder","warning")
            return render_template('checkout.html', product_id=product_id, price=price)

        elif utils.validate_input(address):
            flash("Special Characters Are Not Allowed in Address","warning")
            return render_template('checkout.html', product_id=product_id, price=price)

        elif not utils.validate_phone(tel):
            flash("Invalid Phone Number")
            return render_template('checkout.html', product_id=product_id, price=price)

        else:
            return redirect(url_for('confirm.html'))

    return render_template('checkout.html', product_id=product_id, price=price)

@app.route('/confirm',methods=['POST'])
def confirm_pur():
    product_id = request.form['product_id']
    price = request.form['price']

    user_Correct_MAC = utils.create_mac(price)

    if 'Correct_MAC' in session and session['Correct_MAC'] == user_Correct_MAC:
        return f"Purchase confirmed at price ${price}."
    else:
        return f"Purchase Failed, Please Try Again",400


if __name__ == '__main__':
    db.init_db(connection)
    app.run(debug=True)


