import bcrypt
from flask import session
from network.services.users import add_user, get_user_by_email, get_user_by_username
from network.middlewares.use_db_connection import use_db_connection
from network.middlewares.auth import needs_authentication
from database.connection import driver
from network.services.users import create_follow_relation
from network.services.users import remove_follow_relation

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
    if username:
        user = get_user_by_username(driver, username)
    elif email:
        user = get_user_by_email(driver, email)
    if user == None: 
        return None, False, "User not found."
    
    session["username"] = user["username"]
    session["email"] = user["email"]

    if not verify_password(password, user["password"]):
        return None, False, "Wrong password"
    return None, True, None

def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    return hashed

def verify_password(plain_password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

@use_db_connection
@needs_authentication
def follow_user(followed_username, driver=None):
    return create_follow_relation(driver, session["username"], followed_username)


@use_db_connection
@needs_authentication
def unfollow_user(followed_username, driver=None):
    return remove_follow_relation(driver, session["username"], followed_username)