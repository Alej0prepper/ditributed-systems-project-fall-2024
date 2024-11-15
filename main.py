from src.database.connection import open_db_connection, close_db_connection
from src.network.services.users import add_user, create_follow_relation
from src.network.services.posts import post, repost
from src.network.services.comments import comment_post, answer_comment

# Open connection
session, driver = open_db_connection()

# test users
user_name_ale = add_user(driver,"Alejandro Alvarez", "Alej0", "alej0@gmail.com", "hashed_passw")
user_name_frank = add_user(driver,"Frank Perez", "frankperez24", "frank@gmail.com", "hashed_passw")
create_follow_relation(driver, user_name_ale, user_name_frank)
create_follow_relation(driver, user_name_frank, user_name_ale)

# test posts
post_id = post(driver, ["img1"], "My caption", user_name_ale)
repost(driver, post_id, user_name_frank)

# test comments
comment_id = comment_post(driver, "Hellooooo!", [], user_name_frank, post_id)
answer_comment(driver, "Hello 2 u 2", [], user_name_ale, comment_id)

# Close connection
close_db_connection()