from network.middlewares.auth import needs_authentication
from network.middlewares.use_db_connection import use_db_connection
from flask import session
from network.services.posts import post, repost, delete_post_service, get_post_by_id, get_posts_by_user_id, get_user_by_post_id

@use_db_connection
@needs_authentication
def create_post(media, caption, driver=None, id=None):
    return post(driver, id, media, caption, session["username"],session["email"])

@use_db_connection
@needs_authentication
def repost_existing_post(reposted_post_id:int, driver=None):
    return repost(driver, reposted_post_id, session["username"],session["email"])

@use_db_connection
@needs_authentication
def quote_existing_post(reposted_post_id:id, media, caption, driver=None):
    return repost(driver, reposted_post_id, session["username"],session["email"], media, caption)

@use_db_connection
def delete_post(post_id, driver=None):
    return delete_post_service(driver, post_id, session["username"],session["email"])

@use_db_connection
def get_post_by_id_controller(post_id, driver=None):
    """
    Obtiene un post por su ID.
    
    :param post_id: ID del post a obtener.
    :param driver: Conexión al grafo (opcional, se maneja automáticamente con el decorador).
    :return: El post obtenido.
    """
    return get_post_by_id(driver, post_id)

@use_db_connection
def get_post_by_user_id_controller(user_id,driver = None):
    return get_posts_by_user_id(driver,user_id)

@use_db_connection
def get_user_by_post_id_controller(post_id,driver = None):
    return get_user_by_post_id(driver,post_id)