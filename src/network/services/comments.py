from datetime import datetime

# Comments
def create_comment_node(driver, caption, media,userId):
    now = datetime.now()

    query = """
        CREATE (c:Comment {datetime: $now, caption: $caption, media: $media,userId: $userId}) 
        RETURN c as comment
    """
    params = {
        "now": now,
        "caption": caption,
        "media": media,
        "userId":userId
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
        return new_comment_id, True, None
    
    if commented_post_id:
        query = """
            MATCH (a: Comment {id:$new_comment_id})
            MATCH (p:Post {id:$commented_post_id})
            CREATE (p) -[:Has]-> (a)
        """

        params = {
            "new_comment_id": new_comment_id,
            "commented_post_id": commented_post_id
        }

        driver.execute_query(query, params)
        return new_comment_id, True, None

def answer_comment(driver, caption, media, username, answered_comment_id):
    return comment(driver, caption, media, username, answered_comment_id=answered_comment_id)

def comment_post(driver, caption, media, username, commented_post_id):
    return comment(driver, caption, media, username, commented_post_id=commented_post_id)

def get_comments(driver, target_id):
    """
    Obtiene todos los comentarios de un post o comentario.

    Este servicio verifica si el ID proporcionado pertenece a un post o un comentario.
    Luego, devuelve una lista de todos los comentarios y respuestas asociadas, 
    incluyendo metadatos como el ID del comentario, fecha de creación, texto del comentario, 
    medios adjuntos y el autor.

    Args:
        driver: Conexión al grafo de Neo4j.
        target_id (int): ID del post o comentario del que se quieren obtener los comentarios.

    Returns:
        tuple: 
            - comments (list): Lista de diccionarios con información de cada comentario.
            - success (bool): Indica si la operación fue exitosa.
            - error (str): Mensaje de error si la operación falló.

    Raises:
        Exception: Si ocurre un error durante la ejecución de la consulta.

    Notes:
        - Si el ID no pertenece a un post o comentario existente, devuelve un mensaje de error.
        - Los comentarios se ordenan por fecha de creación.
    """
    # Verificar si es un Post
    post_check = driver.execute_query(
        "MATCH (p:Post) WHERE id(p) = $target_id RETURN p",
        target_id=target_id
    )
    
    if post_check.records:
        query = """
            MATCH (p:Post) WHERE id(p) = $target_id
            MATCH (p)-[:Has*]->(c:Comment)
            MATCH (u:User)-[:Comments]->(c)
            RETURN id(c) AS id, c.datetime AS datetime, 
                   c.caption AS caption, c.media AS media, 
                   u.username AS username
            ORDER BY c.datetime
        """
    else:
        # Verificar si es un Comment
        comment_check = driver.execute_query(
            "MATCH (c:Comment) WHERE id(c) = $target_id RETURN c",
            target_id=target_id
        )
        
        if not comment_check.records:
            return None, False, "Post o comentario no encontrado"
        
        query = """
            MATCH (c1:Comment) WHERE id(c1) = $target_id
            MATCH (c1)-[:Has*1..]->(c:Comment)
            MATCH (u:User)-[:Comments]->(c)
            RETURN id(c) AS id, c.datetime AS datetime, 
                   c.caption AS caption, c.media AS media, 
                   u.username AS username
            ORDER BY c.datetime
        """
    
    try:
        result = driver.execute_query(query, target_id=target_id)
        comments = [
            {
                "id": record["id"],
                "datetime": record["datetime"].isoformat(),
                "caption": record["caption"],
                "media": record["media"],
                "userId": record["username"]
            } for record in result.records
        ]
        
        return comments, True, None
    
    except Exception as e:
        return None, False, str(e)
