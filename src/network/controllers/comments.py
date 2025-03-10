from flask import session
from network.middlewares.use_db_connection import use_db_connection
from network.middlewares.auth import needs_authentication
from network.services.comments import comment_post
from network.services.comments import answer_comment, get_comments

@use_db_connection
@needs_authentication
def create_post_comment(caption, media, commentend_post_id, driver=None):
    return comment_post(driver, caption, media, session["username"],session["id"], commentend_post_id)

@use_db_connection
@needs_authentication
def create_comment_answer(caption, media, answered_comment_id, driver=None):
    return answer_comment(driver, caption, media, session["username"],session["id"], answered_comment_id)

@use_db_connection
def get_comments_controller(entity_id,driver=None):
    return get_comments(driver,entity_id)

