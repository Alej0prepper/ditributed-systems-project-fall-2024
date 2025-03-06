from datetime import datetime
import chord.protocol_logic as chord
import uuid

def create_post_node(driver):
    post_id = str(uuid.uuid4())

    driver.execute_query(
        """
        CREATE (p:Post {id: $post_id})
        """,
        {"post_id": post_id}
    ).records
    
    return post_id

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
            MATCH (p:Post{ id: $post_id })
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

def add_post(driver, media: list[str], caption: str):
    post_id = create_post_node(driver)

    update_post(
        driver, 
        post_id, 
        media=media if media else None, 
        caption=caption if caption else None, 
    )

    return post_id
def post(driver, media, caption, username, email):
    """
    Crea un nuevo post y establece la relación con la entidad correspondiente.
    
    :param driver: Conexión al grafo de Neo4j.
    :param media: Lista de URLs de medios.
    :param caption: Texto del post.
    :param username: Nombre de usuario de la entidad.
    :param email: Correo electrónico de la entidad.
    :return: ID del post, éxito de la operación y mensaje de error (si corresponde).
    """
    
    # Verificar parámetros obligatorios
    if not media and not caption:
        return None, False, "Media and caption can't be None at the same time."
    
    if not driver or not username or not email:
        return None, False, "All required parameters must be provided."

    # Obtener el tipo de entidad basado en el correo electrónico
    entity_type = None
    for et, em, _ in chord.system_entities_list:
        if em == email:
            entity_type = et
            break
    if entity_type is None:
        return None, False, "No entity type found for the provided email."

    try:
        # Verificar si la entidad existe en la base de datos
        query = f"""
            MATCH (e:{entity_type} {{email: $email}}) RETURN e
        """
        parameters = {"email": email}
        entity_exists = driver.execute_query(query, parameters).records

        # Si no existe la entidad, crearla
        if not entity_exists:
            query = f"""
                CREATE (e:{entity_type} {{email: $email, username: $username}})
            """
            parameters = {"email": email, "username": username}
            driver.execute_query(query, parameters)

        # Crear el post
        post_id = add_post(driver, media, caption)

        # Establecer la relación entre la entidad y el post
        now = datetime.now()
        query = f"""
            MATCH (p:Post {{id: $post_id}})
            MATCH (e:{entity_type} {{email: $email}})
            CREATE (e)-[r:Posts {{datetime: $now}}]->(p)
            RETURN r
        """
        parameters = {"post_id": post_id, "email": email, "now": now}

        with driver.session() as session:
            result = session.run(query, parameters)
            if result:
                return post_id, True, None
            else:
                return None, False, "There was a DB related error."
    except Exception as e:
        return None, False, str(e)


def quote(driver, media, caption, username, email, quoted_post_id):
    """
    Crea un nuevo post como cita y establece la relación con el post original.
    
    :param driver: Conexión al grafo de Neo4j.
    :param media: Lista de URLs de medios.
    :param caption: Texto del post.
    :param username: Nombre de usuario de la entidad.
    :param email: Correo electrónico de la entidad.
    :param quoted_post_id: ID del post citado.
    :return: ID del nuevo post.
    """
    new_post_id, _, _ = post(driver, None, media, caption, username, email)
    update_post(driver, new_post_id, media, caption, quoted_post_id)
    return new_post_id

def repost(driver, reposted_post_id: int, username, email, media=None, caption=None):
    """
    Crea un nuevo repost y establece la relación con el post original.
    
    :param driver: Conexión al grafo de Neo4j.
    :param reposted_post_id: ID del post que se va a repostear.
    :param username: Nombre de usuario de la entidad.
    :param email: Correo electrónico de la entidad.
    :param media: Lista de URLs de medios (opcional).
    :param caption: Texto del post (opcional).
    :return: ID del post reposteado, éxito de la operación y mensaje de error (si corresponde).
    """
    
    if get_post_by_id(driver, reposted_post_id) is None:
        return None, False, "Post not found."

    # Obtener el tipo de entidad basado en el correo electrónico
    entity_type = None
    for et, em, _ in chord.system_entities_list:
        if em == email:
            entity_type = et
            break
   
    if entity_type is None:
        return None, False, "No se encontró el tipo de entidad para el correo electrónico proporcionado."

    # Verificar si la entidad existe en la base de datos
    query = f"""
        MATCH (e:{entity_type} {{email: $email}}) RETURN e
    """
    parameters = {"email": email}
    entity_exists = driver.execute_query(query, parameters).records

    # Si no existe la entidad, crearla
    if not entity_exists:
        query = f"""
            CREATE (e:{entity_type} {{email: $email, username: $username}})
        """
        parameters = {"email": email, "username": username}
        driver.execute_query(query, parameters)

    # Si hay media o caption, crear un nuevo post como quote
    if media or caption:
        return quote(driver, media, caption, username, email, reposted_post_id), True, None

    # Crear el repost
    now = datetime.now()
    query = f"""
        MATCH (p:Post)
            WHERE id(p) = $reposted_post_id
        MATCH (e:{entity_type} {{email: $email}})
        CREATE (e)-[r:Reposts {{datetime: $now}}]->(p)
        RETURN e, p
    """
    parameters = {"reposted_post_id": reposted_post_id, "email": email, "now": now}

    with driver.session() as session:
        session.run(query, parameters)

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