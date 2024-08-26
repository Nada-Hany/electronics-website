import re
import bcrypt
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

    if len(password) == 0:
        return "Password cannot be empty."

    if len(password) < min_length:
        return f"Password must be at least {min_length} characters long."

    if require_uppercase and not any(char.isupper() for char in password):
        return "Password must contain at least one uppercase letter."

    if require_lowercase and not any(char.islower() for char in password):
        return "Password must contain at least one lowercase letter."

    if require_digit and not any(char.isdigit() for char in password):
        return "Password must contain at least one digit."

    if require_special_char and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must contain at least one special character."

    return "Password is strong."

def valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, email):
        return "Invalid email address."
    return "Email is valid."

def valid_username(username):
    min_len = 3
    if len(username) < min_len:
        return f"Username must be at least {min_len} characters long."

    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", username):
        return "Username should not contain special characters."

    return "Username is valid."

def valid_phone(phone):
    ph_len = 11
    ph_regex = r'^\d+$'
    if len(phone) != ph_len:
        return f"Phone number must be {ph_len} digits long."

    if not re.match(ph_regex, phone):
        return "Phone number should contain only digits."

    return "Phone number is valid."

def required_data(name, passw, email, phone):
    if not name:
        return "Name is required."
    if not passw:
        return "Password is required."
    if not email:
        return "Email is required."
    if not phone:
        return "Phone number is required."
    return "All required fields are filled."


def requierd_Data(name,passw,email,phone):
    if name or passw or email or phone == "":
        return False
    return True

def validate_input(strinp):
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", strinp):
        return True

    return False

def validate_phone(tel):
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