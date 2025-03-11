from flask import session, jsonify

from network.middlewares.use_db_connection import use_db_connection

from network.middlewares.auth import needs_authentication

from database.connection import driver

from network.services.reactions import react_to_a_comment_service, react_to_a_post_service, get_reactions_by_entity_id
import chord.protocol_logic as chord

@use_db_connection

@needs_authentication

def react_to_a_post(reaction, post_id, driver=None):
    et = "ET"
    for a,b,c in chord.system_entities_set:
        if session['id'] == c:
            et = a
    return react_to_a_post_service(driver, reaction, session["username"],et, post_id)


@use_db_connection

@needs_authentication

def react_to_a_comment(reaction, comment_id, driver=None):
    et = "ET"
    for a,b,c in chord.system_entities_set:
        if session['id'] == c:
            et = a
    return react_to_a_comment_service(driver, reaction, session["username"],et, comment_id)
    


@use_db_connection

def get_reactions_by_entity_id_controller(entity_id, driver=None):

    """

    Controlador para obtener el número de reacciones de un comentario o post dado su ID.

    Se espera que el ID sea proporcionado como parámetro en la URL.

    """

    return get_reactions_by_entity_id(driver, entity_id)

