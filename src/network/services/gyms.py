from datetime import datetime 
from database.connection import driver
def create_gym_node(driver, id, username):
    gym = driver.execute_query(
        '''
        CREATE (g:Gym {username: $username, id: $id})
        RETURN g AS gym
    ''', {'username': username, 'id': id}).records[0]

    return gym['gym']

def update_gym(driver, name , username, email, description, location,image_url,styles,hashed_password, phone_number=None, ig_profile = None):

    phone = phone_number if(phone_number) else ""
    ig = ig_profile if(ig_profile) else ""
    query = '''
    MATCH (g:Gym)
        WHERE g.username = $username  
        SET g.name = $name,
            g.email = $email,
            g.description = $description,
            g.image = $image_url,
            g.lat = $lat,
            g.lng = $lng,
            g.styles = $styles,
            g.phone_number = $phone,
            g.password = $password,
            g.ig_profile = $ig

        RETURN g
    '''
    parameters = {
        "name" : name,
        "username" : username,
        "email" : email,
        "description": description,
        "image_url": image_url,
        "lat": location["lat"],
        "lng": location["lng"],
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

def add_gym(driver, id, name,username, email,description,image_url,location,styles,hashed_password, phone_number=None, ig_profile = None):
        create_gym_node(driver, id, username)

        return update_gym(
            driver,
            name,
            username,
            email,
            description,
            location,
            image_url,
            styles,
            hashed_password,
            phone_number if phone_number else None,
            ig_profile if ig_profile else None,
        )


def get_gym_by_id_service(driver,id):
    
    query = """
    MATCH (g:Gym {id: $id})
        RETURN g
    """
    
    result = driver.execute_query(
        query,
        {"id": id}
    )
    
    if result:
        gym_node_info = result[0][0][0]
        del gym_node_info._properties["password"]
        return dict(gym_node_info._properties),True,None  
    
    return None,False,f"Cannot find gym with ID {id} "

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

def get_gyms_by_search_term_service(gyms, query):
    try:
        if len(gyms) > 0:
            gyms = [gym for gym in gyms if query.lower() in gym["name"].lower() or query.lower() in gym["username"].lower()]
            return gyms,True,None
        else:
            return [],True,None 
    except Exception as e:
        return [],False,str(e)

def get_all_gyms_service(driver):
    try:
        gyms = driver.execute_query(
            """
            MATCH (u:Gym)
            RETURN ID(u) AS id, u
            """,
        ).records

        if gyms:
            gyms = [
                {
                    "id": gym["id"],  # Include Neo4j ID
                    **{k: v for k, v in gym["u"]._properties.items() if k != "password"}  # Remove password
                }
                for gym in gyms
            ]
            return gyms, True, None
        else:
            return [], True, None 

    except Exception as e:
        return [], False, e
