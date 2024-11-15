from datetime import datetime


# Posts and reposts
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
                SET p.media = $media,
                    p.caption = $caption
            MATCH (q:Post)
                WHERE id(q) = $quoted_post_id
            CREATE (p) -[:Quotes]-> (q:Post)
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
        return Exception("Error: media and caption can't be None at the same time.")    
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
    return post_id

def quote(driver, media, caption, quoted_post_id):
    new_post_id = create_post_node(driver)
    update_post(driver, new_post_id, media, caption, quoted_post_id)
    return new_post_id

def repost(driver, quoted_post_id, username, media=None, caption=None):
    now = datetime.now()

    if media or caption:
        return quote(driver, media, caption, quoted_post_id)

    driver.execute_query(
        """
        MATCH (p:Post)
            WHERE id(p) = $quoted_post_id
        MATCH (u:User {username: $username})
        CREATE (u) -[r:Reposts {datetime: $now}]->  (p)
        RETURN r
        """,
        {"quoted_post_id": quoted_post_id, "username": username, "now": now}
    )

    print("Reposted!")
    return quoted_post_id
