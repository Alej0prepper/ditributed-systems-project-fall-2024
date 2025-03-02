
def trains_in_service(driver, styles, username=None, gym_username=None):
    # Primero, verifica si el usuario y la gimnasio existen
    user_exists = driver.execute_query(
        "MATCH (u:User {username: $username}) RETURN u", 
        {"username": username} if username else {}
    ).records if username else []
    
    gym_exists = driver.execute_query(
        "MATCH (g:Gym {username: $gym_username}) RETURN g", 
        {"gym_username": gym_username} if gym_username else {}
    ).records if gym_username else []

    # Si no existe el usuario, crea un shadow de él
    if username and not user_exists:
        driver.execute_query(
            "CREATE (u:User {username: $username})",
            {"username": username}
        )
        user_exists = True  # Después de crearlo

    # Si no existe la gimnasio, crea un shadow
    if gym_username and not gym_exists:
        driver.execute_query(
            "CREATE (g:Gym {username: $gym_username})",
            {"gym_username": gym_username}
        )
        gym_exists = True  # Después de crearla

    if not user_exists or not gym_exists:
        return None, False, "User or Gym not found or creation failed"

    # Si ambos existen, crea la relación
    query = '''
    MATCH (u:User {username: $username})
    MATCH (g:Gym {username: $gym_username})
    MERGE (u) -[r:Trains_in]-> (g)
    SET r.styles = $styles
    RETURN r
    '''
    
    parameters = {
        "styles": styles,
        "username": username,
        "gym_username": gym_username
    }

    try:
        result = driver.execute_query(query, parameters)
        if result:
            return None, True, None
        else:
            return None, False, f"User {username} or Gym with username {gym_username} not found or update failed"
    except Exception as e:
        return None, False, str(e)


def remove_training_styles_service(driver,styles,username,gym_id):
    
    query = '''
    MATCH (u:User{username: $username})-[r:Trains_in]->(g:Gym)
        WHERE id(g) = $gym_id
    RETURN r.styles AS styles
    '''
    parameters = {
        "username" : username,
        "gym_id" : gym_id
    }
    result = driver.execute_query(query,parameters)
    if len(result.records) == 0:
        return None,False,f"User {username} or Gym with ID {gym_id} not found"
    styles = set(styles)
    current_styles = set(result.records[0]['styles'])
    styles_left = current_styles - styles
    if len(styles_left) == 0:
        #delete the relation
        query = '''
        MATCH (u:User{username: $username})-[r:Trains_in]->(g:Gym)
            WHERE id(g) = $gym_id
        DELETE r
        '''
        parameters = {
            "username" : username,
            "gym_id" : gym_id
        }
        return None,True,None
    else:
        #update the relation
        query = '''
        MATCH (u:User{username: $username})-[r:Trains_in]->(g:Gym)
            WHERE id(g) = $gym_id
        SET r.styles = $styles_left
        RETURN r
        '''
        parameters = {
            "username" : username,
            "gym_id" : gym_id,
            "styles_left" : list(styles_left)
        }
        result = driver.execute_query(query,parameters)
        if(result):
            return None,True,None
        else:
            return None,False,f"User {username} or Gym with ID {gym_id} not found or update failed"
    
def add_training_styles_service(driver,styles,username,gym_id):
    query = '''
    MATCH (u:User{username: $username})-[r:Trains_in]->(g:Gym)
        WHERE id(g) = $gym_id
    RETURN r.styles AS styles
    '''
    parameters = {
        "username" : username,
        "gym_id" : gym_id
    }
    result = driver.execute_query(query,parameters)
    if len(result.records) == 0:
        return None,False,f"User {username} or Gym with ID {gym_id} not found"
    current_styles = set(result.records[0]['styles'])
    styles = set(styles)
    styles_left = set(styles + current_styles)
    if len(styles_left) == 0:
        return None,True,None
    else:
        #update the relation
        query = '''
        MATCH (u:User{username: $username})-[r:Trains_in]->(g:Gym)
            WHERE id(g) = $gym_id
        SET r.styles = $styles_left
        RETURN r
        '''
        parameters = {
            "username" : username,
            "gym_id" : gym_id,
            "styles_left" : list(styles_left)
        }
        result = driver.execute_query(query,parameters)
        if(result):
            return None,True,None
        else:
            return None,False,f"User {username} or Gym with ID {gym_id} not found or update failed"
