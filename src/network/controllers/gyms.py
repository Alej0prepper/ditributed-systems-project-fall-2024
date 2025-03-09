import bcrypt
from flask import session
from network.middlewares.token import generate_token
from network.middlewares.use_db_connection import use_db_connection
from network.middlewares.auth import needs_authentication
from network.services.gyms import add_gym, get_all_gyms_service, update_gym, delete_gym, get_gym_by_email, get_gym_by_username
from network.services.gyms import get_gyms_by_search_term_service
from network.services.gyms import get_gym_by_id_service

@use_db_connection
def login_gym(username, email, password, driver = None):
    if username:
        gym = get_gym_by_username(driver, username)
        
    elif email:
        gym = get_gym_by_email(driver, email)
    if gym == None: 
        return None, False, "Gym account not found."
    
    session["username"] = gym["username"]
    session["email"] = gym["email"]

    if not verify_password(password, gym["password"]):
        return None, False, "Wrong password"
    
    data = {
        "token": generate_token(gym["id"], gym["username"], gym["email"]),
        "role": "gym", 
        "id": gym['id'] 
    }

    return data, True, None

@use_db_connection
def add_gym_controller(name, username, email, description, image_url, location, styles, password,phone_number = None ,ig_profile = None,driver = None, id=None):
    return add_gym(driver, id, name, username,email, description, image_url, location, styles, hash_password(password),phone_number,ig_profile)

@use_db_connection
@needs_authentication
def update_gym_controller(name, username, email, description,image_url, location,styles, password, phone_number, ig_profile, driver =None):
    return update_gym(driver, name,username,email, description,image_url, location,styles, hash_password(password),phone_number,ig_profile)

@use_db_connection
def get_gym_by_id_controller(id,driver=None):
    return get_gym_by_id_service(driver,id)   

@use_db_connection
@needs_authentication
def delete_gym_controller(username,driver=None):
    return delete_gym(driver,username)


def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

def verify_password(plain_password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

@use_db_connection
def get_gyms_by_search_term(gyms, query):
    return get_gyms_by_search_term_service(gyms, query)

@use_db_connection
def get_all_gyms_controller(driver=None):
    return get_all_gyms_service(driver)

@use_db_connection
@needs_authentication
def get_logged_gym_controller(driver=None):
    gym = get_gym_by_username(driver, session["username"])
    if gym:
        gym.pop("password", None)
        return gym, True, None
    return None, False, "Gym not found."

@use_db_connection
def get_gym_by_username_controller(username, driver=None):
    gym = get_gym_by_username(driver, username)
    if gym:
        gym.pop("password", None)
        return gym, True, None
    return None, False, "Gym not found."

@use_db_connection
@needs_authentication
def get_gym_trainees_by_id_controller(driver=None):
    """
    Controller to retrieve trainees of a gym by its ID.
    
    :param gym_id: ID of the gym.
    :param driver: Connection to the graph.
    :return: Tuple (trainees, success, error).
    """
    return get_gym_trainees_by_id_service(driver, session["id"])
