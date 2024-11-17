from flask import session, jsonify 

def needs_authentication(func):
    def wrapper(*args, **kwargs):
        if not session.get("username"): 
            return None, False, "Acces denied, authentication is required."
        return func(*args, **kwargs)
    return wrapper