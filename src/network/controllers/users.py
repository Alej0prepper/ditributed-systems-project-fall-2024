import bcrypt
from flask import session
from network.controllers.trains_in import trains_in
from network.middlewares.token import generate_token
from network.services.users import add_user, get_all_users_service, get_user_by_email, get_user_by_id_service, get_user_by_username_service
from network.middlewares.use_db_connection import use_db_connection
from network.middlewares.auth import needs_authentication
from network.services.users import create_follow_relation
from network.services.users import remove_follow_relation
from network.services.users import update_user
from network.services.users import get_users_by_search_term_service
from network.services.users import delete_user_service, get_follows_by_user_id_service, get_followers_by_user_id_service
import ast


@use_db_connection
def register_user(_id, name, username, email, image_url, password, weight, styles, levels_by_style, birth_date, gyms_ids,description, driver=None):
    user_id, ok, error = add_user(driver, _id, name, username, email, image_url, hash_password(password), weight, styles, levels_by_style, birth_date,description)
    if ok:
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
    
    if not verify_password(password, user["password"]):
        return None, False, "Wrong password"
    
    data = {
        "token": generate_token(user["id"], user["username"], user["email"]),
        "role": "user", 
        "id": user['id'] 
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
def follow_account(followed_username,followed_type, driver=None):
    return create_follow_relation(driver, session["username"], followed_username,"User",followed_type)

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
def update_user_account(name, email, password, image_url, weight, styles, levels_by_style, birth_date,description, driver=None):
    return update_user(driver, name, session["username"], email, hash_password(password), image_url, weight, styles, levels_by_style, birth_date,description)

def get_users_by_search_term(query, users):
    return get_users_by_search_term_service(users, query)

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
def get_user_by_id_controller(_id, driver=None):
    user = get_user_by_id_service(driver, _id)
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


from flask import session

@use_db_connection
def get_follows_by_user_id_controller(user_id, driver=None):
    """
    Controller to get the list of users followed by the logged-in user.
    Requires authentication.
    """
    follows, success, error = get_follows_by_user_id_service(driver, user_id)

    if success:
        # Optionally, remove sensitive information (e.g., password) from followed users
        for follow in follows:
            if "password" in follow:
                del follow["password"]
        return follows, True, None
    else:
        return None, False, error
@use_db_connection
def get_followers_by_user_id_controller(user_id,driver = None):
    followers,success,error = get_followers_by_user_id_service(driver,user_id)
    if success:
        for follower in followers:
            if "password" in follower:
                del follower["password"]
        return followers,True,None
    else: 
        return None,False,error