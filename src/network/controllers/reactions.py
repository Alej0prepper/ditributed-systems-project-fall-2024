from flask import session, jsonify
from network.middlewares.use_db_connection import use_db_connection
from network.middlewares.auth import needs_authentication
from database.connection import driver
from network.services.reactions import react_to_a_comment_service, react_to_a_post_service, get_reactions_count_by_id

@use_db_connection
@needs_authentication
def react_to_a_post(reaction, post_id, driver=None):
    return react_to_a_post_service(driver, reaction, session["username"], post_id)

@use_db_connection
@needs_authentication
def react_to_a_comment(reaction, comment_id, driver=None):
    return react_to_a_comment_service(driver, reaction, session["username"], comment_id)
    

@use_db_connection
def get_reactions_count_by_id_controller(entity_id, driver=None):
    """
    Controlador para obtener el número de reacciones de un comentario o post dado su ID.
    Se espera que el ID sea proporcionado como parámetro en la URL.
    """
    return get_reactions_count_by_id(driver, entity_id)