from datetime import datetime

# Comments
def create_comment_node(driver, caption, media):
    now = datetime.now()

    query = """
        CREATE (c:Comment {datetime: $now, caption: $caption, media: $media}) 
        RETURN id(c) as comment_id
    """
    params = {
        "now": now,
        "caption": caption,
        "media": media
    }

    comment_id = driver.execute_query(query, params).records[0]["comment_id"]
    return comment_id

def comment(driver, caption, media, username, answered_comment_id=None, commented_post_id=None):

    if answered_comment_id:
        query = """
            MATCH (c: Comment)
                WHERE id(c) = $answered_comment_id 
            RETURN c
        """
        params = {
            "answered_comment_id": answered_comment_id
        }

        if len(driver.execute_query(query, params).records) == 0:
            return None, False, "Comment not found."
    
    if commented_post_id:
        query = """
            MATCH (c: Post)
                WHERE id(c) = $commented_post_id 
            RETURN c
        """
        params = {
            "commented_post_id": commented_post_id
        }
        if len(driver.execute_query(query, params).records) == 0:
            return None, False, "Post not found."

    new_comment_id = create_comment_node(driver, caption, media)

    query = """
            MATCH (u:User {username: $username}) 
            MATCH (c:Comment)
                WHERE id(c) = $new_comment_id
            CREATE (u) -[:Comments]-> (c)
        """

    params = {
        "username": username,
        "new_comment_id": new_comment_id
    }

    driver.execute_query(query, params)
    
    if answered_comment_id:
        query = """
            MATCH (a: Comment)
                WHERE id(a) = $new_comment_id 
            MATCH (c:Comment)
                WHERE id(c) = $answered_comment_id
            CREATE (c) -[:Has]-> (a)
        """

        params = {
            "new_comment_id": new_comment_id,
            "answered_comment_id": answered_comment_id
        }

        driver.execute_query(query, params)
        print("Comment answered!")
        return new_comment_id, True, None
    
    if commented_post_id:
        query = """
            MATCH (a: Comment)
                WHERE id(a) = $new_comment_id 
            MATCH (p:Post)
                WHERE id(p) = $commented_post_id
            CREATE (p) -[:Has]-> (a)
        """

        params = {
            "new_comment_id": new_comment_id,
            "commented_post_id": commented_post_id
        }

        driver.execute_query(query, params)
        print("Post commented!")
        return new_comment_id, True, None

def answer_comment(driver, caption, media, username, answered_comment_id):
    return comment(driver, caption, media, username, answered_comment_id=answered_comment_id)

def comment_post(driver, caption, media, username, commented_post_id):
    return comment(driver, caption, media, username, commented_post_id=commented_post_id)
