from datetime import datetime

def create_post_node(driver):
    post = driver.execute_query(
        """
        CREATE (p:Post)
        RETURN id(p) AS post_id
        """
    ).records[0]
    
    return post["post_id"]

def update_post(driver, post_id, media: list[str], caption: str, quoted_post_id: str = None):
    """
    Updates a Post node with the specified post_id in the Neo4j database.

    :param driver: Neo4j driver for executing queries.
    :param post_id: Unique identifier of the Post node to update.
    :param media: Updated list of media URLs for the Post.
    :param caption: Updated caption for the Post.
    :param quoted_post_id: Quoted post id.
    """
    if not quoted_post_id:
        query = """
            MATCH (p:Post)
                WHERE id(p) = $post_id
                SET p.media = $media,
                    p.caption = $caption
                RETURN p
        """
    else:
        query = """
            MATCH (p:Post)
                WHERE id(p) = $post_id
            MATCH (q:Post)
                WHERE id(q) = $quoted_post_id
            SET p.media = $media,
                p.caption = $caption
            CREATE (p) -[:Quotes]-> (q)
                RETURN p
        """

    parameters = {
        "post_id": post_id,
        "media": media if media else [],
        "caption": caption if caption else "",
        "quoted_post_id": quoted_post_id if quoted_post_id else ""
    }
    
    result = driver.execute_query(query, parameters)
    if result:
        print(f"Post with ID {post_id} updated successfully.")
    else:
        print(f"Post with ID {post_id} not found or update failed.")

def add_post(driver, media: list[str], caption: str):
    post_id = create_post_node(driver)

    update_post(
        driver, 
        post_id, 
        media=media if media else None, 
        caption=caption if caption else None, 
    )

    return post_id

def post(driver, media, caption, username):
    if not media and not caption:
        return None, False, "media and caption can't be None at the same time."    
    post_id = add_post(driver, media, caption)
    now = datetime.now()
    driver.execute_query(
        """
        MATCH (p:Post)
            WHERE id(p) = $post_id
        MATCH (u:User {username: $username})
        CREATE (u) -[r:Posts {datetime: $now}]->  (p)
        RETURN r
        """,
        {"post_id": post_id, "username": username, "now": now}
    )

    print("Posted!")
    return post_id, True, None

def quote(driver, media, caption, username, quoted_post_id):
    new_post_id, _, _ = post(driver, media, caption, username)
    update_post(driver, new_post_id, media, caption, quoted_post_id)
    return new_post_id

def repost(driver, reposted_post_id:int, username, media=None, caption=None):

    if get_post_by_id(driver, reposted_post_id) == None: return None, False, "Post not found."
    now = datetime.now()

    if media or caption:
        return quote(driver, media, caption, username, reposted_post_id), True, None

    driver.execute_query(
        """
        MATCH (p:Post)
            WHERE id(p) = $reposted_post_id
        MATCH (u:User {username: $username})
        CREATE (u) -[r:Reposts {datetime: $now}]->  (p)
        RETURN u, p
        """,
        {"reposted_post_id": reposted_post_id, "username": username, "now": now}
    )
    

    print(f"User {username} reposted post with ID: {reposted_post_id}")
    return reposted_post_id, True, None

def get_post_by_id(driver, post_id):
    post = driver.execute_query(
        """
        MATCH (p:Post)
            WHERE id(p) = $post_id
        RETURN p
        """,
        {"post_id": post_id}
    ).records

    return post[0] if post else None

def delete_post_service(driver, post_id, username):
    if get_post_by_id(driver, post_id) == None: return None, False, "Post not found."
      
    user_is_owner = len(driver.execute_query(
            """
            MATCH (n:Post)
                WHERE id(n) = $post_id
            MATCH (s:User {username: $username}) -[r:Posts]-> (n)  
            RETURN r
            """,
            {"post_id": post_id, "username": username}
    ).records) > 0

    if user_is_owner:
        driver.execute_query(
            """
            MATCH (n:Post)
                WHERE id(n) = $post_id
            MATCH (n) -[r]-> (s)
            DELETE r
            """,
            {"post_id": post_id}
        )
        driver.execute_query(
            """
            MATCH (n:Post)
                WHERE id(n) = $post_id
            MATCH (s) -[r]-> (n)
            DELETE r
            """,
            {"post_id": post_id}
        )
        driver.execute_query(
            """
            MATCH (p:Post)
                WHERE id(p) = $post_id
            DELETE p
            """,
            {"post_id": post_id}
        )
        return None, True, None
    return None, False, "Action not allowed, must be post's owner"