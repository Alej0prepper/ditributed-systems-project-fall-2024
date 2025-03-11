from datetime import datetime
import uuid
# Comments
def create_comment_node(driver, caption, media, user_id):
    now = datetime.now()

    query = """
        CREATE (c:Comment {datetime: $now, caption: $caption, media: $media,id:$id,userId: $userId }) 
        RETURN c 
    """
    comment_id = str(uuid.uuid4())
    params = {
        "now": now,
        "caption": caption,
        "media": media,
        "id": comment_id,
        "userId": user_id
    }

    driver.execute_query(query, params)
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

def get_comments(driver, entity_id):
    # Primero, verificamos si la entidad es un Post o un Comment
    query = """
        MATCH (e) WHERE e.id = $entity_id
        RETURN labels(e) AS labels
    """
    params = {"entity_id": entity_id}
    
    # Ejecutar la consulta para obtener el tipo de entidad
    result = driver.execute_query(query, params)
    
    # Si no se encuentran resultados, retornamos None
    if len(result.records) == 0:
        return None,False,"entity was'nt there"

    labels = result.records[0]["labels"]

    # Si la entidad tiene el label "Post", buscamos los comentarios asociados
    if "Post" in labels:
        query = """
            MATCH (p: Post {id: $entity_id})-[:Has]->(c: Comment)
            RETURN c.id AS comment_id, c.caption AS caption, c.media AS media, c.datetime AS datetime, c.userId AS user_id
        """
    # Si la entidad tiene el label "Comment", buscamos las respuestas a este comentario
    elif "Comment" in labels:
        query = """
            MATCH (c: Comment {id: $entity_id})<-[:Has]-(r: Comment)
            RETURN r.id AS comment_id, r.caption AS caption, r.media AS media, r.datetime AS datetime, r.userId AS user_id
        """
    else:
        return None,False," la entidad no es ni un Post ni un Comment"  # Si la entidad no es ni un Post ni un Comment, retornamos None

    # Ejecutar la consulta para obtener los comentarios
    params = {"entity_id": entity_id}
    records = driver.execute_query(query, params).records

    comments = []
    
    # Iterar sobre los registros obtenidos y armar el formato de salida
    for record in records:
        comment_data = {
            "caption": record["caption"],
            "media": record["media"],
            "datetime": record["datetime"]
        }

        # comments.append([record["comment_id"], record["user_id"], comment_data])
        # Asumiendo que comment_data es un diccionario
        comments.append({
            "id": record["comment_id"],
            "userId": record["user_id"],
            **comment_data  # Fusiona las claves y valores de comment_data con el diccionario principal
})


    return comments,True,None
