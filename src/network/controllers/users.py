import bcrypt
from flask import session
import json
from network.controllers.trains_in import trains_in
from network.middlewares.token import generate_token
from network.services.users import add_user, get_all_users_service, get_user_by_email, get_user_by_username_service
from network.middlewares.use_db_connection import use_db_connection
from network.middlewares.auth import needs_authentication
from network.services.users import create_follow_relation
from network.services.users import remove_follow_relation
from network.services.users import update_user
from network.services.users import get_users_by_search_term_service
from network.services.users import delete_user_service
import ast


@use_db_connection
def register_user(name, username, email, image_url, password, weight, styles, levels_by_style, birth_date, gyms_ids, driver=None):
    user_id, ok, error = add_user(driver, name, username, email, image_url, hash_password(password), weight, styles, levels_by_style, birth_date)
    if ok:
        login_user(password, email=email)
        if gyms_ids:
            for gym_id in ast.literal_eval(gyms_ids):
                trains_in([],gym_id)
        return user_id, None
    else:
        return None, error

@use_db_connection
def login_user(password, username=None, email=None, driver=None):
    user = None

    if username:
        user = get_user_by_username_service(driver, username)
    if not user and email:
        user = get_user_by_email(driver, email)
    
    if user is None: 
        return None, False, "User not found."
    
    session["username"] = user["username"]
    session["email"] = user["email"]

    if not verify_password(password, user["password"]):
        return None, False, "Wrong password"
    
    data = {
        "token": generate_token(user["username"], user["email"]),
        "role": "user" 
    }

    return data, True, None

def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

def verify_password(plain_password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

@use_db_connection
@needs_authentication
def follow_account(followed_username, driver=None):
    return create_follow_relation(driver, session["username"], followed_username)

@use_db_connection
@needs_authentication
def unfollow_user(followed_username, driver=None):
    return remove_follow_relation(driver, session["username"], followed_username)

@use_db_connection
@needs_authentication
def delete_user_account(driver=None):
    return delete_user_service(driver, session["username"])

@use_db_connection
@needs_authentication
def update_user_account(name, email, password, image_url, weight, styles, levels_by_style, birth_date, driver=None):
    return update_user(driver, name, session["username"], email, hash_password(password), image_url, weight, styles, levels_by_style, birth_date)

@use_db_connection
def get_users_by_search_term(query, driver=None):
    return get_users_by_search_term_service(driver, query)

@use_db_connection
def get_all_users_controller(query, driver=None):
    return get_all_users_service(driver, query)

@use_db_connection
def get_user_by_username_controller(username, driver=None):
    user = get_user_by_username_service(driver, username)
    if user:
        user.pop("password", None)
        return user, True, None
    return None, False, "User not found."

@use_db_connection
@needs_authentication
def get_logged_user_controller(driver=None):
    user = get_user_by_username_service(driver, session["username"])
    if user:
        user.pop("password", None)
        return user, True, None
    return None, False, "User not found."

