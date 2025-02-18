import os
import jwt
import datetime

SECRET_KEY = os.getenv('SECRET_KEY', '')
def generate_token(username, email):
    """
    Generates a JWT token for the logged-in user.
    """
    payload = {
        'id': id,
        'username': username,
        'email': email,
        'exp': datetime.datetime.now() + datetime.timedelta(hours=1)  # Token expires in 1 hour
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def validate_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        
        if datetime.datetime.now() > datetime.datetime.fromtimestamp(payload["exp"]):
            return None

        return payload

    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None