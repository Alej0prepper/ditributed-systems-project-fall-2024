from datetime import datetime 
from database.connection import driver
def create_gym_node(driver, username):
    """
    Creates a new Gym node in the Neo4j database if it doesn't exist, otherwise returns the existing node's ID.

    Args:
        driver: neo4j.Driver
            The Neo4j database driver connection
        username (str):
            The username to identify the gym node

    Returns:
        int: The ID of the newly created gym node
        OR
        tuple: (existing_gym_id, False, error_message) if the gym already exists

    Raises:
        IndexError: If no records are returned from the initial query
        neo4j.exceptions.Neo4jError: If database operations fail

    Note:
        This function performs two separate Cypher queries:
        1. First checks if a gym with the given username exists
        2. If not found, creates a new gym node with the provided username
    """
        
    existing_gym = driver.execute_query("MATCH (g:gym {username: $username}) RETURN id(g) AS gym_id",{"username": username}).records[0]
    if len(existing_gym) == 0:
            
        gym = driver.execute_query(
            '''
            CREATE (g:Gym {username: $username})
            RETURN id(g) AS gym_id
        ''', {'username': username}).records[0]

        return gym['gym_id']
    else:
        return existing_gym['gym_id'], False, f"Gym with username:{username} already exists."
    
def update_gym(driver, name , username, email, description, location,image_url,styles,hashed_password, phone_number=None, ig_profile = None):
    """
    Updates an existing gym's details in the Neo4j database.

    Args:
        driver (neo4j.Driver): The Neo4j database driver connection
        name (str): The updated name of the gym
        username (str): The unique identifier for the gym
        email (str): The gym's contact email
        description (str): Detailed description of the gym
        location (dict): Dictionary containing latitude and longitude coordinates
        image_url (str): URL pointing to the gym's image
        styles (list): List of martial arts/styles offered by the gym
        hashed_password (str): Hashed password for security
        phone_number (str, optional): Contact phone number. Defaults to empty string.
        ig_profile (str, optional): Instagram profile link. Defaults to empty string.

    Returns:
        tuple: Contains three elements:
            - Updated gym record (or username if update fails)
            - Boolean indicating success/failure
            - Error message (None if successful)

    Raises:
        neo4j.exceptions.Neo4jError: If database operations fail
        KeyError: If location dictionary doesn't contain 'lat' or 'lng'

    Note:
        This function performs a single Cypher query that:
        1. Locates the gym node by username
        2. Updates multiple properties simultaneously
        3. Returns the updated node record
    """

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
        return result,True,None
    else:
        return username,False,f"Gym with username {username} not found or update failed"

def add_gym(driver,name,username, email,description,image_url,location,styles,hashed_password, phone_number=None, ig_profile = None):
        create_gym_node(driver, username)

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

def get_gyms_by_search_term_service(driver, query):
    try:
        gyms = driver.execute_query(
            """
            MATCH (u:Gym)
            WHERE toLower(u.username) CONTAINS toLower($query) 
            OR toLower(u.name) CONTAINS toLower($query)
            RETURN u
            """,
            {"query": query}
        ).records
        if len(gyms) > 0:
            gyms = [gym["u"]._properties for gym in gyms]
            for gym in gyms:
                del gym["password"]
            return gyms,True,None
        else:
            return [],True,None 
    except Exception as e:
        return [],False,e

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
