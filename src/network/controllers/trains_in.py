from flask import session
from network.middlewares.use_db_connection import use_db_connection
from network.middlewares.auth import needs_authentication
from database.connection import driver
from network.services.trains_in import add_training_styles_service, remove_training_styles_service, trains_in_service


@use_db_connection
# @needs_authentication
def add_training_styles(styles, gym_id, driver=None):
    return add_training_styles_service(driver, styles, session["username"], gym_id)

@use_db_connection
# @needs_authentication
def remove_training_styles(styles, gym_id, driver=None):
    return remove_training_styles_service(driver, styles, session["username"], gym_id)

@use_db_connection
# @needs_authentication
def trains_in(styles,gym_id, driver=None):
    return trains_in_service(driver,styles, session["username"], gym_id)
