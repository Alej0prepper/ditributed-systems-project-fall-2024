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
                MATCH (u {username: $username})
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
                MATCH (u{username: $username})
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
        MATCH (c:Comment)
            WHERE id(c) = $reacted_comment_id
        CREATE (u) -[:Reacted_to {reaction_type: $reaction_type}]-> (c)
    """
    params = {
        "username": username,
        "reaction_type": reaction_type,
        "reacted_comment_id": reacted_comment_id
    }
    driver.execute_query(query, params)
    return None, True, None


def react_to_a_post_service(driver, reaction_type, username, entity_type, reacted_post_id):
    """
    Handles reactions to a post from both Users and Gyms.
    
    :param driver: Neo4j driver connection
    :param reaction_type: Type of reaction (e.g., 'like', 'share')
    :param username: Username of reacting entity (User/Gym)
    :param entity_type: Type of entity ('User' or 'Gym')
    :param reacted_post_id: ID of the post being reacted to
    :return: Tuple (None, success, error)
    """
    try:
        # Verify entity type validity
        if entity_type not in ["User", "Gym"]:
            return None, False, "Invalid entity type. Must be 'User' or 'Gym'"

        # Check if reacting entity exists
        entity_exists = driver.execute_query(
            f"MATCH (e:{entity_type} {{username: $username}}) RETURN e",
            {"username": username}
        ).records

        # Check if post exists
        post_exists = driver.execute_query(
            "MATCH (p:Post {id: $reacted_post_id}) RETURN p",
            {"reacted_post_id": reacted_post_id}
        ).records

        # Create shadow entity if needed
        if not entity_exists:
            driver.execute_query(
                f"CREATE (e:{entity_type} {{username: $username}})",
                {"username": username}
            )

        # Create shadow post if needed
        if not post_exists:
            driver.execute_query(
                "CREATE (p:Post {id: $reacted_post_id})",
                {"reacted_post_id": reacted_post_id}
            )

        # Check and delete existing reaction
        existing_reaction = driver.execute_query(
            f"""
            MATCH (p:Post {{id: $reacted_post_id}})
            MATCH (p)-[r:Reacted_by]->(e:{entity_type} {{username: $username}})
            RETURN r
            """,
            {"reacted_post_id": reacted_post_id, "username": username}
        ).records

        if existing_reaction:
            driver.execute_query(
                f"""
                MATCH (p:Post)
                WHERE id(p) = $reacted_post_id
                MATCH (p)-[r:Reacted_by]->(e:{entity_type} {{username: $username}})
                DELETE r
                """,
                {"reacted_post_id": reacted_post_id, "username": username}
            )

        # Create new reaction
        driver.execute_query(
            f"""
            MATCH (e:{entity_type} {{username: $username}})
            MATCH (p:Post)
            WHERE id(p) = $reacted_post_id
            CREATE (p)-[:Reacted_by {{reaction_type: $reaction_type}}]->(e)
            """,
            {
                "username": username,
                "reaction_type": reaction_type,
                "reacted_post_id": reacted_post_id
            }
        )

        return None, True, None

    except Exception as e:
        return None, False, str(e)



def get_reactions_service(driver, target_id):
    """
    Retrieves all reactions of a post or comment.

    :param driver: Connection to the graph.
    :param target_id: ID of the post or comment.
    :return: List of reactions.
    """
    # Primero, verifica si el target_id corresponde a un post o un comentario
    post_exists = driver.execute_query(
        "MATCH (p:Post) WHERE id(p) = $target_id RETURN p",
        {"target_id": target_id}
    ).records

    comment_exists = driver.execute_query(
        "MATCH (c:Comment) WHERE id(c) = $target_id RETURN c",
        {"target_id": target_id}
    ).records

    if post_exists:
        query = """
            MATCH (p:Post) -[r:Reacted_by]-> (u:User) 
            WHERE id(p) = $target_id
            RETURN u.username, r.reaction_type
        """
    elif comment_exists:
        query = """
            MATCH (c:Comment) -[r:Reacted_by]-> (u:User) 
            WHERE id(c) = $target_id
            RETURN u.username, r.reaction_type
        """
    else:
        return []  # No existe ni post ni comentario con ese ID

    params = {"target_id": target_id}
    results = driver.execute_query(query, params)
    reactions = []
    for record in results.records:
        reaction = {
            "username": record["u.username"],
            "reaction_type": record["r.reaction_type"]
        }
        reactions.append(reaction)

    return reactions
