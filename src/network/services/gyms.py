from datetime import datetime 

def create_gym_node(driver):
    gym = driver.execute_query(
        '''
        CREATE (g:Gym)
        RETURN id(g) AS gym_id
    ''').records[0]

    return gym['gym_id']
def update_gym(driver, gym_id, name , email,location,address,styles, phone_number=None, ig_profile = None):

    phone = phone_number if(phone_number) else ""
    ig = ig_profile if(ig_profile) else ""
    gym_id = int(gym_id)
    print(gym_id)
    print(type(gym_id))
    query = '''
    MATCH (g:Gym)
        WHERE id(g) = $gym_id  
        SET g.name = $name,
            g.email = $email,
            g.location = $location,
            g.address = $address,
            g.styles = $styles,
            g.phone_number = $phone,
            g.ig_profile = $ig

        RETURN g
    '''

    parameters = {
        "gym_id" : gym_id,
        "name" : name,
        "email" : email,
        "location": location,
        "address" : address,
        "styles" : styles,
        "phone" : phone,
        "ig" : ig

    }

    result = driver.execute_query(query,parameters)
    if(result):
        print(f"Gym with ID {gym_id} updated successfully")
        return gym_id,True,None
    else:
        print(f"Gym with ID {gym_id} not found or update failed")
        return gym_id,False,f"Gym with ID {gym_id} not found or update failed"

def add_gym(driver,name, email,location,address,styles, phone_number=None, ig_profile = None):
        gym_id = create_gym_node(driver)

        update_gym(
            driver,
            gym_id,
            name,
            email,
            location,
            address,
            styles,
            phone_number=phone_number if phone_number else None,
            ig_profile=ig_profile if ig_profile else None,
        )
        return gym_id

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
    print(gym_id)
    if result:
        gym_node_info = result[0][0][0]
        print(result)
        print(gym_node._properties)
        return dict(gym_node._properties),True,None  # Convierte el nodo en un diccionario de propiedades
    return None,False,f"cannot find gym with ID {gym_id} "

        
