from flask import Flask, render_template, request, redirect, url_for, flash
import os
import db
import validators

UPLOAD_FOLDER = 'static/uploads'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

connection = db.connect_to_database()
db.init_db(connection)



@app.route('/product', methods=[ 'Get','POST'])
def product():
    if request.method == 'POST':

        photo = request.files.get('profile_picture')
        if photo:
            if not validators.allowed_file_size(photo):
                return f"Unallowed photo size."
            elif not validators.allowed_file(photo.filename):
                return f"Unallowed photo extention."
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo.filename))
        product_data = {
                "name": request.form.get('product_name'),
                "description": request.form.get('description'),
                "price": request.form.get('price'),
                "img": photo.filename,
                "Category": request.form.get('Category')
        }
        db.add_product(connection,product_data)
        return f'product added'
    
    return render_template('add-product.html')
    


if __name__ == "__main__":
    app.run(debug=True)
