from flask import session
from network.middlewares.use_db_connection import use_db_connection
from network.middlewares.auth import needs_authentication
from database.connection import driver
from network.services.reactions import react_to_a_comment_service, react_to_a_post_service

@use_db_connection
@needs_authentication
def react_to_a_post(reaction, post_id, driver=None):
    return react_to_a_post_service(driver, reaction, session["username"], post_id)

@use_db_connection
@needs_authentication
def react_to_a_comment(reaction, comment_id, driver=None):
    return react_to_a_comment_service(driver, reaction, session["username"], comment_id)