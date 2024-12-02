import requests
from dotenv import load_dotenv
import os

load_dotenv()
BASE_URL = os.getenv('SERVER_URL')

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

def update_user(email, name, password, weight, styles, levels_by_style, token):
    url = f"{BASE_URL}/update-user"
    headers = {"Authorization": token}
    data = {
        "email": email,
        "name": name,
        "password": password,
        "weight": weight,
        "styles": styles,
        "levels_by_style": levels_by_style
    }
    try:
        response = requests.put(url, headers=headers, data=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def delete_user(token):
    url = f"{BASE_URL}/delete-user"
    headers = {"Authorization": token}
    try:
        response = requests.post(url, headers=headers)
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
        token = response.json().get('token')
        return response, token
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None, None

def logout(token):
    url = f"{BASE_URL}/logout"
    headers = {"Authorization": token}
    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def create_post(media, caption, token):
    url = f"{BASE_URL}/post"
    headers = {"Authorization": token}
    data = {
        "media": media,
        "caption": caption
    }
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def repost(reposted_post_id, token):
    url = f"{BASE_URL}/repost"
    headers = {"Authorization": token}
    data = {"reposted_post_id": int(reposted_post_id)}
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def quote_post(quoted_post_id, media, caption, token):
    url = f"{BASE_URL}/quote"
    headers = {"Authorization": token}
    data = {
        "quoted_post_id": int(quoted_post_id),
        "media": media,
        "caption": caption
    }
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def delete_post(post_id, token):
    url = f"{BASE_URL}/delete-post"
    headers = {"Authorization": token}
    data = {"post_id": int(post_id)}
    try:
        response = requests.delete(url, headers=headers, data=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def follow_user(followed_username, token):
    url = f"{BASE_URL}/follow"
    headers = {"Authorization": token}
    data = {"followed": followed_username}
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def unfollow_user(followed_username, token):
    url = f"{BASE_URL}/unfollow"
    headers = {"Authorization": token}
    data = {"followed": followed_username}
    try:
        response = requests.post(url, headers=headers, data=data)
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

def react_to_post(reaction, post_id, token):
    url = f"{BASE_URL}/react-post"
    headers = {"Authorization": token}
    data = {
        "reaction": reaction,
        "post_id": int(post_id)
    }
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def react_to_comment(reaction, comment_id, token):
    url = f"{BASE_URL}/react-comment"
    headers = {"Authorization": token}
    data = {
        "reaction": reaction,
        "comment_id": int(comment_id)
    }
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def comment_post(caption, media, post_id, token):
    url = f"{BASE_URL}/comment-post"
    headers = {"Authorization": token}
    data = {
        "caption": caption,
        "media": media,
        "post_id": int(post_id)
    }
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def answer_comment(caption, media, comment_id, token):
    url = f"{BASE_URL}/answer-comment"
    headers = {"Authorization": token}
    data = {
        "caption": caption,
        "media": media,
        "comment_id": int(comment_id)
    }
    try:
        response = requests.post(url, headers=headers, data=data)
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

def trains_in(gym_id, styles, token=None):
    url = f"{BASE_URL}/trains-in"
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    data = {
        "gym_id": int(gym_id),
        "styles": styles
    }
    try:
        response = requests.post(url, data=data, headers=headers)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def add_training_styles(styles, gym_id, token=None):
    url = f"{BASE_URL}/add-training-styles"
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    data = {
        "styles": styles,
        "gym_id": int(gym_id)
    }
    try:
        response = requests.post(url, data=data, headers=headers)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
