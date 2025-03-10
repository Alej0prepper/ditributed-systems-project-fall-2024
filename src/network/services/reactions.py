def react(driver, reaction_type,username , reacted_comment_id = None, reacted_post_id = None) :
    if(reacted_comment_id):
        react_comment(driver,reaction_type,username,reacted_comment_id)
    elif(react_post):
        react_post(driver,reaction_type,username,reacted_post_id)
    else:
        raise Exception("ERROR: Reacted_comment_id and Reacted_post_id can't be None at the same time")


def reaction_exist(driver,username, reacted_comment_id=None, reacted_post_id = None):
    if(reacted_comment_id):
        query = """
                MATCH (u:User{username: $username})
                MATCH (c:Comment)
                    WHERE id(c) = $reacted_comment_id
                    MATCH (c) -[r:Reacted_by]-> (u)
                    RETURN r
            """
        params = {
                "username": username,
                "reacted_comment_id": reacted_comment_id
            }
        reaction_id = driver.execute_query(query,params)
        return reaction_id

    elif(reacted_post_id):
        query = """
                MATCH (u:User{username: $username})
                MATCH (p:Post {id:$reacted_post_id})
                    MATCH (p) -[r:Reacted_by]-> (u)
                    RETURN r
            """
        params = {
                "username": username,
                "reacted_post_id": reacted_post_id
            }
        reaction_id = driver.execute_query(query,params)
        return reaction_id
    else:
        raise Exception("ERROR: Reacted_comment_id and Reacted_post_id can't be None at the same time")

def delete_reaction(driver, username, reacted_comment_id=  None, reacted_post_id = None):
    if(reacted_comment_id):
        query = """
                MATCH (u:User{username: $username})
                MATCH (c:Comment)
                    WHERE id(c) = $reacted_comment_id
                    MATCH (p) -[r:Reacted_by]-> (u)
                    DELETE r
            """
        params = {
                "username": username,
                "reacted_comment_id": reacted_comment_id
            }
        driver.execute_query(query,params)
    elif(reacted_post_id):
        query = """
                MATCH (u:User{username: $username})
                MATCH (p:Post {id:$reacted_post_id})
                    MATCH (p) -[r:Reacted_by]-> (u)
                    DELETE r
                    
            """
        params = {
                "username": username,
                "reacted_post_id": reacted_post_id
            }
        driver.execute_query(query,params)
    else:
        raise Exception("ERROR: Reacted_comment_id and Reacted_post_id can't be None at the same time")     


def react_to_a_comment_service(driver, reaction_type, username, reacted_comment_id):
    # Primero, verifica si el usuario y el comentario existen
    user_exists = driver.execute_query(
        "MATCH (u:User {username: $username}) RETURN u", 
        {"username": username}
    ).records

    comment_exists = driver.execute_query(
        "MATCH (c:Comment) WHERE id(c) = $reacted_comment_id RETURN c", 
        {"reacted_comment_id": reacted_comment_id}
    ).records
    if not user_exists and not comment_exists:
        return None,False,"Do not exists comment and user at the same time "
    # Si no existe el usuario, crea un shadow de él
    if not user_exists:
        driver.execute_query(
            "CREATE (u:User {username: $username})",
            {"username": username}
        )
        user_exists = True  # Después de crearlos

    # Si no existe el comentario, crea un shadow
    if not comment_exists:
        driver.execute_query(
            "CREATE (c:Comment {id: $reacted_comment_id})",
            {"reacted_comment_id": reacted_comment_id}
        )
        comment_exists = True  # Después de crearlo

    if not user_exists or not comment_exists:
        return None, False, "User or Comment not found or creation failed"

    # Si ya existe una reacción del mismo tipo, elimina la reacción existente
    if reaction_exist(driver, username, reacted_comment_id):
        delete_reaction(driver, username, reacted_comment_id)

    # Crea la nueva reacción
    query = """
        MATCH (u:User{username: $username})
        MATCH (c:Comment{id:$reacted_comment_id})
           
        CREATE (u) -[:Reacted_to {reaction_type: $reaction_type, id: $id}]-> (c)
    """
    params = {
        "username": username,
        "reaction_type": reaction_type,
        "reacted_comment_id": reacted_comment_id,
        "id": str(uuid.uuid4())
    }
    driver.execute_query(query, params)
    return None, True, None


def react_to_a_post_service(driver, reaction_type, username, reacted_post_id):
    # Primero, verifica si el usuario y el post existen
    user_exists = driver.execute_query(
        "MATCH (u:User {username: $username}) RETURN u", 
        {"username": username}
    ).records

    post_exists = driver.execute_query(
        "MATCH (p:Post {id:$reacted_post_id}) RETURN p", 
        {"reacted_post_id": reacted_post_id}
    ).records
    if not user_exists and not post_exists:
        return None,False,"Do not exists comment and post at the same time "
    # Si no existe el usuario, crea un shadow de él
    if not user_exists:
        driver.execute_query(
            "CREATE (u:User {username: $username})",
            {"username": username}
        )
        user_exists = True  # Después de crearlo

    # Si no existe el post, crea un shadow
    if not post_exists:
        driver.execute_query(
            "CREATE (p:Post {id: $reacted_post_id})",
            {"reacted_post_id": reacted_post_id}
        )
        post_exists = True  # Después de crearlo

    if not user_exists or not post_exists:
        return None, False, "User or Post not found or creation failed"

    # Si ya existe una reacción, elimina la reacción existente
    if reaction_exist(driver, username, None, reacted_post_id):
        delete_reaction(driver, username, None, reacted_post_id)

    # Crea la nueva reacción
    query = """
        MATCH (u:User{username: $username})
        MATCH (p:Post {id:$reacted_post_id})
        CREATE (p) -[:Reacted_by {reaction_type: $reaction_type,id: $id}]-> (u)
    """
    params = {
        "username": username,
        "reaction_type": reaction_type,
        "reacted_post_id": reacted_post_id,
        "id": str(uuid.uuid4())
    }
    driver.execute_query(query, params)
    return None, True, None
