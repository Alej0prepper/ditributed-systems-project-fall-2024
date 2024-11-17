import bcrypt
from flask import session
from network.services.users import add_user, get_user_by_email, get_user_by_username
from network.controllers.utils import use_db_connection

@use_db_connection
def register_user(name, username, email, password, driver=None):
    user_id, ok, error = add_user(driver, name, username, email, hash_password(password))
    if ok:
        print(f"User with name: {name} created successfully. (ID: {user_id})")
        return user_id, None
    else:
        print("Error registering user")
        return None, error

@use_db_connection
def login_user(password, username=None, email=None, driver=None):
    if not username and not email:
        return Exception("Error (Login): username or email are required")
    if username:
        user = get_user_by_username(driver, username)
    elif email:
        user = get_user_by_email(driver, email)
    session["username"] = user["username"]
    session["email"] = user["email"]

    if not verify_password(password, user["password"]):
        return False
    return True

def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

def verify_password(plain_password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)