from datetime import datetime
import uuid
# Comments
def create_comment_node(driver, caption, media, user_id):
    now = datetime.now()

    query = """
        CREATE (c:Comment {datetime: $now, caption: $caption, media: $media,id:$id,userId: $userId }) 
        RETURN c 
    """
    params = {
        "now": now,
        "caption": caption,
        "media": media,
        "id": str(uuid.uuid4()),
        "userId": user_id
    }

    comment_id = driver.execute_query(query, params).records[0]["id"]
    return comment_id

def comment(driver, caption, media, username,user_id, answered_comment_id=None, commented_post_id=None):

    if answered_comment_id:
        query = """
            MATCH (c: Comment {id: $answered_comment_id})
            RETURN c
        """
        params = {
            "answered_comment_id": answered_comment_id
        }

        if len(driver.execute_query(query, params).records) == 0:
            return None, False, "Comment not found."
    
    if commented_post_id:
        query = """
            MATCH (c: Post {id: $commented_post_id })
            RETURN c
        """
        params = {
            "commented_post_id": commented_post_id
        }
        if len(driver.execute_query(query, params).records) == 0:
            return None, False, "Post not found."

    new_comment_id = create_comment_node(driver, caption, media,user_id)

    query = """
            MATCH (u:User {username: $username}) 
            MATCH (c:Comment {id:})
            CREATE (u) -[:Comments{id:$comment_relation_id}]-> (c)
        """

    params = {
        "username": username,
        "new_comment_id": new_comment_id,
        "comment_relation_id": str(uuid.uuid4())
    }

    driver.execute_query(query, params)
    
    if answered_comment_id:
        query = """
            MATCH (a: Comment)
                WHERE id(a) = $new_comment_id 
            MATCH (c:Comment)
                WHERE id(c) = $answered_comment_id
            CREATE (c) -[:Has{id:$has_id}]-> (a)
        """

        params = {
            "new_comment_id": new_comment_id,
            "answered_comment_id": answered_comment_id,
            "has_id": str(uuid.uuid4())
        }

        driver.execute_query(query, params)
        return new_comment_id, True, None
    
    if commented_post_id:
        query = """
            MATCH (a: Comment {id:$new_comment_id})
            MATCH (p:Post {id:$commented_post_id})
            CREATE (p) -[:Has{id:$has_id}]-> (a)
        """

        params = {
            "new_comment_id": new_comment_id,
            "commented_post_id": commented_post_id,
            "has_id": str(uuid.uuid4())
        }

        driver.execute_query(query, params)
        return new_comment_id, True, None

def answer_comment(driver, caption, media, username,user_id, answered_comment_id):
    return comment(driver, caption, media, username,user_id, answered_comment_id=answered_comment_id)

def comment_post(driver, caption, media, username,user_id, commented_post_id):
    return comment(driver, caption, media, username,user_id, commented_post_id=commented_post_id)
