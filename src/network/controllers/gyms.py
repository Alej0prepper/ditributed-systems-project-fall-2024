from flask import session
from network.middlewares.use_db_connection import use_db_connection
from network.middlewares.auth import needs_authentication
from network.services.gyms import add_gym
from network.services.gyms import update_gym
from network.services.gyms import get_gym_info
from network.services.gyms import delete_gym
@use_db_connection
def add_gym_controller(name,email,location,address,styles,phone_number = None ,ig_profile = None,driver = None):
    return add_gym(driver, name,email,location,address,styles,phone_number,ig_profile)

@use_db_connection
@needs_authentication
def update_gym_controller(gym_id, name, email,location,address,styles, phone_number=None, ig_profile = None,driver =None):
    return update_gym(driver,gym_id,name,email,location,address,styles,phone_number,ig_profile)

@use_db_connection
def get_gym_info_controller(gym_id,driver =None):
    gym_id = int(gym_id)
    return get_gym_info(driver,gym_id)   

@use_db_connection
@needs_authentication
def delete_gym_controller(gym_id,driver=None):
    gym_id = int(gym_id)
    return delete_gym(driver,gym_id)