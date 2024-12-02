import requests

BASE_URL = "http://10.0.11.3"

def register_user(name, username, email, password, weight, styles, levels_by_style):
    url = f"{BASE_URL}/register"
    data = {
        "name": name,
        "username": username,
        "email": email,
        "password": password,
        "weight": weight,
        "styles": styles,
        "levels_by_style": levels_by_style
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def update_user(email, name, password, weight, styles, levels_by_style):
    url = f"{BASE_URL}/update-user"
    data = {
        "email": email,
        "name": name,
        "password": password,
        "wheight": weight,
        "styles": styles,
        "levels_by_style": levels_by_style
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def delete_user():
    url = f"{BASE_URL}/delete-user"
    try:
        response = requests.post(url)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def login(username=None, email=None, password=None):
    url = f"{BASE_URL}/login"
    data = {
        "username": username,
        "email": email,
        "password": password
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def logout():
    url = f"{BASE_URL}/logout"
    try:
        response = requests.post(url)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def create_post(media, caption):
    url = f"{BASE_URL}/post"
    data = {
        "media": media,
        "caption": caption
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def repost(reposted_post_id):
    url = f"{BASE_URL}/repost"
    data = {"reposted_post_id": int(reposted_post_id)}
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def quote_post(quoted_post_id, media, caption):
    url = f"{BASE_URL}/quote"
    data = {
        "quoted_post_id": int(quoted_post_id),
        "media": media,
        "caption": caption
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def delete_post(post_id):
    url = f"{BASE_URL}/delete-post"
    data = {"post_id": int(post_id)}
    try:
        response = requests.delete(url, data=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def follow_user(followed_username):
    url = f"{BASE_URL}/follow"
    data = {"followed": followed_username}
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def unfollow_user(followed_username):
    url = f"{BASE_URL}/unfollow"
    data = {"followed": followed_username}
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def find_users(query):
    url = f"{BASE_URL}/find-users"
    data = {"query": query}
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def react_to_post(reaction, post_id):
    url = f"{BASE_URL}/react-post"
    data = {
        "reaction": reaction,
        "post_id": int(post_id)
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def react_to_comment(reaction, comment_id):
    url = f"{BASE_URL}/react-comment"
    data = {
        "reaction": reaction,
        "comment_id": int(comment_id)
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def comment_post(caption, media, post_id):
    url = f"{BASE_URL}/comment-post"
    data = {
        "caption": caption,
        "media": media,
        "post_id": int(post_id)
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def answer_comment(caption, media, comment_id):
    url = f"{BASE_URL}/answer-comment"
    data = {
        "caption": caption,
        "media": media,
        "comment_id": int(comment_id)
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def create_gym(name, username, email, location, address, password, styles, phone_number=None, ig_profile=None):
    url = f"{BASE_URL}/create-gym"
    data = {
        "name": name,
        "username": username,
        "email": email,
        "location": location,
        "address": address,
        "password": password,
        "styles": styles,
        "phone_number": phone_number,
        "ig_profile": ig_profile
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def login_gym(username=None, email=None, password=None):
    url = f"{BASE_URL}/gym-login"
    data = {
        "username": username,
        "email": email,
        "password": password
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def update_gym(name, email, location, address, styles, password, phone_number=None, ig_profile=None):
    url = f"{BASE_URL}/update-gym"
    data = {
        "name": name,
        "email": email,
        "location": location,
        "address": address,
        "styles": styles,
        "password": password,
        "phone_number": phone_number,
        "ig_profile": ig_profile
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def get_gym_info(gym_id):
    url = f"{BASE_URL}/get-gym-info"
    data = {"gym_id": int(gym_id)}
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def delete_gym():
    url = f"{BASE_URL}/delete-gym"
    try:
        response = requests.post(url)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def trains_in(gym_id, styles):
    url = f"{BASE_URL}/trains-in"
    data = {
        "gym_id": int(gym_id),
        "styles": styles
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def add_training_styles(styles, gym_id):
    url = f"{BASE_URL}/add-training-styles"
    data = {
        "styles": styles,
        "gym_id": int(gym_id)
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
