from flask import session, request
from network.middlewares.token import validate_token

def needs_authentication(func):
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        
        if token is None:
            return {"error": "Token is missing"}, 403

        token = token.split(" ")[1] if token.startswith("Bearer ") else token

        user_data = validate_token(token)
        if user_data is None:
            return {"error": "Invalid or expired token"}, 403

        session["username"] =  user_data["username"]
        session["email"] =  user_data["email"]
        
        return func(*args, **kwargs)
    return wrapper