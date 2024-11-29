from datetime import datetime 

def create_gym_node(driver):
    gym = driver.execute_query(
        '''
        CREATE (g:Gym)
        RETURN id(g) AS gym_id
    ''').records[0]

    return gym['gym_id']

def update_gym(driver, name , username, email,location,address,styles,hashed_password, phone_number=None, ig_profile = None):

    phone = phone_number if(phone_number) else ""
    ig = ig_profile if(ig_profile) else ""
    query = '''
    MATCH (g:Gym)
        WHERE g.username = $username  
        SET g.name = $name,
            g.email = $email,
            g.location = $location,
            g.address = $address,
            g.styles = $styles,
            g.phone_number = $phone,
            g.password = $hashed_password,
            g.ig_profile = $ig

        RETURN g
    '''

    parameters = {
        "name" : name,
        "username" : username,
        "email" : email,
        "location": location,
        "address" : address,
        "styles" : styles,
        "password" : hashed_password,
        "phone" : phone,
        "ig" : ig
    }

    result = driver.execute_query(query,parameters)
    if(result):
        return username,True,None
    else:
        return username,False,f"Gym with username {username} not found or update failed"

def add_gym(driver,name,username, email,location,address,styles,hashed_password, phone_number=None, ig_profile = None):
        gym_id = create_gym_node(driver)

        return update_gym(
            driver,
            gym_id,
            name,
            username,
            email,
            location,
            address,
            styles,
            hashed_password,
            phone_number=phone_number if phone_number else None,
            ig_profile=ig_profile if ig_profile else None,
        )

def get_gym_info(driver,gym_id):
    
    query = """
    MATCH (g:Gym)
        WHERE id(g) = $gym_id
        RETURN g
    """
    
    result = driver.execute_query(
        query,
        {"gym_id": gym_id}
    )
    
    if result:
        gym_node_info = result[0][0][0]
        return dict(gym_node_info._properties),True,None  
    
    return None,False,f"Cannot find gym with ID {gym_id} "

def delete_gym(driver,username):

    
    query = """
    MATCH (g:Gym)
        WHERE g.username = $username
        RETURN g
    """
    result = driver.execute_query(
        query,
        {"username": username}
    )
    if result[0] == []:
        return username,False,f"Gym with username {username} not found"
    
    query = """
    MATCH (g:Gym)
        WHERE g.username = $username
        DELETE g
    """
    driver.execute_query(
        query,
        {"username": username}
    )

    query = """
    MATCH (g:Gym)
        WHERE g.username = $username
        RETURN g
    """
    result = driver.execute_query(
        query,
        {"username": username}
    )

    if result[0] == []:
        return None,True,None
    return None,False,f"Gym {username} could not be deleted succesfully"

def get_gym_by_email(driver, email):
    user = driver.execute_query(
        """
            Match (u:Gym {email: $email}) return u as gym
        """,
        {"email": email},
    )
    return user.records[0]["gym"]._properties if len(user.records)!=0 else None

def get_gym_by_username(driver, username):
    user = driver.execute_query(
        """
            Match (u:Gym {username: $username}) return u as gym
        """,
        {"username": username},
    )
    return user.records[0]["gym"]._properties if len(user.records)!=0 else None
