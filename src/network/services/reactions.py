from datetime import datetime


def react(driver, reaction_type,username , reacted_comment_id = None, reacted_post_id = None) :
    if(reacted_comment_id):
        react_comment(driver,reaction_type,username,reacted_comment_id)
    elif(react_post):
        react_post(driver,reaction_type,username,reacted_post_id)
    else:
        raise Exception("ERROR: Reacted_comment_id and Reacted_post_id can't be None at the same time")



def react_comment(driver, reaction_type,username , reacted_comment_id):
        
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
        print("Comment reacted!!!")

def react_post(driver, reaction_type,username,reacted_post_id):
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
    print("Post reacted!!!")
