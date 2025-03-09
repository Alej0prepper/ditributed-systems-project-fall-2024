from flask import session
from network.middlewares.use_db_connection import use_db_connection
from network.middlewares.auth import needs_authentication
from database.connection import driver
from network.services.reactions import react_to_a_comment_service, react_to_a_post_service,delete_reaction
import chord.protocol_logic as chord

@use_db_connection
@needs_authentication
def react_to_a_post(reaction, post_id, driver=None):
    for et, em, id in chord.system_entities_set:
        if id ==post_id:
            entity_type = et
            break
    return react_to_a_post_service(driver, reaction, session["username"], et, post_id)

@use_db_connection
@needs_authentication
def react_to_a_comment(reaction, comment_id, driver=None):
    return react_to_a_comment_service(driver, reaction, session["username"], comment_id)

@use_db_connection
def get_reactions_controller(target_id, driver=None):
    """
    Controlador para obtener reacciones de un post o comentario.

    :param target_id: ID del post o comentario.
    :param driver: Conexión al grafo.
    :return: Lista de reacciones.
    """
    return get_reactions_service(driver, target_id)

@use_db_connection
def delete_reaction_controller(reacted_comment_id=None, reacted_post_id=None, driver=None):
    """
    Controlador para eliminar una reacción de un comentario o post.

    Este controlador utiliza el servicio `delete_reaction` para eliminar una reacción
    asociada con un comentario o post. Requiere el nombre de usuario del que realiza
    la acción y el ID del comentario o post al que pertenece la reacción.

    Args:
        username (str): Nombre de usuario que realiza la acción.
        reacted_comment_id (int, optional): ID del comentario al que pertenece la reacción. Defaults to None.
        reacted_post_id (int, optional): ID del post al que pertenece la reacción. Defaults to None.
        driver: Conexión al grafo de Neo4j (inyectada por decorador).

    Returns:
        tuple: Resultado de la operación de eliminación (devuelto por el servicio `delete_reaction`)

    Raises:
        Exception: Si ocurre un error durante la ejecución de la consulta.
    """
    return delete_reaction(driver, session["username"], reacted_comment_id, reacted_post_id)
