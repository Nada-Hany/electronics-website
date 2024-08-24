
import utils

def connect_to_database(name='database.db'):
    import sqlite3
    return sqlite3.connect(name, check_same_thread=False)
    


def init_db(connection):
    cursor = connection.cursor()

    cursor.execute('''
		CREATE TABLE IF NOT EXISTS users (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			username TEXT NOT NULL UNIQUE,
			password TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE, 
            contact INTEGER NOT NULL,
            img TEXT
		);
	''')

    cursor.execute('''
		CREATE TABLE IF NOT EXISTS products (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			name TEXT NOT NULL ,
			description TEXT,
            price INTEGER NOT NULL,
            img TEXT Not Null,
            Category TEXT Not Null
		);
	''')

    cursor.execute('''
		CREATE TABLE IF NOT EXISTS payment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGERR,
            products_id INTEGERR,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (products_id) REFERENCES products(id)
		);
	''')
    

    connection.commit()

def add_user(connection, username, password, email ="", contact ="", img =""):
    cursor = connection.cursor()
    hashed_password = utils.hash_password(password)
    query = '''INSERT INTO users (username, password, email, contact, img) VALUES (?, ?, ?, ?, ?)'''
    cursor.execute(query, (username, hashed_password, email, contact, img))
    connection.commit()

def add_product(connection,product_data):
    cursor = connection.cursor()
    query = '''INSERT INTO products (name, description, price,img,Category) VALUES (?, ?, ?,?,?)'''
    cursor.execute(query, (product_data['name'], product_data['description'], product_data['price'],product_data['img'],product_data['Category']))
    connection.commit()


def delete_user(connection, username):
    cursor = connection.cursor()
    query = ''' DELETE FROM users WHERE username = ? '''
    cursor.execute(query, (username,)) 
    connection.commit()

def update_user(connection , user_data):
    cursor = connection.cursor()
    query = ''' UPDATE users set email = ? , contact = ? WHERE username = ? '''
    cursor.execute(query,(user_data['email'] , user_data['contact'] , user_data['username']))
    connection.commit() 

def update_user_photo(connection, filename , username):
    cursor = connection.cursor()  
    query = '''UPDATE users SET img = ? WHERE username = ?'''
    cursor.execute(query, (filename,username))  
    connection.commit()  

def update_product_photo(connection, filename , name):
    cursor = connection.cursor()  
    query = '''UPDATE products SET img = ? WHERE name = ?'''
    cursor.execute(query, (filename,name))  
    connection.commit() 

def get_user(connection, username):
    cursor = connection.cursor()
    query = '''SELECT * FROM users WHERE username = ?'''
    cursor.execute(query, (username,))
    return cursor.fetchone()

def get_product(connection, name):
    cursor = connection.cursor()
    query = '''SELECT * FROM products WHERE name = ?'''
    cursor.execute(query, (name,))
    return cursor.fetchone()

def get_all_users(connection):
    cursor = connection.cursor()
    query = 'SELECT * FROM users'
    cursor.execute(query)
    return cursor.fetchall()

def seed_admin_user(connection):
    admin_username = 'admin'
    admin_password = 'admin'

    admin_user = get_user(connection, admin_username)
    if not admin_user:
        add_user(connection, admin_username, admin_password)
        print("Admin user seeded successfully.")