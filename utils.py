import re
import bcrypt
# from wtforms.validators import DataRequired,Length,Email,Regexp



def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    print(hashed_password, "while signing in")
    return hashed_password.decode()


def is_password_match(entered_password, stored_hash):
    stored_hash_bytes = stored_hash.encode()
    print(stored_hash_bytes, "hashed while log in hashed pass")
    # print(entered_password.encode(), "actual password while logging in")
    return bcrypt.checkpw(entered_password.encode(), stored_hash_bytes)


def is_strong_password(password):
    min_length = 8
    require_uppercase = True
    require_lowercase = True
    require_digit = True
    require_special_char = True

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
    if not re.match(email_regex, email):
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

    if not re.match(ph_regex, phone):
        return False

    return True

