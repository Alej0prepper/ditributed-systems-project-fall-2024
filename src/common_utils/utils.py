def convert_node_to_dict(node):
    """
    Convierte un nodo de Neo4j a un diccionario.
    
    :param node: Nodo de Neo4j.
    :return: Diccionario con las propiedades del nodo.
    """
    if node is None:
        return None
    
    data = {"id": node.id}
    data.update(node.items())  # Agrega las propiedades del nodo al diccionario
    return data

def get_post_by_id(driver, post_id):
    post = driver.execute_query(
        """
        MATCH (p:Post {id: $post_id})
        RETURN p
        """,
        {"post_id": post_id}
    ).records
    
    if not post:
        return None
    
    # Convertir el nodo a diccionario
    post_dict = convert_node_to_dict(post[0]["p"])
    
    return post_dict
