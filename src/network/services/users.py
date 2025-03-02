from datetime import datetime

def add_user(driver, _id, name, username, email, image_url, password, weight, styles, levels_by_style, birth_date, description):
    existing_user = driver.execute_query(
        "MATCH (u:User {username: $username}) RETURN u", {"username": username}
    ).records

    if len(existing_user) == 0:
        driver.execute_query(
            """
                CREATE (u:User {name: $name, id: $id, email: $email, image: $image, username: $username, password: $password, weight: $weight, styles: $styles, levels_by_style: $levels_by_style, birth_date: $birth_date, description: $description})
            """,
            {
                "name": name, 
                "id": _id, 
                "email": email, 
                "image": image_url, 
                "username": username, 
                "password": password, 
                "weight": weight, 
                "styles": styles, 
                "levels_by_style": levels_by_style, 
                "birth_date": birth_date,
                "description": description
            },
        )
        return driver.execute_query(
            "MATCH (u:User {username: $username}) RETURN id(u) as user_id", {"username": username}
        ).records[0]["user_id"], True, None
    else:
        return None, False, Exception("Username already exists.")
def get_user_by_email(driver, email):
    user = driver.execute_query(
        """
            Match (u:User {email: $email}) return u as User
        """,
        {"email": email},
    )
    return user.records[0]["User"]._properties if len(user.records)!=0 else None

def get_user_by_username_service(driver, username):
    user = driver.execute_query(
        """
            Match (u:User {username: $username}) return u as User
        """,
        {"username": username},
    )
    return user.records[0]["User"]._properties if len(user.records)!=0 else None

def get_user_by_id_service(driver, _id):
    user = driver.execute_query(
        """
            Match (u:User {id: $id}) return u as User
        """,
        {"id": _id},
    )
    return user.records[0]["User"]._properties if len(user.records)!=0 else None



def create_follow_relation(driver, entity_1, entity_2, type_entity_1=None, type_entity_2=None):
    # Primero, verifica si las entidades existen
    existing_entity_1 = driver.execute_query(
        """
        MATCH (e) 
        WHERE (e:User OR e:Gym) AND e.username = $entity_1 
        RETURN e LIMIT 1
        """,
        {"entity_1": entity_1}
    ).records

    existing_entity_2 = driver.execute_query(
        """
        MATCH (e) 
        WHERE (e:User OR e:Gym) AND e.username = $entity_2 
        RETURN e LIMIT 1
        """,
        {"entity_2": entity_2}
    ).records

    # Si no existen ninguna de las dos, lanza error
    if not existing_entity_1 and not existing_entity_2:
        return None, False, "Both entities not found."

    # Si existe una de las dos, crea la otra
    if existing_entity_1 and not existing_entity_2:
        # Asumiendo que type_entity_2 es 'User' o 'Gym'
        if type_entity_2 == 'User':
            driver.execute_query(
                "CREATE (e:User {username: $entity_2})",
                {"entity_2": entity_2}
            )
        elif type_entity_2 == 'Gym':
            # Para crear una gimnasio, necesitarías más datos, pero por simplicidad...
            driver.execute_query(
                "CREATE (e:Gym {username: $entity_2})",
                {"entity_2": entity_2}
            )
        existing_entity_2 = driver.execute_query(
            """
            MATCH (e) 
            WHERE (e:User OR e:Gym) AND e.username = $entity_2 
            RETURN e LIMIT 1
            """,
            {"entity_2": entity_2}
        ).records

    if existing_entity_2 and not existing_entity_1:
        # Asumiendo que type_entity_1 es 'User' o 'Gym'
        if type_entity_1 == 'User':
            driver.execute_query(
                "CREATE (e:User {username: $entity_1})",
                {"entity_1": entity_1}
            )
        elif type_entity_1 == 'Gym':
            # Para crear una gimnasio, necesitarías más datos, pero por simplicidad...
            driver.execute_query(
                "CREATE (e:Gym {username: $entity_1})",
                {"entity_1": entity_1}
            )
        existing_entity_1 = driver.execute_query(
            """
            MATCH (e) 
            WHERE (e:User OR e:Gym) AND e.username = $entity_1 
            RETURN e LIMIT 1
            """,
            {"entity_1": entity_1}
        ).records

    # Si ambas entidades existen, crea la relación
    if existing_entity_1 and existing_entity_2:
        now = datetime.now()
        driver.execute_query(
            """
            MATCH (e1) WHERE (e1:User OR e1:Gym) AND e1.username = $entity_1
            MATCH (e2) WHERE (e2:User OR e2:Gym) AND e2.username = $entity_2
            MERGE (e1)-[:Follows {start_datetime: $now}]->(e2)
            """,
            {"entity_1": entity_1, "entity_2": entity_2, "now": now}
        )
        return None, True, None
    else:
        return None, False, "Entity creation failed."

    

def remove_follow_relation(driver, entity_1, entity_2):
    existing_entity_1 = driver.execute_query(
        """
        MATCH (e) 
        WHERE (e:User OR e:Gym) AND e.username = $entity_1 
        RETURN e LIMIT 1
        """,
        {"entity_1": entity_1}
    ).records

    existing_entity_2 = driver.execute_query(
        """
        MATCH (e) 
        WHERE (e:User OR e:Gym) AND e.username = $entity_2 
        RETURN e LIMIT 1
        """,
        {"entity_2": entity_2}
    ).records

    if existing_entity_1 and existing_entity_2:
        relation_exists = len(driver.execute_query(
            """
            MATCH (e1)-[f:Follows]->(e2)
            WHERE (e1:User OR e1:Gym) AND e1.username = $entity_1
              AND (e2:User OR e2:Gym) AND e2.username = $entity_2
            RETURN f
            """,
            {"entity_1": entity_1, "entity_2": entity_2}
        ).records) > 0

        if relation_exists:
            driver.execute_query(
                """
                MATCH (e1)-[f:Follows]->(e2)
                WHERE (e1:User OR e1:Gym) AND e1.username = $entity_1
                  AND (e2:User OR e2:Gym) AND e2.username = $entity_2
                DELETE f
                """,
                {"entity_1": entity_1, "entity_2": entity_2}
            )
            return None, True, None
        return None, False, "Not following entity."
    else:
        return None, False, "Entity not found."

def update_user(driver, name, username, email, password, image_url, weight, styles, levels_by_style, birth_date, description):
    existing_user = driver.execute_query(
        "MATCH (u:User {username: $username}) RETURN u LIMIT 1", 
        {"username": username}
    ).records

    if existing_user:
        driver.execute_query(
            """
            MATCH (u:User {username: $username}) 
            SET u.name = $name, u.email = $email, u.password = $password, u.image = $image_url, 
                u.weight = $weight, u.styles = $styles, u.levels_by_style = $levels_by_style, 
                u.birth_date = $birth_date, u.description = $description
            """,
            {"name": name, "email": email, "username": username, "password": password, "image_url": image_url, 
             "weight": weight, "styles": styles, "levels_by_style": levels_by_style, "birth_date": birth_date,
             "description": description}
        )
        return username, True, None
    else:
        return None, False, "User not found."


def delete_user_service(driver, username):
    existing_user = driver.execute_query(
        "MATCH (u:User {username: $username}) RETURN u LIMIT 1",
        {"username": username}
    ).records

    if existing_user:
        driver.execute_query(
            """
            MATCH (u:User {username: $username}) -[r]-> (n)
            DELETE r
            """,
            {"username": username}
        )
        driver.execute_query(
            """
            MATCH (n) -[r]-> (u:User {username: $username})
            DELETE r
            """,
            {"username": username}
        )
        driver.execute_query(
            """
            MATCH (u:User {username: $username})
            DELETE u
            """,
            {"username": username}
        )
        return None, True, None
    else:
        return None, False, "User not found."

def get_users_by_search_term_service(users, query):
    try:
        if len(users) > 0:
            users = [user["u"]._properties for user in users]
            for user in users:
                del user["password"]
            return users,True,None
        else:
            return [],True,None 
    except Exception as e:
        return [],False,e

def get_all_users_service(driver, query):
    
    try:
        users = driver.execute_query(
            """
            MATCH (u:User)
            RETURN u
            """,
            {"query": query}
        ).records
        if len(users) > 0:
            users = [user["u"]._properties for user in users]
            for user in users:
                del user["password"]
            return users,True,None
        else:
            return [],True,None 
    except Exception as e:
        return [],False,e
