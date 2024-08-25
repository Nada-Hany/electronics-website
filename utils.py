import re
import bcrypt  # type: ignore

import hmac
import hashlib



def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)

    return hashed_password.decode()


def is_password_match(entered_password, stored_hash):
    stored_hash_bytes = stored_hash.encode()

    return bcrypt.checkpw(entered_password.encode(), stored_hash_bytes)


def is_strong_password(password):
    min_length = 8
    require_uppercase = True
    require_lowercase = True
    require_digit = True
    require_special_char = True

    if password ==" ": 
        return False
    
    if len(password) < min_length:
        return False

    if require_uppercase and not any(char.isupper() for char in password):
        return False

    if require_lowercase and not any(char.islower() for char in password):
        return False

    if require_digit and not any(char.isdigit() for char in password):
        return False

    if require_special_char and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

def valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.search(email_regex, email) :
        return False
    return True

def valid_username(username):
    min_len = 3
    if len(username) < min_len:
      return False
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", username):
        return False
    return True

def valid_phone(phone):
    ph_len = 11
    ph_regex = r'^\d+$'
    if len(phone) != ph_len:
        return False
    if not re.search(ph_regex, phone) :
        return False
    return True

def requierd_Data(name,passw,email,phone):
    if name or passw or email or phone == "":
        return False
    return True
def validate_input(strinp):

   if re.search(r"[!@#$%^&*(),.?\":{}|<>]", strinp):
    return True

    return False

def validate_input(tel):
    if len(tel) < 10 or not tel.isdigit():
        return False

    return True

def is_valid_card_number(card_number):
    if not card_number.isdigit() or not (13 <= len(card_number) <= 19):
        return False
    return True
def get_product_by_id(products_list, product_id):
    for product in products_list:
        if product['product_id'] == int(product_id):
            return product
    return None

def create_mac(price):
    secret_key = b'supersecretkey'
    price_bytes = str(price).encode('utf-8')
    mac = hmac.new(secret_key, price_bytes, hashlib.sha256).hexdigest()
    return mac
