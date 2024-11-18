from flask import session
from network.middlewares.use_db_connection import use_db_connection
from network.middlewares.auth import needs_authentication
from network.services.comments import comment_post
from network.services.comments import answer_comment

@use_db_connection
@needs_authentication
def create_post_comment(caption, media, commentend_post_id, driver=None):
    return comment_post(driver, caption, media, session["username"], commentend_post_id)

@use_db_connection
@needs_authentication
def create_comment_answer(caption, media, answered_comment_id, driver=None):
    return answer_comment(driver, caption, media, session["username"], answered_comment_id)