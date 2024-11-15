from datetime import datetime

# Reactions

def create_reaction_node(driver, reaction_id):
    now = datetime.now()

    query = """
        CREATE (r:Reaction {datetime: $now, reaction_id: $reaction_id })
        RETURN id(r) as reaction_id
    """
    params = {
        "now": now ,
        "reaction_id" : reaction_id
    }


def react(driver, reaction_id, comment_id, post_id):
    pass

def react_comment(driver, reaction_id, comment_id):
    pass