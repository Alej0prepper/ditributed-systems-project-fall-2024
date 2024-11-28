
def trains_in_service(driver,styles,username,gym_id):
    query = '''
    MATCH (u:User{username: $username})
    MATCH (g:Gym)
        WHERE id(g) = $gym_id
        CREATE (u) -[r:Trains_in]-> (g)
        SET r.styles = $styles
    RETURN r
    '''

    parameters = {
        "styles" : styles,
        "username" : username,
        "gym_id" : gym_id
    }

    result = driver.execute_query(query,parameters)
    if(result):
        return None,True,None
    else:
        return None,False,f"User {username} or Gym with ID {gym_id} not found or update failed"

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
