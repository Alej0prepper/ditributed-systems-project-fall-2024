from network.middlewares.auth import needs_authentication
from network.controllers.utils import use_db_connection
from flask import session
from network.services.posts import post, repost

@use_db_connection
@needs_authentication
def create_post(media, caption, driver=None):
    return post(driver, media, caption, session["username"])

@use_db_connection
@needs_authentication
def repost_existing_post(reposted_post_id:int, driver=None):
    return repost(driver, reposted_post_id, session["username"])

@use_db_connection
@needs_authentication
def quote_existing_post(reposted_post_id:id, media, caption, driver=None):
    return repost(driver, reposted_post_id, session["username"], media, caption)