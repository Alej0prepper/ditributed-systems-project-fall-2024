from datetime import datetime

def add_user(driver, name, username, email, password,wheigth,styles,levels_by_style):
    existing_user = driver.execute_query(
        "MATCH (u:User {username: $username}) RETURN u", {"username": username}
    ).records

    if len(existing_user) == 0:
        driver.execute_query(
            """
                CREATE (u:User {name: $name, email: $email, username: $username, password: $password, wheigth: $wheigth, styles: $styles, levels_by_style: $levels_by_style})
            """,
            {"name": name, "email": email, "username": username, "password": password, "wheigth": wheigth, "styles": styles, "levels_by_style": levels_by_style},
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

def create_follow_relation(driver, user_1, user_2):
    existing_user_1 = driver.execute_query(
        "MATCH (u:User {username: $user_1}) RETURN u LIMIT 1", {"user_1": user_1}
    ).records

    existing_user_2 = driver.execute_query(
        "MATCH (u:User {username: $user_2}) RETURN u LIMIT 1", {"user_2": user_2}
    ).records

    if existing_user_1 and existing_user_2:
        now = datetime.now()
        driver.execute_query(
            """
            MERGE (u1:User {username: $user_1})
            MERGE (u2:User {username: $user_2})
            CREATE (u1) - [:Follows {start_datetime: $now}] -> (u2)
            """, 
        {"user_1": user_1, "user_2": user_2, "now": now})
        return None, True, None
    else:
        return None, False, "User not found."

def remove_follow_relation(driver, user_1, user_2):
    existing_user_1 = driver.execute_query(
        "MATCH (u:User {username: $user_1}) RETURN u LIMIT 1", {"user_1": user_1}
    ).records

    existing_user_2 = driver.execute_query(
        "MATCH (u:User {username: $user_2}) RETURN u LIMIT 1", {"user_2": user_2}
    ).records

    if existing_user_1 and existing_user_2:
        now = datetime.now()
        relation_exists = len(driver.execute_query(
            """
            MATCH (u1:User {username: $user_1})
            MATCH (u2:User {username: $user_2})
            MATCH (u1) - [f:Follows] -> (u2)
            RETURN f
            """, 
        {"user_1": user_1, "user_2": user_2, "now": now}).records) > 0
        if relation_exists:
            driver.execute_query(
                """
                MATCH (u1:User {username: $user_1})
                MATCH (u2:User {username: $user_2})
                MATCH (u1) - [f:Follows] -> (u2)
                DELETE f
                """, 
            {"user_1": user_1, "user_2": user_2, "now": now})
            return None, True, None
        return None, False, "Not following user."
    else:
        return None, False, "User not found."

def update_user(driver, name, username, email, password, wheight,styles,levels_by_style):
    existing_user = driver.execute_query(
        "MATCH (u:User {username: $username}) RETURN u LIMIT 1", 
        {"username": username}
    ).records

    if existing_user:
        driver.execute_query(
            """
            MATCH (u:User {username: $username}) 
            SET u.name = $name, u.email = $email, u.password = $password, 
                u.wheight = $wheight, u.styles = $styles, u.levels_by_style = $levels_by_style
            """,
            {"name": name, "email": email, "username": username, "password": password, 
             "wheight": wheight, "styles": styles, "levels_by_style": levels_by_style}
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

def get_users_by_search_term_service(driver, query):
    
    try:
        users = driver.execute_query(
            """
            MATCH (u:User)
            WHERE toLower(u.username) CONTAINS toLower($query) 
            OR toLower(u.name) CONTAINS toLower($query)
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
