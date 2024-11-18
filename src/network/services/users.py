from datetime import datetime

def add_user(driver, name, username, email, password):
    existing_user = driver.execute_query(
        "MATCH (u:User {username: $username}) RETURN u", {"username": username}
    ).records

    if len(existing_user) == 0:
        driver.execute_query(
            """
                CREATE (u:User {name: $name, email: $email, username: $username, password: $password})
            """,
            {"name": name, "email": email, "username": username, "password": password},
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

def get_user_by_username(driver, username):
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