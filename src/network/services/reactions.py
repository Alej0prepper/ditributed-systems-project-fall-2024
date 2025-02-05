def react(driver, reaction_type,username , reacted_comment_id = None, reacted_post_id = None) :
    if(reacted_comment_id):
        react_comment(driver,reaction_type,username,reacted_comment_id)
    elif(react_post):
        react_post(driver,reaction_type,username,reacted_post_id)
    else:
        raise Exception("ERROR: Reacted_comment_id and Reacted_post_id can't be None at the same time")


def reaction_exist(driver,username, reacted_comment_id=None, reacted_post_id = None):
    if(reacted_comment_id):
        query = """
                MATCH (u:User{username: $username})
                MATCH (c:Comment)
                    WHERE id(c) = $reacted_comment_id
                    MATCH (c) -[r:Reacted_by]-> (u)
                    RETURN r
            """
        params = {
                "username": username,
                "reacted_comment_id": reacted_comment_id
            }
        reaction_id = driver.execute_query(query,params)
        return reaction_id

    elif(reacted_post_id):
        query = """
                MATCH (u:User{username: $username})
                MATCH (p:Post)
                    WHERE id(p) = $reacted_post_id
                    MATCH (p) -[r:Reacted_by]-> (u)
                    RETURN r
            """
        params = {
                "username": username,
                "reacted_post_id": reacted_post_id
            }
        reaction_id = driver.execute_query(query,params)
        return reaction_id
    else:
        raise Exception("ERROR: Reacted_comment_id and Reacted_post_id can't be None at the same time")

def delete_reaction(driver, username, reacted_comment_id=  None, reacted_post_id = None):
    if(reacted_comment_id):
        query = """
                MATCH (u:User{username: $username})
                MATCH (c:Comment)
                    WHERE id(c) = $reacted_comment_id
                    MATCH (p) -[r:Reacted_by]-> (u)
                    DELETE r
            """
        params = {
                "username": username,
                "reacted_comment_id": reacted_comment_id
            }
        driver.execute_query(query,params)
    elif(reacted_post_id):
        query = """
                MATCH (u:User{username: $username})
                MATCH (p:Post)
                    WHERE id(p) = $reacted_post_id
                    MATCH (p) -[r:Reacted_by]-> (u)
                    DELETE r
                    
            """
        params = {
                "username": username,
                "reacted_post_id": reacted_post_id
            }
        driver.execute_query(query,params)
    else:
        raise Exception("ERROR: Reacted_comment_id and Reacted_post_id can't be None at the same time")     


def react_to_a_comment_service(driver, reaction_type,username , reacted_comment_id):
    query = """
        MATCH (c:Comment)
            WHERE id(c) = $reacted_comment_id
        RETURN c
    """
    params = {
        "reacted_comment_id": reacted_comment_id
    }
    if len(driver.execute_query(query,params).records) == 0:
        return None, False, "Comment not found"

    if(reaction_exist(driver,username,reacted_comment_id)):
        delete_reaction(driver,username,reacted_comment_id)
    query = """
        MATCH (u:User{username: $username})
        MATCH (c:Comment)
            WHERE id(c) = $reacted_comment_id
            CREATE (c) -[:Reacted_by {reaction_type: $reaction_type}]-> (u)
    """
    params = {
        "username": username,
        "reaction_type": reaction_type,
        "reacted_comment_id": reacted_comment_id
    }
    driver.execute_query(query,params)
    return None, True, None
    

def react_to_a_post_service(driver, reaction_type,username,reacted_post_id):
    query = """
        MATCH (p:Post)
            WHERE id(p) = $reacted_post_id
        RETURN p
    """
    params = {
        "reacted_post_id": reacted_post_id
    }
    if len(driver.execute_query(query,params).records) == 0:
        return None, False, "Post not found"
    
    if(reaction_exist(driver,username,None,reacted_post_id)):
        delete_reaction(driver,username,None,reacted_post_id)
    query = """
        MATCH (u:User{username: $username})
        MATCH (p:Post)
            WHERE id(p) = $reacted_post_id
            CREATE (p) -[:Reacted_by {reaction_type: $reaction_type}]-> (u)
    """
    params = {
        "username": username,
        "reaction_type": reaction_type,
        "reacted_post_id": reacted_post_id
    }
    driver.execute_query(query,params)
    return None, True, None